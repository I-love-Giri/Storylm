import json
from character_manager import get_characters
from emotion_analyzer import analyze_emotions
from story_generator import generate_story
from config import client, gemini_client
from story_memory import update_memory
from story_planner import create_story_plan
from narrator_agent import create_narration_script
from story_storage import (
    create_story_folder,
    list_saved_stories,
    load_story_state,
    save_chapter,
    save_memory,
    save_story_setup,
    save_narration_script,
)


def get_story_idea():
    return input("What kind of story do you want? ")


def get_story_mode():
    print("\n1. Start a new story")
    print("2. Continue a saved story")

    while True:
        choice = input("Enter your choice (1 or 2):")
        if choice in ["1", "2"]:
            return choice
        print("Please enter 1 or 2.")


if __name__ == "__main__":

    mode = get_story_mode()

    if mode == "1":
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

    else:
        saved_stories = list_saved_stories()

        if not saved_stories:
            print("\nNo saved stories found.")
            raise SystemExit

        print("\nSaved stories:")

        for index, folder in enumerate(saved_stories, start=1):
            print(f"{index}. {folder.name}")

        while True:
            choice = input("\nChoose a story number: ")

            if choice.isdigit():
                selected_index = int(choice) - 1

                if 0 <= selected_index < len(saved_stories):
                    story_folder = saved_stories[selected_index]
                    break

            print("Please enter a valid story number.")

        story_plan, characters, memory, chapter = load_story_state(story_folder)

        print(f"\nContinuing: {story_folder.name}")
        print(f"Starting from Chapter {chapter}")

    while True:
        story = generate_story(
            client,
            story_plan,
            characters,
            chapter,
            memory,
        )

        print(f"\n--- CHAPTER {chapter} ---\n")
        print(story)

        memory = update_memory(
            client,
            story,
            characters,
            memory,
        )

        save_chapter(story_folder, chapter, story)
        save_memory(story_folder, memory)

        print("\n--- UPDATED MEMORY ---\n")
        print(memory)
        try:
            narration_script = create_narration_script(
                gemini_client,
                story,
            )

            save_narration_script(
                story_folder,
                chapter,
                narration_script,
            )

            print("\nNarration script saved.")

            emotion_script = analyze_emotions(
                gemini_client,
                narration_script,
            )

            print("\n--- EMOTION ANALYSIS ---\n")
            print(json.dumps(emotion_script, indent=2))

        except RuntimeError as error:
            print(f"\nNarration script was not created: {error}")

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
