from character_manager import get_characters
from story_generator import generate_story
from config import client
from story_memory import update_memory
from story_planner import create_story_plan
import json


from character_manager import get_characters
from story_generator import generate_story
from config import client
from story_memory import update_memory
from story_planner import create_story_plan
from story_storage import (
    create_story_folder,
    save_chapter,
    save_memory,
    save_story_setup,
)


def get_story_idea():
    return input("What kind of story do you want? ")


if __name__ == "__main__":
    story_idea = get_story_idea()

    story_plan = create_story_plan(client, story_idea)
    characters = get_characters(story_plan)

    story_name = story_plan.get("title", story_idea)

    story_folder = create_story_folder(story_name)

    save_story_setup(
        story_folder,
        story_plan,
        characters,
    )

    memory = None

    chapter = 1

    while True:
        story = generate_story(client, story_plan, characters, chapter, memory)

        print(f"\n--- CHAPTER {chapter} ---\n")
        print(story)

        save_chapter(story_folder, chapter, story)

        memory = update_memory(client, story, characters, memory)

        save_memory(story_folder, memory)

        print("\n--- UPDATED MEMORY ---\n")
        print(memory)

        chapter += 1

        choice = input("\nGenerate another chapter? (y/n): ")

        if choice.lower() != "y":
            break

    """print("\n--- YOUR STORY ---\n")
    print(story)"""

    """print("\n--- MEMORY TYPE ---\n")
    print(type(memory))"""

    """print("\n--- UPDATED MEMORY ---\n")
    print(memory)

    print("\n--- FIRST CHARACTER ---")
    print(memory[0])"""
