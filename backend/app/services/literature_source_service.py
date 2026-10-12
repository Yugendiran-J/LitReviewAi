import re
import xml.etree.ElementTree as ET
import os

import requests
from dotenv import load_dotenv


REQUEST_TIMEOUT = 30
USER_AGENT = "LitReviewAI/1.0 (literature discovery)"
load_dotenv()


def get_literature_sources() -> list[dict]:
    ieee_configured = bool(os.getenv("IEEE_XPLORE_API_KEY"))
    serpapi_configured = bool(os.getenv("SERPAPI_API_KEY"))
    return [
        {
            "id": "pubmed",
            "name": "PubMed",
            "available": True,
            "description": "Biomedical and life sciences literature.",
        },
        {
            "id": "openalex",
            "name": "OpenAlex",
            "available": True,
            "description": "Cross-disciplinary open research index.",
        },
        {
            "id": "crossref",
            "name": "Crossref",
            "available": True,
            "description": "DOI and publisher metadata.",
        },
        {
            "id": "arxiv",
            "name": "arXiv",
            "available": True,
            "description": "Open preprints in computer science, physics, and other fields.",
        },
        {
            "id": "ieee_xplore",
            "name": "IEEE Xplore",
            "available": ieee_configured,
            "description": (
                "Configure IEEE_XPLORE_API_KEY in the backend .env file."
                if not ieee_configured
                else "IEEE Xplore publications (API credentials configured)."
            ),
        },
        {
            "id": "google_scholar",
            "name": "Google Scholar",
            "available": serpapi_configured,
            "description": (
                "Configure SERPAPI_API_KEY in the backend .env file to search "
                "Google Scholar via SerpApi."
                if not serpapi_configured
                else "Google Scholar results via SerpApi."
            ),
        },
        {
            "id": "researchgate",
            "name": "ResearchGate",
            "available": False,
            "description": (
                "No supported official public search API is configured; "
                "automated scraping is intentionally not used."
            ),
        },
    ]


def _plain_query(query: str) -> str:
    query = re.sub(r"\[[^\]]+\]", " ", query)
    query = re.sub(r"\b(?:AND|OR|NOT)\b", " ", query, flags=re.IGNORECASE)
    query = re.sub(r"[()\"*]", " ", query)
    return " ".join(query.split())


def _request_json(url: str, params: dict) -> dict:
    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError(f"{url} returned an invalid JSON response.")
    return data


def _reconstruct_abstract(inverted_index: dict | None) -> str:
    if not isinstance(inverted_index, dict):
        return ""

    words = {}
    for word, positions in inverted_index.items():
        if isinstance(positions, list):
            for position in positions:
                if isinstance(position, int) and position >= 0:
                    words[position] = word
    return " ".join(words[index] for index in sorted(words))


def search_openalex(query: str, max_results: int = 10) -> list[dict]:
    search_term = _plain_query(query)
    if not search_term:
        return []

    data = _request_json(
        "https://api.openalex.org/works",
        {
            "search": search_term,
            "per-page": max_results,
            "select": (
                "id,doi,title,publication_year,authorships,"
                "primary_location,abstract_inverted_index,"
                "open_access"
            ),
        },
    )

    works = data.get("results", [])
    if not isinstance(works, list):
        raise ValueError("OpenAlex returned an invalid works list.")

    papers = []
    for work in works:
        if not isinstance(work, dict) or not work.get("title"):
            continue

        authorships = work.get("authorships") or []
        authors = [
            authorship.get("author", {}).get("display_name")
            for authorship in authorships
            if isinstance(authorship, dict)
            and isinstance(authorship.get("author"), dict)
            and authorship["author"].get("display_name")
        ]

        location = work.get("primary_location") or {}
        venue = location.get("source") or {}
        open_access = work.get("open_access") or {}

        papers.append(
            {
                "title": work["title"],
                "authors": ", ".join(authors) or None,
                "abstract": _reconstruct_abstract(
                    work.get("abstract_inverted_index")
                ),
                "publication_year": work.get("publication_year"),
                "journal": venue.get("display_name"),
                "doi": work.get("doi"),
                "url": (
                    open_access.get("oa_url")
                    or work.get("doi")
                    or work.get("id")
                ),
                "source": "OpenAlex",
            }
        )

    return papers


def _crossref_year(item: dict) -> int | None:
    for field in ("published-print", "published-online", "issued"):
        date_parts = (item.get(field) or {}).get("date-parts")
        if date_parts and date_parts[0] and isinstance(date_parts[0][0], int):
            return date_parts[0][0]
    return None


def search_crossref(query: str, max_results: int = 10) -> list[dict]:
    search_term = _plain_query(query)
    if not search_term:
        return []

    data = _request_json(
        "https://api.crossref.org/works",
        {
            "query.bibliographic": search_term,
            "rows": max_results,
        },
    )
    message = data.get("message", {})
    items = message.get("items", []) if isinstance(message, dict) else []
    if not isinstance(items, list):
        raise ValueError("Crossref returned an invalid works list.")

    papers = []
    for item in items:
        if not isinstance(item, dict):
            continue
        titles = item.get("title") or []
        if not titles or not titles[0]:
            continue

        authors = [
            " ".join(part for part in (author.get("given"), author.get("family")) if part)
            for author in (item.get("author") or [])
            if isinstance(author, dict)
        ]
        containers = item.get("container-title") or []
        doi = item.get("DOI")

        papers.append(
            {
                "title": titles[0],
                "authors": ", ".join(author for author in authors if author) or None,
                "abstract": item.get("abstract"),
                "publication_year": _crossref_year(item),
                "journal": containers[0] if containers else None,
                "doi": doi,
                "url": item.get("URL") or (f"https://doi.org/{doi}" if doi else None),
                "source": "Crossref",
            }
        )

    return papers


def search_arxiv(query: str, max_results: int = 10) -> list[dict]:
    search_term = _plain_query(query)
    if not search_term:
        return []

    response = requests.get(
        "https://export.arxiv.org/api/query",
        params={
            "search_query": f"all:({search_term})",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as error:
        raise ValueError("arXiv returned invalid Atom XML.") from error

    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    papers = []
    for entry in root.findall("atom:entry", namespace):
        title = entry.findtext("atom:title", default="", namespaces=namespace)
        if not title.strip():
            continue
        published = entry.findtext(
            "atom:published", default="", namespaces=namespace
        )
        authors = [
            author.findtext("atom:name", default="", namespaces=namespace)
            for author in entry.findall("atom:author", namespace)
        ]
        papers.append(
            {
                "title": " ".join(title.split()),
                "authors": ", ".join(author for author in authors if author) or None,
                "abstract": entry.findtext(
                    "atom:summary", default="", namespaces=namespace
                ).strip(),
                "publication_year": (
                    int(published[:4]) if published[:4].isdigit() else None
                ),
                "journal": "arXiv",
                "doi": None,
                "url": entry.findtext("atom:id", default="", namespaces=namespace),
                "source": "arXiv",
            }
        )

    return papers


def search_ieee_xplore(query: str, max_results: int = 10) -> list[dict]:
    api_key = os.getenv("IEEE_XPLORE_API_KEY")
    if not api_key:
        raise ValueError(
            "IEEE Xplore search requires IEEE_XPLORE_API_KEY in the backend .env file."
        )

    search_term = _plain_query(query)
    if not search_term:
        return []

    try:
        data = _request_json(
            "https://ieeexploreapi.ieee.org/api/v1/search/articles",
            {
                "apikey": api_key,
                "format": "json",
                "querytext": search_term,
                "max_records": max_results,
                "start_record": 1,
                "sort_field": "relevance",
                "sort_order": "desc",
            },
        )
    except requests.RequestException as error:
        response = getattr(error, "response", None)
        status_code = getattr(response, "status_code", None)
        if status_code in (401, 403):
            message = (
                "IEEE Xplore rejected the API credentials "
                f"(HTTP {status_code}). Check that IEEE_XPLORE_API_KEY is "
                "valid and active, then restart the backend."
            )
        elif status_code is not None:
            message = (
                f"IEEE Xplore returned HTTP {status_code}. "
                "Check the request and try again later."
            )
        else:
            message = (
                "Could not reach the IEEE Xplore API. Check your internet "
                "connection and try again."
            )
        raise RuntimeError(message) from error
    articles = data.get("articles", [])
    if not isinstance(articles, list):
        raise ValueError("IEEE Xplore returned an invalid articles list.")

    papers = []
    for article in articles:
        if not isinstance(article, dict):
            continue

        title = article.get("article_title")
        if not title:
            continue

        author_data = article.get("authors") or {}
        raw_author_list = (
            author_data.get("authors")
            if isinstance(author_data, dict)
            else None
        )
        author_list = raw_author_list if isinstance(raw_author_list, list) else []
        authors = [
            author["full_name"]
            for author in author_list
            if isinstance(author, dict) and author.get("full_name")
        ]
        doi = article.get("doi")
        publication_year = article.get("publication_year")
        if isinstance(publication_year, str) and publication_year.isdigit():
            publication_year = int(publication_year)
        if not isinstance(publication_year, int):
            publication_year = None

        papers.append(
            {
                "title": title,
                "authors": ", ".join(authors) or None,
                "abstract": article.get("abstract"),
                "publication_year": publication_year,
                "journal": article.get("publication_title"),
                "doi": doi,
                "url": (
                    article.get("html_url")
                    or article.get("pdf_url")
                    or (f"https://doi.org/{doi}" if doi else None)
                ),
                "source": "IEEE Xplore",
            }
        )

    return papers


def search_google_scholar(query: str, max_results: int = 10) -> list[dict]:
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError(
            "Google Scholar search requires SERPAPI_API_KEY in the backend .env file."
        )

    search_term = _plain_query(query)
    if not search_term:
        return []

    try:
        response = requests.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google_scholar",
                "api_key": api_key,
                "q": search_term,
                "num": min(max_results, 20),
                "hl": "en",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        response = getattr(error, "response", None)
        status_code = getattr(response, "status_code", None)
        if status_code in (401, 403):
            message = (
                "Google Scholar search credentials were rejected "
                f"(HTTP {status_code}). Check that SERPAPI_API_KEY is valid and active."
            )
        elif status_code == 429:
            message = (
                "Google Scholar search reached the SerpApi rate or usage limit "
                "(HTTP 429). Check your SerpApi plan and try again later."
            )
        elif status_code is not None:
            message = f"Google Scholar search failed (HTTP {status_code})."
        else:
            message = (
                "Could not reach SerpApi for Google Scholar search. "
                "Check your internet connection and try again."
            )
        raise RuntimeError(message) from error

    if not isinstance(data, dict):
        raise ValueError("SerpApi returned an invalid Google Scholar response.")
    if data.get("error"):
        raise RuntimeError(
            "SerpApi returned an error for the Google Scholar search. "
            "Check the API key, query, and SerpApi account status."
        )

    results = data.get("organic_results", [])
    if not isinstance(results, list):
        raise ValueError("SerpApi returned an invalid Google Scholar results list.")

    papers = []
    for result in results:
        if not isinstance(result, dict) or not result.get("title"):
            continue

        publication_info = result.get("publication_info") or {}
        if not isinstance(publication_info, dict):
            publication_info = {}

        author_data = publication_info.get("authors")
        authors = []
        if isinstance(author_data, list):
            authors = [
                author["name"]
                for author in author_data
                if isinstance(author, dict) and author.get("name")
            ]
        summary = publication_info.get("summary")
        if not authors and isinstance(summary, str) and " - " in summary:
            authors = [summary.split(" - ", 1)[0].strip()]

        year = publication_info.get("year")
        if isinstance(year, str) and year.isdigit():
            year = int(year)
        if not isinstance(year, int):
            year_match = (
                re.search(r"\b(?:19|20)\d{2}\b", summary)
                if isinstance(summary, str)
                else None
            )
            year = int(year_match.group(0)) if year_match else None

        papers.append(
            {
                "title": result["title"],
                "authors": ", ".join(authors) or None,
                "abstract": result.get("snippet"),
                "publication_year": year,
                "journal": publication_info.get("journal"),
                "doi": result.get("doi"),
                "url": result.get("link"),
                "source": "Google Scholar",
            }
        )

    return papers
