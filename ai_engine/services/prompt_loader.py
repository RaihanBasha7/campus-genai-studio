from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(template_name: str, user_idea: str) -> str:
    """
    Load a prompt template by filename and inject the user idea.

    Args:
        template_name: Filename of the prompt template (e.g. 'event_builder.txt')
        user_idea: The raw idea string to inject into the template.

    Returns:
        Fully rendered prompt string ready to send to the LLM.

    Raises:
        FileNotFoundError: If the template file does not exist.
        ValueError: If user_idea is empty.
    """
    if not user_idea or not user_idea.strip():
        raise ValueError("user_idea must not be empty.")

    template_path = PROMPTS_DIR / template_name

    if not template_path.exists():
        raise FileNotFoundError(
            f"Prompt template not found: {template_path}\n"
            f"Expected location: {PROMPTS_DIR}"
        )

    template = template_path.read_text(encoding="utf-8")
    return template.replace("{{USER_IDEA}}", user_idea.strip())