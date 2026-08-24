"""NARRATOR_SCHEMA = {
    "name": "narration_script",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "scenes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "scene_type": {
                            "type": "string",
                            "enum": ["narration", "dialogue"],
                        },
                        "speaker": {"type": "string"},
                        "text": {"type": "string"},
                    },
                    "required": ["scene_type", "speaker", "text"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["scenes"],
        "additionalProperties": False,
    },
}"""

NARRATOR_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "scenes": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "scene_type": {
                        "type": "STRING",
                        "enum": ["narration", "dialogue"],
                    },
                    "speaker": {
                        "type": "STRING",
                    },
                    "text": {
                        "type": "STRING",
                    },
                },
                "required": [
                    "scene_type",
                    "speaker",
                    "text",
                ],
            },
        },
    },
    "required": ["scenes"],
}
