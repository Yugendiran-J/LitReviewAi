import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any


BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

BATCH_SIZE = 20
REQUEST_TIMEOUT = 30


# ============================================================
# PUBMED SEARCH
# ============================================================

def search_pubmed(query: str, max_results: int = 10):
    """
    Search PubMed and return PubMed IDs.
    """

    if not query or not query.strip():
        raise ValueError("PubMed search query cannot be empty.")

    query = query.strip()

    if len(query) < 3:
        raise ValueError("PubMed search query must contain at least three characters.")

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results
    }

    try:
        response = requests.get(
            f"{BASE_URL}/esearch.fcgi",
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            "PubMed search request failed. Check your internet connection "
            "and PubMed availability, then try again."
        ) from error

    try:
        data = response.json()

    except ValueError:
        raise ValueError("PubMed returned an invalid JSON response.")

    search_result = data.get("esearchresult", {})

    if not isinstance(search_result, dict):
        raise ValueError("PubMed returned an invalid search response.")

    id_list = search_result.get("idlist", [])

    if not isinstance(id_list, list):
        raise ValueError("PubMed returned an invalid paper ID list.")

    print(f"PubMed papers found: {len(id_list)}")

    return id_list


# ============================================================
# BATCH HELPER
# ============================================================

def _chunks(items: List[str], size: int):

    for index in range(0, len(items), size):
        yield items[index:index + size]


# ============================================================
# FETCH PUBMED DETAILS
# ============================================================

def fetch_pubmed_details(pubmed_ids):
    """
    Fetch PubMed details safely in batches.

    This function is kept with the original name because
    candidate_service.py imports fetch_pubmed_details().
    """

    if not pubmed_ids:
        return []

    unique_ids = list(
        dict.fromkeys(
            str(pubmed_id).strip()
            for pubmed_id in pubmed_ids
            if pubmed_id
        )
    )

    print()
    print(
        f"Fetching PubMed details for "
        f"{len(unique_ids)} papers..."
    )

    print(
        f"Using batch size: {BATCH_SIZE}"
    )

    all_records = []
    failed_batches = 0

    batches = list(
        _chunks(
            unique_ids,
            BATCH_SIZE
        )
    )

    for batch_number, batch_ids in enumerate(
        batches,
        start=1
    ):

        print(
            f"Fetching batch "
            f"{batch_number}/{len(batches)} "
            f"({len(batch_ids)} papers)..."
        )

        params = {
            "db": "pubmed",
            "id": ",".join(batch_ids),
            "retmode": "xml"
        }

        try:

            response = requests.get(
                f"{BASE_URL}/efetch.fcgi",
                params=params,
                timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()

        except requests.exceptions.RequestException:
            failed_batches += 1
            continue

        try:

            root = ET.fromstring(
                response.text
            )

        except ET.ParseError:
            failed_batches += 1
            continue

        records = parse_pubmed_xml(root)

        all_records.extend(records)

    print()
    print(
        f"Total PubMed details retrieved: "
        f"{len(all_records)}"
    )

    if failed_batches and not all_records:
        raise RuntimeError(
            "PubMed found paper IDs but could not retrieve their metadata. "
            "Check your internet connection and try again."
        )

    return all_records


# ============================================================
# XML PARSER
# ============================================================

def parse_pubmed_xml(
    root
) -> List[Dict[str, Any]]:

    records = []

    for article in root.findall(
        ".//PubmedArticle"
    ):

        try:

            # ------------------------------------------------
            # PMID
            # ------------------------------------------------

            pmid_element = article.find(
                ".//PMID"
            )

            pubmed_id = ""

            if pmid_element is not None:

                pubmed_id = (
                    pmid_element.text or ""
                ).strip()

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            title_element = article.find(
                ".//ArticleTitle"
            )

            title = ""

            if title_element is not None:

                title = "".join(
                    title_element.itertext()
                ).strip()

            # ------------------------------------------------
            # ABSTRACT
            # ------------------------------------------------

            abstract_parts = []

            for abstract_element in article.findall(
                ".//Abstract/AbstractText"
            ):

                text = "".join(
                    abstract_element.itertext()
                ).strip()

                if not text:
                    continue

                label = abstract_element.attrib.get(
                    "Label"
                )

                if label:

                    abstract_parts.append(
                        f"{label}: {text}"
                    )

                else:

                    abstract_parts.append(
                        text
                    )

            abstract = "\n\n".join(
                abstract_parts
            )

            # ------------------------------------------------
            # AUTHORS
            # ------------------------------------------------

            authors = []

            for author in article.findall(
                ".//AuthorList/Author"
            ):

                collective_name = author.findtext(
                    "CollectiveName",
                    default=""
                )

                last_name = author.findtext(
                    "LastName",
                    default=""
                )

                initials = author.findtext(
                    "Initials",
                    default=""
                )

                if collective_name:

                    authors.append(
                        collective_name.strip()
                    )

                elif last_name:

                    author_name = (
                        last_name.strip()
                    )

                    if initials:

                        author_name += (
                            f" {initials.strip()}"
                        )

                    authors.append(
                        author_name
                    )

            authors_text = ", ".join(
                authors
            )

            # ------------------------------------------------
            # PUBLICATION YEAR
            # ------------------------------------------------

            publication_year = None

            year_candidates = [

                article.findtext(
                    ".//PubDate/Year"
                ),

                article.findtext(
                    ".//ArticleDate/Year"
                ),

                article.findtext(
                    ".//PubMedPubDate[@PubStatus='pub']/Year"
                )
            ]

            for year in year_candidates:

                if year and year.isdigit():

                    publication_year = int(
                        year
                    )

                    break

            # ------------------------------------------------
            # JOURNAL
            # ------------------------------------------------

            journal = article.findtext(
                ".//Journal/Title",
                default=""
            ).strip()

            # ------------------------------------------------
            # DOI
            # ------------------------------------------------

            doi = ""

            for article_id in article.findall(
                ".//ArticleId"
            ):

                id_type = article_id.attrib.get(
                    "IdType",
                    ""
                ).lower()

                if id_type == "doi":

                    doi = (
                        article_id.text or ""
                    ).strip()

                    break

            # ------------------------------------------------
            # URL
            # ------------------------------------------------

            url = ""

            if pubmed_id:

                url = (
                    "https://pubmed.ncbi.nlm.nih.gov/"
                    f"{pubmed_id}/"
                )

            # ------------------------------------------------
            # RECORD
            # ------------------------------------------------

            record = {

                "pubmed_id":
                    pubmed_id,

                "title":
                    title,

                "authors":
                    authors_text,

                "abstract":
                    abstract,

                "publication_year":
                    publication_year,

                "journal":
                    journal,

                "doi":
                    doi,

                "url":
                    url,

                "source":
                    "PubMed"
            }

            records.append(
                record
            )

        except Exception as error:

            print(
                "Failed to parse one PubMed record:",
                error
            )

            continue

    return records


# ============================================================
# ABSTRACT FETCH
# ============================================================

def fetch_pubmed_abstracts(
    pubmed_ids: List[str]
) -> Dict[str, str]:

    records = fetch_pubmed_details(
        pubmed_ids
    )

    abstracts = {}

    for record in records:

        pubmed_id = record.get(
            "pubmed_id"
        )

        abstract = record.get(
            "abstract"
        )

        if pubmed_id and abstract:

            abstracts[
                str(pubmed_id)
            ] = abstract

    return abstracts