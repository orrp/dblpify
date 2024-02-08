import logging
import pickle as pkl
from pathlib import Path
from time import sleep, time
from typing import Any
from urllib.parse import urlencode

import requests
from tqdm import tqdm

from dblpify.matcher import normalize_string
from dblpify.bib_db import Entry

DBLP_RECOMMENDED_TIMEOUT = 2  # seconds


class DblpRequester:
    """Class to request information from DBLP."""

    base_url = 'https://dblp.org/search/publ/api'
    success_code = 200
    too_many_requests = 429

    cached_responses: dict[str, requests.Response]

    def __init__(self, logger, cache_path: Path | None):
        self.session = requests.Session()
        self.logger = logger

        self.cache_path = cache_path
        if cache_path is not None and cache_path.exists():
            self.logger.info(f"Loading responses from {cache_path}")
            with open(cache_path, "rb") as f:
                self.cached_responses = pkl.load(f)
        else:
            self.cached_responses = {}

        self._time_of_last_request = time()

    def _request(self, url: str) -> requests.Response:
        """Requests the given URL and returns the response. Caches the response. Handles rate limiting.
        Parameters:
            url (str): URL to request.
        """
        if url in self.cached_responses:
            self.logger.debug(f"Using cached response for {url}")
            return self.cached_responses[url]
        logging.info(f"Requesting {url}")
        # Sleep if last request was too recent
        if time() - self._time_of_last_request < DBLP_RECOMMENDED_TIMEOUT:
            sleep(DBLP_RECOMMENDED_TIMEOUT)
        response = self.session.get(url)
        while response.status_code == self.too_many_requests:
            time_to_sleep = int(response.headers["Retry-After"])
            self.logger.info(f"dblp sent 429 (too many requests); sleeping {time_to_sleep}")
            # create a nested tqdm to show sleep time without overwriting the progress bar
            for _ in tqdm(range(time_to_sleep), desc="Sleeping", leave=False):
                sleep(1)

            response = self.session.get(url)
        if response.status_code != self.success_code:
            self.logger.warning(f"Encountered status code {response.status_code}")
        self.cached_responses[url] = response
        return response

    def _dblp_query(self, entry: Entry, num_hits) -> requests.Response:
        """Queries DBLP for the given entry and returns the response.
        Parameters:
            entry (Entry): Entry to query for.
            num_hits (int): Number of hits to request.
        Returns:
            requests.Response: Response from DBLP.
        """
        query = entry.title
        # query +=  ' ' + entry['author']
        query = normalize_string(query)
        options = {
            'q': query,
            'format': 'json',
            'h': num_hits
        }
        entry.set_query_url(f'{self.base_url}?{urlencode(options)}')
        return self._request(entry.query_url)

    def fetch_bib(self, dblp_entry_url: str) -> str | None:
        """Fetches the BibTeX entry for the given DBLP URL.
        Parameters:
            dblp_entry_url (str): URL of an entry on DBLP.
        Returns:
            str: BibTeX entry as a string.
        """
        assert dblp_entry_url.startswith('https://dblp.org/')
        bib_url = f"{dblp_entry_url}.bib"
        return self._request(bib_url).text

    def fetch_hits(self, entry: Entry, num_hits=10) -> list[Any] | None:
        """Fetches the hits for the given entry by forming and issuing a query to DBLP.
        Parameters:
            entry (Entry): Entry to fetch hits for.
            num_hits (int): Number of hits to request.
        Returns:
            list[dict] | None: List of hits as returned by DBLP.
        """
        response = self._dblp_query(entry, num_hits)
        if response.status_code != self.success_code:
            self.logger.debug(f"DBLP response was not successful.")
            return None
        response = response.json().get('result').get('hits').get('hit')
        if response is None:
            self.logger.debug(f"DBLP query had no matches.")
            return None
        return [x.get('info') for x in response]

    def save_cache(self):
        """Saves the cached responses to a pkl file."""
        if self.cache_path is None:
            logging.debug("No cache_path provided, not saving.")
            return
        if not self.cached_responses:
            logging.debug("No responses to save.")
            return
        self.logger.info(f"Saving cached responses to {self.cache_path}")
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "wb") as f:
            pkl.dump(self.cached_responses, file=f)
