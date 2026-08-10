from pydantic import BaseModel
from typing import List , Optional


class Scene(BaseModel):
    id: str
    location: str

    characters: List[str] = []

    objective: Optional[str] = None
    conflict: Optional[str] = None
    emotion: Optional[str] = None

    events: List[str] = []
    outcome: Optional[str] = None
