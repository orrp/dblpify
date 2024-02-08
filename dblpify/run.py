import argparse
import logging
from pathlib import Path

from dblpify.dblpifier import Dblpifier

if __name__ == '__main__':
    argparse = argparse.ArgumentParser()
    argparse.add_argument("--bib_path", type=str, default="references.bib", help="Path to the BibTeX file.")
    argparse.add_argument("--out_path", type=str, help="Directory to store outputs.", default="./output")
    argparse.add_argument("--save_formatted", action="store_true",
                          help="Save the original BibTeX in the same format as the updated one (useful for diffing).")
    argparse.add_argument("--clear_cache", action="store_true", help="Clear the cache before running.")
    argparse.add_argument("--num_hits", type=int, default=10, help="Number of hits to request from DBLP.")
    argparse.add_argument("--log_path", type=str, help="Path to log file (default stdout).")
    argparse.add_argument("--dev", action="store_true",
                          help="Dev mode (saves report and response cache at each iteration).")

    args = argparse.parse_args()
    if args.log_path:
        Path(args.log_path).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=args.log_path, level=logging.INFO)
    dblpifier = Dblpifier(args, logging)
    dblpifier.run()
