"""
src/web_fetcher.py — Web article fetching module
=================================================
Fetches article content from a URL and strips HTML boilerplate,
returning clean title and text for quiz generation.
"""

from __future__ import annotations

import re
import urllib.parse
import requests
from bs4 import BeautifulSoup


def fetch_article_content(url: str, timeout: int = 10) -> tuple[str, str]:
    """Fetch article content from a web URL.

    Parameters
    ----------
    url : str
        Target web page URL.
    timeout : int
        Request timeout in seconds.

    Returns
    -------
    tuple[str, str]
        (title, body_text) extracted from the web page.

    Raises
    ------
    ValueError
        If the URL is invalid or content is empty.
    requests.RequestException
        If the HTTP request fails.
    """
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 QuickQuizStudio/1.0"
    }

    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")

    # Remove unwanted tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg"]):
        tag.decompose()

    # Extract title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find("h1"):
        h1 = soup.find("h1")
        if h1 and h1.text:
            title = h1.text.strip()
    if not title:
        title = parsed.netloc

    # Extract article / main body
    main_node = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_=re.compile(r"content|article|post|entry|main", re.I))
        or soup.body
    )

    if not main_node:
        raise ValueError(f"Could not extract body content from {url}")

    # Clean text lines
    lines = [line.strip() for line in main_node.get_text("\n").splitlines()]
    clean_lines = [l for l in lines if len(l) > 15]  # ignore tiny navigation snippets
    body_text = "\n".join(clean_lines)

    if not body_text:
        raise ValueError(f"Extracted content is too short or empty from {url}")

    return title, body_text
