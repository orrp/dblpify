from difflib import SequenceMatcher
from unidecode import unidecode

from dblpify.bib_db import Entry

DBLP_TYPES_ORDERED = [
    'Books and Theses',
    'Parts in Books or Collections',
    'Journal Articles',
    'Conference and Workshop Papers',
    'Informal and Other Publications',
]


def normalize_string(s: str) -> str:
    # replace \aa with a
    s = s.replace('\\aa', 'a').replace('\\AA', 'A')
    s = unidecode(s)  # remove accents
    # replace - with space
    s = s.replace('-', ' ')
    # delete non-alphabetical characters and replace any whitespace with single space
    s = ''.join([c for c in s if c.isalpha() or c == ' ']).lower()
    # replace multiple spaces with single space
    s = ' '.join(s.split())
    # omit the string "extended abstract" which is often appended to titles
    s = s.replace('extended abstract', '')
    return s.strip()


def same_title(entry: Entry, hit, threshold=0.9):
    # delete non-alphabetical characters and replace spaces with single space
    a = normalize_string(entry.title)
    b = normalize_string(hit['title'])
    similarity = SequenceMatcher(None, a, b).ratio()
    return similarity >= threshold


def same_authors(entry: Entry, hit):
    normalized_authors_from_entry = normalize_string(entry.authors)
    authors = hit['authors']['author']
    if not isinstance(authors, list):  # if only one author, make it a list
        authors = [authors]
    for author in authors:
        author = normalize_string(author['text'])
        if author not in normalized_authors_from_entry:
            return False
    return True


def top_hit(entry: Entry, hits: list[dict]) -> dict | None:
    # keep only hits with valid types, matching titles and authors up to lower case
    valid_hits = []
    for hit in hits:
        # Splitting into three different ifs for debugging and clarity
        if hit['type'] not in DBLP_TYPES_ORDERED:
            continue
        if not same_authors(entry, hit):
            continue
        if not same_title(entry, hit):
            continue
        valid_hits.append(hit)
    if not valid_hits:  # unnecessary, but for clarity
        return None
    # return the hit with the highest type
    return sorted(valid_hits, key=lambda x: DBLP_TYPES_ORDERED.index(x['type']))[0]
