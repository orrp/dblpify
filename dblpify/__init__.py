from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

# Make output dir relative to the current file
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

CACHE_DIR = ROOT_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)


def formatted_bib_filename(bib_path: Path) -> Path:
    return Path(f"{bib_path.stem}_formatted.bib")


def dblpified_bib_filename(bib_path: Path) -> Path:
    return Path(f"{bib_path.stem}_dblpified.bib")


def cache_path(bib_path: Path) -> Path:
    return CACHE_DIR / f"{bib_path.stem}_responses.pkl"


def report_filename(bib_path: Path) -> Path:
    return Path(f"{bib_path.stem}_report.csv")
