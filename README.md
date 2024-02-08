# dblpify
> _dblpify (verb, transitive)_: The act of updating one's bibliography from the [dblp computer science bibliography](https://dblp.org) service.
> - Etymology: From the [orphan initialism](https://dblp.org/faq/What+is+the+meaning+of+the+acronym+dblp.html) _dblp_ and the English suffix _-ify_, meaning "to make" or "to cause to become".
> - Example usage: "I accidentally cited the arXiv version of the paper instead of the journal one. I really should have dblpified my references before submitting!"


`dblpify` is a tool for replacing BibTeX entries with their corresponding entries from [dblp](https://dblp.org).
Keys are preserved so that no changes to the LaTeX source are necessary.
It uses [bibtexparser](https://bibtexparser.readthedocs.io/en/main/) for parsing,
and handles rate limiting, caching, and [matching](#matching-heuristic).

### Installation
To install `dblpify`, you first need a working Python installation (e.g. [Miniconda](https://docs.anaconda.com/free/miniconda/)).
Then, clone this repository and install the package:
```bash
git clone ...
pip install dblpify
```

### Usage
You can use `dblpify` directly from the command line. Here is a basic example:
```bash
python run.py --bib_path references.bib
```
By default, the output will be saved to the `output` directory, and will consist of two files:
- `references_dblpified.bib`: The original .bib file with entries replaced by their dblp counterparts.
- `references_report.csv`: An entry-by-entry report on the outcome of the matching process.

Here are the full options:
```
usage: dblpify.py [-h] [--bib_path BIB_PATH] [--out_path OUT_PATH] [--save_formatted] [--clear_cache] [--num_hits NUM_HITS] [--log_path LOG_PATH] [--dev]

options:
  -h, --help           show this help message and exit
  --bib_path BIB_PATH  Path to the BibTeX file.
  --out_path OUT_PATH  Directory to store outputs.
  --save_formatted     Save the original BibTeX in the same format as the updated one (useful for diffing).
  --clear_cache        Clear the cache before running.
  --num_hits NUM_HITS  Number of hits to request from DBLP.
  --log_path LOG_PATH  Path to log file (default stdout).
  --dev                Dev mode (saves report and response cache at each iteration).
```

### Reporting
Reports are output as a CSV and contain a row for each entry, with the following columns:
- `Key`: The BibTeX key of the entry. 
- `Status`: The outcome of the matching process. An uninterrupted run of the tool will result one of following:
  - `Updated with dblp entry!`: The entry was successfully matched and replaced.
  - `Already from dblp`: The entry was already from dblp and was left unchanged.
  - `No hits to query`: The entry's title was not found in dblp.
  - `No match among hits`: The entry's title was found in dblp, but no hit matched its title and author fields.
- `Match URL`: The URL of the matching entry in dblp, for entries that were updated.

You may additionally want to diff the original and dblpified .bib files to check for any discrepancies.
Unfortunately, the dblpified .bib does not retain the formatting (e.g. linebreaks) of the original .bib file, but
you can specify the `--save_formatted` flag to save the original .bib file in the new formatting, which can
be used for line-by-line comparison.

### Matching heuristic
`dblpify` uses a simple matching heuristic as follows. For each entry:
1. Query dblp for the entry's title.
2. Keep only hits that exactly match the title and author fields (up to special characters, case, spaces, etc.).
3. If multiple entries are matching, break ties according to venue type: book > journal > conference/workshop > preprint.

Entries that are already from dblp are left unchanged.

This heuristic may fail in some cases.
For example, it will fail to match entries with incomplete titles, or typos in author names.
For now, our approach is to minimize false matches and let the user complete the matching manually themselves.

## Contributing

This tool started as a quick hack to solve a personal problem, and is still very much a work in progress.
Please feel free to open an issue if you encounter a bug, or directly submit a pull request if you like. Thanks!

Here are a few ways you can help:
- [ ] Add unit tests (you may want to use pytest mock).
- [ ] Retain the formatting (e.g. spacing) of the original .bib file.
- [ ] Improve the matching heuristic. 
- [ ] Wrap the tool in a browser extension so it can be used directly from Overleaf.

## License

`dblpify` is available under the MIT license. See the LICENSE file for more info.