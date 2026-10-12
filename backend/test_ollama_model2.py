from app.services.screening_model2_service import (
    screen_candidate_paper
)


print("=" * 60)
print("LITREVIEWAI - OLLAMA MODEL 2 TEST")
print("=" * 60)


try:

    result = screen_candidate_paper(

        title=(
            "Artificial Intelligence Applications "
            "in Healthcare: A Systematic Review"
        ),

        abstract=(
            "This systematic review examines the use of "
            "artificial intelligence and machine learning "
            "methods in healthcare applications. The study "
            "evaluates their impact on patient outcomes and "
            "clinical decision support."
        ),

        population="Healthcare patients",

        intervention="Artificial Intelligence",

        comparison="Traditional healthcare methods",

        outcome="Improved healthcare outcomes",

        study_type="Systematic Review"
    )


    print("\nModel 2 Result:")
    print("-" * 60)

    print(
        f"Population Match: "
        f"{result['population_match']}"
    )

    print(
        f"Intervention Match: "
        f"{result['intervention_match']}"
    )

    print(
        f"Comparison Match: "
        f"{result['comparison_match']}"
    )

    print(
        f"Outcome Match: "
        f"{result['outcome_match']}"
    )

    print(
        f"Study Type Match: "
        f"{result['study_type_match']}"
    )

    print(
        f"Decision: "
        f"{result['decision']}"
    )

    print(
        f"Confidence: "
        f"{result['confidence']}"
    )

    print(
        f"Reason: "
        f"{result['reason']}"
    )


    print("\n" + "=" * 60)
    print("MODEL 2 TEST SUCCESSFUL")
    print("=" * 60)


except Exception as error:

    print("\n" + "=" * 60)
    print("MODEL 2 TEST FAILED")
    print("=" * 60)

    print(
        type(error).__name__
    )

    print(error)