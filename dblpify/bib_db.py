from enum import Enum
from pandas import DataFrame
import bibtexparser


class EntryStatus(str, Enum):
    """Status of an entry in the BibDB."""
    NOT_YET_PROCESSED = "Not yet processed (error)"
    ALREADY_FROM_DBLP = "Already from dblp"
    NO_HIT = "No hits to query"
    NO_MATCH = "No match among hits"
    MATCHED = "Matched but not yet updated (error)"
    UPDATED = "Updated with dblp entry!"


class Entry:
    """Wrapper around a BibTeX entry. It keeps track of the status of the entry and its match on DBLP."""
    def __init__(self, entry):
        self.match = None
        self.query_url = None
        self.status = EntryStatus.NOT_YET_PROCESSED
        self.entry = entry
        # If the entry is already from DBLP, set status and match accordingly
        if 'bibsource' in entry and 'dblp' in entry['bibsource']:
            self.status = EntryStatus.ALREADY_FROM_DBLP
            assert 'biburl' in entry and 'dblp' in entry['biburl']
            assert entry['biburl'].endswith('.bib')
            url_on_dblp = entry['biburl'][:-4]  # remove .bib suffix to get the DBLP page
            self.match = {'url': url_on_dblp}

    @property
    def key(self):
        return self.entry['ID']

    @property
    def title(self):
        return self.entry['title']

    @property
    def authors(self):
        return self.entry['author']

    @property
    def year(self):
        return self.entry['year']

    @property
    def match_url(self):
        return self.match.get('url') if self.match else None

    def set_entry(self, bib_str: str):
        """Set the entry with the new BibTeX string, parsed with bibtexparser.
        This method should be called only if the entry has been matched.
        Parameters:
            bib_str (str): BibTeX string of the new entry.
        """
        assert self.status == EntryStatus.MATCHED, f"Entry {self.key} not matched yet."

        parsed_bib = bibtexparser.loads(bib_str)
        assert len(parsed_bib.entries) == 1  # Old DBLP used to have multiple entries for some conference entries
        parsed_bib.entries[0]['ID'] = self.key  # Ensure the key is the same
        self.entry = parsed_bib.entries[0]
        self.status = EntryStatus.UPDATED

    def set_query_url(self, query_url: str):
        """Set the query URL for the entry. This method should be called only once.
        Parameters:
            query_url (str): URL used to query DBLP.
        """
        assert self.query_url is None or self.query_url == query_url, f"Query already set for {self.key}"
        self.query_url = query_url

    def set_match(self, match: dict):
        """Set the match for the entry. This method should be called only once.
        Parameters:
            match (dict): Match for the entry as returned by DBLP.
        """
        self.match = match
        self.status = EntryStatus.MATCHED


class BibDB:
    """Wrapper around a bibtexparser BibDatabase. It uses the Entry class to keep track of the status of each entry,
    and provides a method to generate and save a report of the status of each entry."""
    def __init__(self, bib_db: bibtexparser.bibdatabase.BibDatabase):
        self._key_to_entry = {entry['ID']: Entry(entry) for entry in bib_db.entries}
        # assert no duplicate keys in bib_db
        assert len(self._key_to_entry) == len(bib_db.entries), "Duplicate keys in bib_db."

    def _to_bib_db(self):
        """Converts the BibDB to a bibtexparser BibDatabase, which can be saved to a .bib file."""
        bib_db = bibtexparser.bibdatabase.BibDatabase()
        bib_db.entries = [entry.entry for entry in self._key_to_entry.values()]
        return bib_db

    def save(self, path):
        """Saves the BibDB to a .bib file."""
        with open(path, 'w') as f:
            bibtexparser.dump(self._to_bib_db(), f)

    def __len__(self):
        return len(self._key_to_entry)

    def __iter__(self):
        return iter(self._key_to_entry.values())

    @classmethod
    def from_bib_file(cls, path):
        """Creates a BibDB from a .bib file."""
        with open(path, 'r') as f:
            bib_db = bibtexparser.load(f)
        return cls(bib_db)

    def _generate_report(self) -> DataFrame:
        return DataFrame(
            [
                {
                    "Key": key,
                    "Status": entry.status,
                    # "Query URL": entry.query_url,
                    "Match URL": entry.match_url,
                }
                for key, entry in self._key_to_entry.items()
            ]
        )

    def save_report(self, path):
        """Saves the report of the BibDB to a .csv file. The report lists the status of each entry, the URL
        used for querying DBLP, and the URL of the match on DBLP (if any).
        """
        self._generate_report().to_csv(path, index=False)
