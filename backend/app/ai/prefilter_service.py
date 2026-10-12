import re


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def build_terms(keywords: list[str]) -> list[str]:

    terms = []

    for keyword in keywords:

        if not keyword:
            continue

        keyword = keyword.strip()

        if not keyword:
            continue

        normalized = normalize_text(keyword)

        if not normalized:
            continue

        # Keep complete phrase
        terms.append(normalized)

        # Also keep individual meaningful words
        words = normalized.split()

        for word in words:

            if len(word) >= 4:

                terms.append(word)

    # Remove duplicates while preserving order

    return list(
        dict.fromkeys(terms)
    )


def keyword_match_score(
    title: str,
    abstract: str,
    keywords: list[str]
) -> int:

    title_text = normalize_text(
        title
    )

    abstract_text = normalize_text(
        abstract
    )

    score = 0

    terms = build_terms(
        keywords
    )

    for term in terms:

        if not term:
            continue

        # Title match is more important
        if term in title_text:

            score += 4

        # Abstract match
        if term in abstract_text:

            score += 1

    return score


def prefilter_papers(
    papers: list[dict],
    keywords: list[str],
    max_papers: int = 3
):

    if not papers:

        return {
            "total_input": 0,
            "total_selected": 0,
            "high_relevance_count": 0,
            "medium_relevance_count": 0,
            "low_relevance_count": 0,
            "papers": []
        }

    cleaned_keywords = []

    for keyword in keywords:

        if not keyword:
            continue

        keyword = keyword.strip()

        if keyword:

            cleaned_keywords.append(
                keyword
            )

    cleaned_keywords = list(
        dict.fromkeys(
            cleaned_keywords
        )
    )

    scored_papers = []

    for paper in papers:

        title = paper.get(
            "title",
            ""
        )

        abstract = " ".join(
            part
            for part in (
                paper.get("abstract", ""),
                paper.get("full_text", ""),
            )
            if part
        )

        score = keyword_match_score(
            title=title,
            abstract=abstract,
            keywords=cleaned_keywords
        )

        scored_papers.append({

            **paper,

            "prefilter_score": score
        })

    # Highest score first

    scored_papers.sort(
        key=lambda paper:
            paper["prefilter_score"],
        reverse=True
    )

    # ----------------------------------------------------------
    # Relevance categories
    # ----------------------------------------------------------

    high_relevance = [
        paper
        for paper in scored_papers
        if paper["prefilter_score"] >= 6
    ]

    medium_relevance = [
        paper
        for paper in scored_papers
        if 3 <= paper["prefilter_score"] < 6
    ]

    low_relevance = [
        paper
        for paper in scored_papers
        if paper["prefilter_score"] < 3
    ]

    # ----------------------------------------------------------
    # Select top papers
    # ----------------------------------------------------------

    if max_papers < 1:

        max_papers = 1

    selected_papers = scored_papers[
        :max_papers
    ]

    return {

        "total_input":
            len(scored_papers),

        "total_selected":
            len(selected_papers),

        "high_relevance_count":
            len(high_relevance),

        "medium_relevance_count":
            len(medium_relevance),

        "low_relevance_count":
            len(low_relevance),

        "papers":
            selected_papers
    }