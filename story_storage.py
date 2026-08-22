import json
import re
from datetime import datetime
from pathlib import Path

STORIES_FOLDER = Path("saved_stories")


def make_safe_folder_name(story_name):
    cleaned_name = story_name.lower().strip()

    # Letters/numbers ke alawa jo bhi ho—space, `!`, `?`, `-`—use `_` se replace karo.
    cleaned_name = re.sub(r"[^a-z0-9]+", "_", cleaned_name)

    # Agar end/start mein extra underscore bacha hai toh remove.
    cleaned_name = cleaned_name.strip("_")

    return cleaned_name or "untitled_story"


def create_story_folder(story_name):
    STORIES_FOLDER.mkdir(exist_ok=True)

    story_name = make_safe_folder_name(story_name)

    """  
    2026-08-21 14:30:05
            ↓
    20260821_143005
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    story_folder = STORIES_FOLDER / f"{story_name}_{timestamp}"

    """
    saved_stories
        /
    the_hills_20260821_143005
        ↓
    saved_stories/the_hills_20260821_143005
    
    """

    story_folder.mkdir()

    return story_folder


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:

        """
        json.dump() Python dictionary/list ko JSON format mein convert karke direct file mein likhta hai.
        """

        json.dump(data, f, indent=2, ensure_ascii=False)


"""
load_json() saved JSON ko wapas Python dictionary/list mein convert karega.

"""


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# ek helper function jo story ka plan aur characters ko JSON files mein save karega.
def save_story_setup(story_folder, story_plan, characters):
    save_json(story_folder / "story_plan.json", story_plan)
    save_json(story_folder / "characters.json", characters)


"""
saved_stories/
└── the_hills_20260821_143000/
    ├── story_plan.json
    └── characters.json
"""


# chapter save karenge—chapter_1.txt, chapter_2.txt, etc.


def save_chapter(story_folder, chapter_number, story):

    chapter_file = story_folder / f"chapter_{chapter_number}.txt"

    with open(chapter_file, "w", encoding="utf-8") as file:
        file.write(story)


# memory ko memory.json mein save karenge.


def save_memory(story_folder, memory):
    save_json(story_folder / "memory.json", memory)


"""
the_hills_20260821_143000/
├── story_plan.json
├── characters.json
├── memory.json
├── chapter_1.txt
├── chapter_2.txt
└── chapter_3.txt

"""


# saved story folders ki list nikalna—taaki user choose kar sake kaunsi old story continue karni hai

# Ab saved_stories ke andar jitni stories hain, unki list nikalte hain.


def list_saved_stories():
    STORIES_FOLDER.mkdir(exist_ok=True)

    return [folder for folder in STORIES_FOLDER.iterdir() if folder.is_dir()]


# load_story_state(). Ye old story ka plan, characters, memory load karega aur next chapter number calculate karega.


def load_story_state(story_folder):
    story_plan = load_json(story_folder / "story_plan.json")
    characters = load_json(story_folder / "characters.json")
    memory = load_json(story_folder / "memory.json")

    # Ye folder ke andar woh saari .txt files dhundega jinka naam chapter_ se start hota hai.
    chapter_files = list(story_folder.glob("chapter_*.txt"))

    chapter_number = len(chapter_files) + 1

    return story_plan, characters, memory, chapter_number
