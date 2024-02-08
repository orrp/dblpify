from setuptools import setup, find_packages

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="dblpify",
    description="Updating BibTeX entries with information from dblp.",
    long_description=readme,
    author="Orr Paradise",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "bibtexparser",
        "requests",
        "tqdm",
        "pandas",
        "unidecode",
        "pytest",
    ],
)
