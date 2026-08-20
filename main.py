from character_manager import get_characters
from story_generator import generate_story
from config import client
from story_memory import update_memory
from story_planner import create_story_plan
import json


def get_story_idea():
    story_idea = input("What kind of story do you want? ")
    return story_idea


if __name__ == "__main__":
    story_idea = get_story_idea()
    story_plan = create_story_plan(client, story_idea)

    characters = get_characters(story_plan)

    """for character in characters:
        print("Name: ", character["name"])
        print("Role: ", character["role"])
        print("Description: ", character["description"])
        print()"""

    story = generate_story(client, story_plan, characters)
    memory = update_memory(client, story, characters)
    memory = json.loads(memory)

    """print("\n--- YOUR STORY ---\n")
    print(story)"""

    print("\n--- MEMORY TYPE ---\n")
    print(type(memory))

    print("\n--- UPDATED MEMORY ---\n")
    print(memory)

    print("\n--- FIRST CHARACTER ---")
    print(memory[0])
