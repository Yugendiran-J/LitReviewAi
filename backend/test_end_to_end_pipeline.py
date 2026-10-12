from app.services.end_to_end_pipeline_service import (
    run_end_to_end_pipeline
)

from app.database import SessionLocal


# ============================================================
# TEST CONFIGURATION
# ============================================================

PROJECT_ID = 3

KEYWORD = (
    "Artificial Intelligence in "
    "Systematic Literature Review"
)

DOMAIN = (
    "Artificial Intelligence "
    "and Systematic Literature Review"
)

POPULATION = (
    "researchers and research studies"
)

INTERVENTION = (
    "artificial intelligence "
    "large language models"
)

COMPARISON = (
    "traditional systematic literature review methods"
)

OUTCOME = (
    "screening accuracy "
    "literature review efficiency"
)

STUDY_TYPE = (
    "systematic review"
)


# ============================================================
# START TEST
# ============================================================

print("\n")
print("=" * 70)
print("END-TO-END LITERATURE REVIEW PIPELINE")
print("=" * 70)


# ============================================================
# DATABASE SESSION
# ============================================================

db = SessionLocal()


try:

    # ========================================================
    # RUN COMPLETE PIPELINE
    # ========================================================

    result = run_end_to_end_pipeline(

        db=db,

        project_id=PROJECT_ID,

        keyword=KEYWORD,

        domain=DOMAIN,

        population=POPULATION,

        intervention=INTERVENTION,

        comparison=COMPARISON,

        outcome=OUTCOME,

        study_type=STUDY_TYPE
    )


    # ========================================================
    # PIPELINE RESULT
    # ========================================================

    print("\n")
    print("=" * 70)
    print("PIPELINE COMPLETED")
    print("=" * 70)


    # ========================================================
    # MODEL 1 + MODEL 2
    # ========================================================

    discovery_screening = result.get(
        "discovery_screening",
        {}
    )


    # ========================================================
    # MODEL 1 RESULTS
    # ========================================================

    print("\n")
    print("=" * 70)
    print("MODEL 1 - DISCOVERY")
    print("=" * 70)

    model1 = discovery_screening

    queries = model1.get(
        "queries",
        []
    )

    print(
        f"Generated queries: "
        f"{len(queries)}"
    )

    for index, query in enumerate(
        queries,
        start=1
    ):

        print(
            f"{index}. {query}"
        )


    # ========================================================
    # CANDIDATE PAPERS
    # ========================================================

    candidate_collection = (
        discovery_screening.get(
            "candidate_collection",
            {}
        )
    )

    candidate_count = (
        candidate_collection.get(
            "total_candidates",
            0
        )
    )

    print("\n")
    print("=" * 70)
    print("CANDIDATE PAPERS")
    print("=" * 70)

    print(
        f"Candidates: "
        f"{candidate_count}"
    )


    # ========================================================
    # PREFILTER
    # ========================================================

    prefilter = (
        discovery_screening.get(
            "prefilter",
            {}
        )
    )

    prefilter_count = (
        prefilter.get(
            "selected_count",
            0
        )
    )

    print("\n")
    print("=" * 70)
    print("PRE-FILTER")
    print("=" * 70)

    print(
        f"Papers selected for Model 2: "
        f"{prefilter_count}"
    )

    print(
        "Maximum Model 2 papers: 20"
    )


    # ========================================================
    # MODEL 2 RESULTS
    # ========================================================

    model2 = (
        discovery_screening.get(
            "model2",
            {}
        )
    )

    screening_results = model2.get(
        "results",
        []
    )

    print("\n")
    print("=" * 70)
    print("MODEL 2 - PICOS SCREENING")
    print("=" * 70)

    print(
        f"Screened papers: "
        f"{len(screening_results)}"
    )


    # ========================================================
    # BUILD SCREENING CATEGORIES
    # ========================================================

    included = []

    uncertain = []

    excluded = []


    for paper in screening_results:

        decision = str(
            paper.get(
                "decision",
                ""
            )
        ).lower().strip()


        if decision == "include":

            included.append(
                paper
            )

        elif decision == "uncertain":

            uncertain.append(
                paper
            )

        elif decision == "exclude":

            excluded.append(
                paper
            )


    # ========================================================
    # SCREENING SUMMARY
    # ========================================================

    print("\n")
    print("=" * 70)
    print("MODEL 2 SCREENING SUMMARY")
    print("=" * 70)

    print(
        f"Included: "
        f"{len(included)}"
    )

    print(
        f"Uncertain: "
        f"{len(uncertain)}"
    )

    print(
        f"Excluded: "
        f"{len(excluded)}"
    )


    # ========================================================
    # FULL-TEXT CANDIDATES
    # ========================================================

    fulltext_candidates = result.get(
        "fulltext_candidates",
        {}
    )

    fulltext_included = (
        fulltext_candidates.get(
            "included",
            []
        )
    )

    print("\n")
    print("=" * 70)
    print("FULL-TEXT SHORTLIST")
    print("=" * 70)

    print(
        f"Full-text candidates: "
        f"{len(fulltext_included)}"
    )


    # ========================================================
    # MODEL 3
    # ========================================================

    model3 = result.get(
        "model3",
        {}
    )

    extraction_results = (
        model3.get(
            "extraction_results",
            []
        )
    )

    verification_results = (
        model3.get(
            "verification_results",
            []
        )
    )

    print("\n")
    print("=" * 70)
    print("MODEL 3 - FULL-TEXT ANALYSIS")
    print("=" * 70)

    print(
        f"Extraction results: "
        f"{len(extraction_results)}"
    )

    print(
        f"Verification results: "
        f"{len(verification_results)}"
    )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n")
    print("=" * 70)
    print("FINAL PIPELINE SUMMARY")
    print("=" * 70)

    print(
        f"Candidate papers: "
        f"{candidate_count}"
    )

    print(
        f"Model 2 screened: "
        f"{len(screening_results)}"
    )

    print(
        f"Model 2 included: "
        f"{len(included)}"
    )

    print(
        f"Model 2 uncertain: "
        f"{len(uncertain)}"
    )

    print(
        f"Model 2 excluded: "
        f"{len(excluded)}"
    )

    print(
        f"Model 3 extracted: "
        f"{len(extraction_results)}"
    )

    print(
        f"Evidence verified: "
        f"{len(verification_results)}"
    )


    print("\n")
    print("=" * 70)
    print("END-TO-END TEST SUCCESSFUL")
    print("=" * 70)


except Exception as error:

    print("\n")
    print("=" * 70)
    print("PIPELINE TEST FAILED")
    print("=" * 70)

    print(
        f"\nError: {error}"
    )

    raise


finally:

    db.close()