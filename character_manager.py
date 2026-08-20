def get_characters(story_plan):
    return story_plan["characters"]


def find_character(characters, name):
    for character in characters:
        if character["name"] == name:
            return character

    return None
