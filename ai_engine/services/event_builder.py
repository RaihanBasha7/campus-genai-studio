import json
import logging
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
from ai_engine.schemas.event_schema import EventSchema
from ai_engine.services.prompt_loader import load_prompt
import os
MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral:7b-instruct-q4_K_M")

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral:7b-instruct-q4_K_M"
REQUEST_TIMEOUT = 120  # seconds — LLMs can be slow on first load

def _strip_markdown_fences(text: str) -> str:
    """
    Some LLMs wrap JSON in markdown code fences even when told not to.
    e.g.:  ```json { ... } ```
    This strips those fences so json.loads() can parse cleanly.
    """
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Remove first line (```json or ```) and last line (```)
        lines = lines[1:] if lines[0].startswith("```") else lines
        lines = lines[:-1] if lines[-1].strip() == "```" else lines
        text = "\n".join(lines).strip()
    return text

def generate_event(idea: str) -> EventSchema:
    """
    Generate a structured campus event from a raw idea string.

    Args:
        idea: A plain-text description of the event idea.

    Returns:
        A validated EventSchema instance.

    Raises:
        ConnectionError: If Ollama is not running or unreachable.
        ValueError: If Ollama returns unparseable or schema-invalid JSON.
        RuntimeError: For any unexpected Ollama API failure.
    """
    logger.info(f"Generating event for idea: '{idea}'")

    # Step 1: Load and render prompt
    prompt = load_prompt("event_builder.txt", idea)

    # Step 2: Build request payload
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,   # Lower = more deterministic JSON output
            "top_p": 0.9
        }
    }

    # Step 3: Call Ollama with proper error handling
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
            raise
        logger.warning("Retrying Ollama request due to timeout...")
     except ConnectionError:
        raise ConnectionError(
            "Cannot connect to Ollama. Make sure it is running:\n"
            "  $ ollama serve\n"
            f"  Expected at: {OLLAMA_URL}"
        )
     except Timeout:
        raise TimeoutError(
            f"Ollama request timed out after {REQUEST_TIMEOUT}s. "
            "The model may still be loading — try again."
        )
     except RequestException as e:
        raise RuntimeError(f"Ollama API request failed: {e}")

    # Step 4: Extract raw text from Ollama response
    try:
        raw_text = response.json()["response"]
    except (KeyError, json.JSONDecodeError) as e:
        raise RuntimeError(
            f"Unexpected Ollama response format: {e}\n"
            f"Raw response: {response.text[:500]}"
        )

    logger.debug(f"Raw Ollama response:\n{raw_text}")

    # Step 5: Strip markdown fences (LLMs sometimes add them despite instructions)
    cleaned_text = _strip_markdown_fences(raw_text)

    # Step 6: Parse JSON
    try:
        parsed_json = json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Ollama returned invalid JSON: {e}\n"
            f"Cleaned text received:\n{cleaned_text[:500]}"
        )

    # Step 7: Validate against Pydantic schema
    try:
        event = EventSchema(**parsed_json)
    except Exception as e:
        raise ValueError(
            f"AI output did not match expected EventSchema: {e}\n"
            f"Parsed JSON: {json.dumps(parsed_json, indent=2)}"
        )

    logger.info(f"Successfully generated event: '{event.event_name}'")
    return event