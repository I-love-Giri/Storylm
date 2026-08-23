import json

from config import client
from narrator_agent import create_narration_script

sample_story = """
Mara entered the dark cabin.

"Did you hear that?" Eli whispered.

A cold wind shook the windows.
"""

narration_script = create_narration_script(
    client,
    sample_story,
)

print(json.dumps(narration_script, indent=2))
