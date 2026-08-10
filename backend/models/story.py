from pydantic import BaseModel
from typing import List , Optional
from backend.models.character import Character
from backend.models.scene import Scene

class StoryState(BaseModel):
    story_id: str
    title: str
    genre: str

    current_chapter: int = 1
    current_scene: Optional[str] = None

    characters: List[Character] = []
    locations: List[str] = []
    objects: List[str] = []
    events: List[str] = []
    relationships: List[str] = []

    plot_summary: str = ""
    chapter_summaries: List[str] = []

    current_scene_state: Optional[Scene] = None