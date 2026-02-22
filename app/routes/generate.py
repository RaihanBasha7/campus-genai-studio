from fastapi import APIRouter
from app.models.schema import EventRequest, EventResponse
from app.services.generator import generate_event_plan

router = APIRouter()

@router.post("/generate", response_model=EventResponse)
def generate_plan(request: EventRequest):
    
    result = generate_event_plan(request.idea)
    
    return result