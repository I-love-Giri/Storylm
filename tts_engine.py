import asyncio
import hashlib
import shutil
import tempfile

from pathlib import Path

import edge_tts
from pydub import AudioSegment

# Default voice for narration.
NARRATOR_VOICE = "en-US-AndrewNeural"

# Voices available for character dialogue.
CHARACTER_VOICES = [
    "en-US-AriaNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-EricNeural",
    "en-US-AvaNeural",
    "en-US-BrianNeural",
    "en-US-EmmaNeural",
]

# Optional overrides for important characters.
# Add your character names here when needed.
CHARACTER_VOICE_MAP = {
    "Alex": "en-US-GuyNeural",
    "Sarah": "en-US-AriaNeural",
}

# Convert Voice Director pitch labels into Edge TTS pitch.
PITCH_MAP = {
    "low": "-20Hz",
    "slightly_low": "-10Hz",
    "normal": "+0Hz",
    "slightly_high": "+10Hz",
    "high": "+20Hz",
}


def get_voice(scene):
    """Select a consistent voice based on the scene speaker."""

    speaker = str(scene.get("speaker", "NARRATOR")).strip()

    if speaker.upper() == "NARRATOR":
        return NARRATOR_VOICE

    # Allow manually configured character voices.
    if speaker in CHARACTER_VOICE_MAP:
        return CHARACTER_VOICE_MAP[speaker]

    # Stable mapping: the same character name gets the same voice.
    character_hash = hashlib.sha256(speaker.casefold().encode("utf-8")).hexdigest()

    voice_index = int(character_hash, 16) % len(CHARACTER_VOICES)

    return CHARACTER_VOICES[voice_index]


def get_pitch(scene):
    """Convert the Voice Director's pitch label to Edge TTS format."""

    pitch = scene.get("pitch", "normal")

    return PITCH_MAP.get(pitch, "+0Hz")


async def generate_scene_audio(scene, output_path):
    """Generate audio for one scene."""

    text = str(scene.get("text", "")).strip()

    if not text:
        return False

    voice = get_voice(scene)

    # Voice Director speed: 1.0 means normal speed.
    speed = float(scene.get("speed", 1.0))
    speed = max(0.5, min(speed, 2.0))

    rate_percentage = round((speed - 1.0) * 100)
    rate = f"{rate_percentage:+d}%"

    # Voice Director pitch: low, normal, high, etc.
    pitch = get_pitch(scene)

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
    )

    await communicate.save(str(output_path))

    return True


async def generate_all_scenes(scenes, temp_path):
    """Generate all scene audio sequentially in one event loop."""

    generated_scenes = []

    for index, scene in enumerate(scenes):
        if not str(scene.get("text", "")).strip():
            continue

        audio_path = temp_path / f"scene_{index}.mp3"

        await generate_scene_audio(scene, audio_path)

        generated_scenes.append((scene, audio_path))

        speaker = scene.get("speaker", "NARRATOR")
        voice = get_voice(scene)

        print(
            f"Scene {index + 1}/{len(scenes)} | "
            f"Speaker: {speaker} | "
            f"Voice: {voice} | "
            f"Speed: {scene.get('speed', 1.0)} | "
            f"Pitch: {scene.get('pitch', 'normal')}"
        )

    return generated_scenes


def generate_audio(voice_script, output_path):
    """Generate a complete story chapter as a WAV file."""

    scenes = voice_script.get("scenes", [])

    if not scenes:
        raise ValueError("Voice script contains no scenes.")

    if shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg was not found. Please install FFmpeg first.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        generated_scenes = asyncio.run(generate_all_scenes(scenes, temp_path))

        if not generated_scenes:
            raise ValueError("No scenes contained text to speak.")

        final_audio = AudioSegment.empty()

        for scene, audio_path in generated_scenes:
            scene_audio = AudioSegment.from_file(
                str(audio_path),
                format="mp3",
            )

            final_audio += scene_audio

            pause_after = float(scene.get("pause_after", 0))
            pause_after = max(0, min(pause_after, 3))

            if pause_after > 0:
                silence = AudioSegment.silent(
                    duration=int(pause_after * 1000),
                    frame_rate=24000,
                )

                final_audio += silence

        final_audio.export(
            str(output_path),
            format="wav",
        )

    print(f"\nAudio saved successfully: {output_path}")

    return output_path
