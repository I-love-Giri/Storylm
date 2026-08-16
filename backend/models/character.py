from pydantic import BaseModel, Field
from typing import List, Dict , Optional

class Character(BaseModel):
    id: str
    name: str

    personality: List[str] = []
    goals: List[str] = []
    fears: List[str] = []

    relationships: Dict[str, str] = {}

    location: Optional[str] = None
    health: str = "healthy"
    inventory: List[str] = []

    voice_id: Optional[str] = None