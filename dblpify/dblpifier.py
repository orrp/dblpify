import logging
from pathlib import Path

from tqdm import tqdm

from dblpify.dblp_requester import DblpRequester
from dblpify.matcher import top_hit

from dblpify import cache_path, dblpified_bib_filename, formatted_bib_filename, report_filename
from dblpify.bib_db import BibDB, EntryStatus


class Dblpifier:
    """Main class for the dblpify app. Takes a BibTeX file and updates the entries with dblp information."""

    def __init__(self, args, logger):
        self.bib_path = Path(args.bib_path)
        output_path = Path(args.out_path)
        self.mkdir(output_path)
        self.dblpified_bib_path = output_path / dblpified_bib_filename(self.bib_path)
        self.save_formatted = args.save_formatted
        self.formatted_bib_path = output_path / formatted_bib_filename(self.bib_path)
        self.report_path = output_path / report_filename(self.bib_path)

        self.cache_path = cache_path(self.bib_path)
        self.mkdir(self.cache_path.parent)
        if args.clear_cache:
            logging.info(f"Clearing cache at {self.cache_path}")
            self.cache_path.unlink(missing_ok=True)

        self.dev_mode = args.dev

        self.num_hits = args.num_hits
        self.logger = logger

        self.bib_db = None
        self.init_bib_db()  # initialize self.bib_db

        self.requester = DblpRequester(self.logger, self.cache_path)

    @staticmethod
    def mkdir(path: Path):
        if not path.exists():
            logging.info(f"Creating directory at {path}")
            path.mkdir(exist_ok=True, parents=True)

    def init_bib_db(self):
        """Reads the BibTeX file and initializes the BibDB. This method should be called only once."""
        assert self.bib_db is None, "Bib DB already initialized"
        # Read BibTeX file
        logging.info(f"Reading from {self.bib_path}")
        self.bib_db = BibDB.from_bib_file(self.bib_path)
        if self.save_formatted:
            logging.info(f"Saving formatted BibTeX to {self.formatted_bib_path}")
            self.bib_db.save(self.formatted_bib_path)

    def run(self):
        """Runs the dblpifier: Updates the entries in the BibDB with dblp information."""
        for entry in tqdm(self.bib_db):
            if self.dev_mode:  # Useful in case of crashes
                self.requester.save_cache()
                self.bib_db.save_report(self.report_path)
            if entry.status == EntryStatus.ALREADY_FROM_DBLP:
                continue
            hits = self.requester.fetch_hits(entry, num_hits=self.num_hits)
            if hits is None:
                entry.status = EntryStatus.NO_HIT
                continue
            match = top_hit(entry, hits)
            if match is None:
                entry.status = EntryStatus.NO_MATCH
                continue
            entry.set_match(match)  # sets status to MATCHED
            bib_str = self.requester.fetch_bib(entry.match_url)
            if bib_str is None:
                continue
            entry.set_entry(bib_str)
            entry.status = EntryStatus.UPDATED
        logging.info(f"Saving dblpified BibTeX to {self.dblpified_bib_path}")
        self.bib_db.save(self.dblpified_bib_path)
        logging.info(f"Saving report to {self.report_path}")
        self.bib_db.save_report(self.report_path)
        self.requester.save_cache()
