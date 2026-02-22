from pydantic import BaseModel, Field, field_validator
from typing import List


class EventSchema(BaseModel):
    """
    Structured output schema for an AI-generated campus event.
    Validated against Ollama LLM JSON response.
    """

    event_name: str = Field(..., min_length=3, description="Name of the event")
    description: str = Field(..., min_length=10, description="Brief description of the event")
    target_audience: str = Field(..., description="Who this event is intended for")
    agenda: List[str] = Field(..., min_length=1, description="List of agenda items")
    resources_required: List[str] = Field(..., min_length=1, description="Resources needed")
    execution_steps: List[str] = Field(..., min_length=1, description="Step-by-step execution plan")

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("agenda", "resources_required", "execution_steps", mode="before")
    @classmethod
    def list_must_not_be_empty(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("Field must contain at least one item.")
        return v

    @field_validator("event_name", "description", "target_audience", mode="before")
    @classmethod
    def string_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field must not be blank.")
        return v.strip()

    # ── Config ────────────────────────────────────────────────────────────────

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_name": "AI Sustainability Hackathon",
                "description": "A hackathon focused on building AI solutions for sustainability challenges.",
                "target_audience": "Engineering students interested in AI and environment",
                "agenda": [
                    "Opening ceremony",
                    "Problem statement reveal",
                    "Hackathon begins",
                    "Mentorship session",
                    "Final presentations",
                    "Award ceremony"
                ],
                "resources_required": [
                    "Venue with projectors",
                    "High-speed WiFi",
                    "Domain expert judges",
                    "Prizes and certificates"
                ],
                "execution_steps": [
                    "Finalize and book venue",
                    "Design event poster and marketing material",
                    "Announce event on campus channels",
                    "Open registrations via Google Form",
                    "Shortlist teams",
                    "Conduct event and collect feedback"
                ]
            }
        }
    }