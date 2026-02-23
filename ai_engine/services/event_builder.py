import json
import logging
import os
import requests

from requests.exceptions import ConnectionError, Timeout, RequestException
from ai_engine.schemas.event_schema import EventSchema
from ai_engine.services.prompt_loader import load_prompt


logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral")
REQUEST_TIMEOUT = 120


def _strip_markdown_fences(text: str) -> str:
    """
    Some LLMs wrap JSON in markdown code fences.
    This removes them so json.loads works.
    """
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return text


def generate_event(idea: str) -> EventSchema:
    """
    Generate a structured campus event from a raw idea string.
    """

    logger.info(f"Generating event for idea: '{idea}'")

    # Load prompt template
    prompt = load_prompt("event_builder.txt", idea)

    payload = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "stream": False,
    "format": "json",
    "options": {
        "temperature": 0.2
    }
}

    # Retry logic
    for attempt in range(2):
        try:
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            break

        except Timeout:
            if attempt == 1:
                raise TimeoutError(
                    f"Ollama request timed out after {REQUEST_TIMEOUT}s."
                )
            logger.warning("Retrying Ollama request due to timeout...")

        except ConnectionError:
            raise ConnectionError(
                "Cannot connect to Ollama.\n"
                "Run this in terminal:\n"
                "ollama serve"
            )

        except RequestException as e:
            raise RuntimeError(f"Ollama API request failed: {e}")

    # Extract model output
    try:
        data = response.json()
        raw_text = data.get("message", {}).get("content", "")
    except (KeyError, json.JSONDecodeError) as e:
        raise RuntimeError(
            f"Unexpected Ollama response format: {e}\n"
            f"Raw response: {response.text[:500]}"
        )

    logger.debug(f"Raw Ollama response:\n{raw_text}")

    cleaned_text = _strip_markdown_fences(raw_text)

    # Convert to JSON
    try:
        print(response.text)
        parsed_json = json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Ollama returned invalid JSON: {e}\n"
            f"Model output:\n{cleaned_text[:500]}"
        )

    # Validate with schema
    try:
        event = EventSchema(**parsed_json)
    except Exception as e:
        raise ValueError(
            f"AI output doesn't match EventSchema: {e}\n"
            f"Parsed JSON:\n{json.dumps(parsed_json, indent=2)}"
        )

    logger.info(f"Successfully generated event: {event.event_name}")

    return event