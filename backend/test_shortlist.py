from app.database import SessionLocal

from app.services.shortlist_service import (
    get_model2_shortlist
)


PROJECT_ID = 2


db = SessionLocal()

try:

    print("\nAI MODEL 2 SHORTLIST")
    print("====================")

    result = get_model2_shortlist(
        db=db,
        project_id=PROJECT_ID
    )

    print("\nSUMMARY")
    print("=======")

    print(
        "Total screened:",
        result["total_screened"]
    )

    print(
        "Included:",
        result["included_count"]
    )

    print(
        "Uncertain:",
        result["uncertain_count"]
    )

    print(
        "Excluded:",
        result["excluded_count"]
    )


    print("\nSHORTLISTED PAPERS")
    print("==================")

    for index, paper in enumerate(
        result["included"],
        start=1
    ):

        print(
            f"\n{index}. {paper['title']}"
        )

        print(
            "Paper ID:",
            paper["paper_id"]
        )

        print(
            "PubMed ID:",
            paper["pubmed_id"]
        )

        print(
            "Confidence:",
            paper["confidence"]
        )

        print(
            "Reason:",
            paper["reason"]
        )


    print("\nUNCERTAIN PAPERS")
    print("================")

    for index, paper in enumerate(
        result["uncertain"],
        start=1
    ):

        print(
            f"{index}. {paper['title']}"
        )

finally:

    db.close()