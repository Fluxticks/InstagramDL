import requests
from os.path import sep as PATHSEP
from random import randint
from typing import Dict
from urllib.parse import urlparse


MAGIC_DOC_NUMBER = 7341532402634560  # Required value by instagram.
INSTA_API_URL = "https://www.instagram.com/api/graphql"


def make_random_string(count: int) -> str:
    """Create a random string containing alpha-numeric characters of a given length.

    Args:
        count (int): The length of the string to generate.

    Returns:
        str: A random alpha-numeric string of the given length.
    """
    current = ""
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    for _ in range(count):
        current += chars[randint(0, len(chars) - 1)]
    return current


def get_post_data(post_url: str) -> Dict:
    """Get the all the data about a given Instagram post.

    Args:
        post_url (str): The URL to get the data from.

    Returns:
        Dict: The raw data returned from the API request.
    """
    headers = {
        "User-Agent": make_random_string(10),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": post_url,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.instagram.com",
        "Sec-Fetch-Site": "same-origin",
    }

    parts = post_url.split("/")
    if post_url.endswith("/"):
        short_code = parts[-2]
    else:
        short_code = parts[-1]

    data = f"__hs={make_random_string(10)}&lsd={make_random_string(11)}&variables=%7B%22shortcode%22:%22{short_code}%22%7D&doc_id={MAGIC_DOC_NUMBER}"

    response = requests.post(
        INSTA_API_URL,
        headers=headers,
        data=data,
    )

    return response.json()


def download_file(url: str, download_location: str, max_chunk_size: int) -> str:
    """A simple helper function to retrive a file from a URL.

    Args:
        url (str): The URL to retrieve the file from.
        download_location (str): The path to download the file to.
        max_chunk_size (int): The maximum chunk size to use.

    Returns:
        str: The filepath of the downloaded file.
    """
    filename = urlparse(url).path.split("/")[-1]
    filepath = f"{download_location}{PATHSEP}{filename}"
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=max_chunk_size):
                f.write(chunk)
    return filepath
