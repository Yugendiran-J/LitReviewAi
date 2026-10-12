from app.services.ollama_service import generate_text


def main():
    print("Testing local Ollama connection...")

    try:
        result = generate_text(
            "Reply with exactly: LitReviewAI local Ollama connection successful."
        )

        print("\nOllama response:")
        print(result)

    except Exception as error:
        print("\nOllama connection failed:")
        print(type(error).__name__)
        print(error)
        raise


if __name__ == "__main__":
    main()