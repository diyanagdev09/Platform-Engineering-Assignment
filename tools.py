import re
from html import unescape
import requests


def search_wikipedia(query):
    """Search Wikipedia for background information."""

    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 5
    }

    try:
        response = requests.get(
        url,
        params=params,
        timeout=10,
        headers={
            "User-Agent": "PredixionResearchAgent/1.0 (educational project)"
        }
    )
        response.raise_for_status()
        results = response.json()["query"]["search"]

        return [
            {
                "title": item["title"],
                "snippet": unescape(
                re.sub(r"<[^>]+>", "", item.get("snippet", ""))
            ),
                "source": "Wikipedia",
                "url": (
                    "https://en.wikipedia.org/wiki/"
                    + item["title"].replace(" ", "_")
            )
            }
            for item in results
        ]

    except (requests.RequestException, ValueError, KeyError) as error:
        return {"error": f"Wikipedia search failed: {error}"}


def search_openalex(query):
    """Search scholarly works using the OpenAlex API."""

    url = "https://api.openalex.org/works"

    params = {
        "search": query,
        "per-page": 5
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        results = response.json()["results"]

        return [
            {
                "title": item.get("title"),
                "year": item.get("publication_year"),
                "source": "OpenAlex",
                "url": item.get("doi") or item.get("id")
            }
            for item in results
        ]

    except (requests.RequestException, ValueError, KeyError) as error:
        return {"error": f"OpenAlex search failed: {error}"}
