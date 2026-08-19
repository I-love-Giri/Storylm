from character_manager import get_characters
from story_generator import generate_story
from config import client
from story_planner import create_story_plan


def get_story_idea():
    story_idea = input("What kind of story do you want? ")
    return story_idea


if __name__ == "__main__":
    story_idea = get_story_idea()
    story_plan = create_story_plan(client, story_idea)

    characters = get_characters(story_plan)

    for character in characters:
        print("Name: ", character["name"])
        print("Role: ", character["role"])
        print("Description: ", character["description"])
        print()

    """story = generate_story(client, story_plan)
    print("\n--- YOUR STORY ---\n")
    print(story)"""
