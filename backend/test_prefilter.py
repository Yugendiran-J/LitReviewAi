from app.ai.prefilter_service import prefilter_papers


papers = [
    {
        "title": "Artificial Intelligence in Systematic Literature Review",
        "abstract": "This study investigates AI-assisted literature review methods."
    },
    {
        "title": "Deep Learning for Image Classification",
        "abstract": "This paper presents a computer vision model."
    },
    {
        "title": "Large Language Models for Literature Screening",
        "abstract": "LLMs can assist researchers in screening scientific papers."
    }
]


keywords = [
    "artificial intelligence",
    "literature review",
    "LLM",
    "screening"
]


result = prefilter_papers(
    papers=papers,
    keywords=keywords,
    max_papers=2
)


print("\nPRE-FILTER RESULT")
print("=================")

print("Total input:", result["total_input"])
print("Total selected:", result["total_selected"])

for paper in result["papers"]:
    print(
        "\nTitle:",
        paper["title"]
    )

    print(
        "Score:",
        paper["prefilter_score"]
    )