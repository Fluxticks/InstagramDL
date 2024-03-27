import requests
from typing import Dict
from random import randint

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
