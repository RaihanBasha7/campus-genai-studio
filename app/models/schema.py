from pydantic import BaseModel
from typing import List

class EventRequest(BaseModel):
    idea: str

class EventResponse(BaseModel):
    event_name: str
    tasks: List[str]
    timeline: str