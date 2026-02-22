import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ai_engine.schemas.event_schema import EventSchema
from ai_engine.services.event_builder import generate_event


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["AI Engine"])


# ── Request / Response Models ─────────────────────────────────────────────────

class IdeaRequest(BaseModel):
    idea: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "idea": "College AI Hackathon focused on sustainability"
            }
        }
    }


class EventResponse(BaseModel):
    success: bool
    data: EventSchema


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post(
    "/generate-event",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a structured event from a raw idea",
    description=(
        "Accepts a plain-text campus event idea and returns a fully structured "
        "event plan validated against EventSchema, powered by a local Ollama LLM."
    )
)
def generate_event_route(request: IdeaRequest):
    if not request.idea.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field 'idea' must not be empty."
        )

    try:
        result: EventSchema = generate_event(request.idea)
        return EventResponse(success=True, data=result)

    except ConnectionError as e:
        logger.error(f"Ollama connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except TimeoutError as e:
        logger.error(f"Ollama timeout: {e}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(e)
        )
    except ValueError as e:
        logger.error(f"Validation/parsing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )