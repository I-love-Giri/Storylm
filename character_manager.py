import json


def get_characters(story_plan):
    story_plan_json = json.dumps(story_plan, indent=2)
    return story_plan_json["characters"]
