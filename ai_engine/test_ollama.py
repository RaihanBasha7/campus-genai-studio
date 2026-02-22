import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    try:
        from ai_engine.services.event_builder import generate_event
    except ImportError as e:
        print(
            f"\n[IMPORT ERROR] {e}\n"
            "Make sure you are running from the project root:\n"
            "  cd campus-genai-studio\n"
            "  python -m ai_engine.test_ollama\n"
        )
        sys.exit(1)

    idea = "College AI Hackathon focused on sustainability"
    logger.info(f"Testing with idea: '{idea}'")

    try:
        result = generate_event(idea)

        print("\n" + "=" * 60)
        print("  AI ENGINE TEST — SUCCESS")
        print("=" * 60)
        print(json.dumps(result.model_dump(), indent=2))
        print("=" * 60 + "\n")

    except ConnectionError as e:
        print(f"\n[CONNECTION ERROR] Ollama not reachable:\n{e}")
        print("Fix: Run `ollama serve` in a separate terminal.\n")
        sys.exit(1)

    except ValueError as e:
        print(f"\n[VALIDATION ERROR] AI output was invalid:\n{e}\n")
        sys.exit(1)

    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()