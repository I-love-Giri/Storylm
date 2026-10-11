import subprocess
import tempfile
import wave

from pathlib import Path


def generate_audio(voice_script, output_path):
    scenes = voice_script.get("scenes", [])

    if not scenes:
        raise ValueError("Voice script contains no scenes.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        scene_files = []

        for index, scene in enumerate(scenes):
            text = scene.get("text", "").strip()

            if not text:
                continue

            speed = scene.get("speed", 1.0)

            # Convert speech speed into a macOS speech rate.
            rate = int(175 * speed)
            rate = max(80, min(rate, 350))

            aiff_path = temp_path / f"scene_{index}.aiff"
            wav_path = temp_path / f"scene_{index}.wav"

            # Step 1: Generate speech using macOS TTS.
            subprocess.run(
                [
                    "say",
                    "-r",
                    str(rate),
                    "-o",
                    str(aiff_path),
                    text,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            if not aiff_path.exists():
                raise RuntimeError(f"Speech file was not created for scene {index}.")

            # Step 2: Convert AIFF to WAV.
            subprocess.run(
                [
                    "/usr/bin/afconvert",
                    "-f",
                    "WAVE",
                    "-d",
                    "LEI16",
                    str(aiff_path),
                    str(wav_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            if not wav_path.exists():
                raise RuntimeError(f"WAV file was not created for scene {index}.")

            # Keep the WAV path and pause for final composition.
            scene_files.append((wav_path, scene.get("pause_after", 0)))

            print(f"Generated audio for scene {index + 1}/{len(scenes)}")

        if not scene_files:
            raise ValueError("No scenes contained text to speak.")

        # Read the audio format from the first scene.
        with wave.open(str(scene_files[0][0]), "rb") as first:
            audio_params = first.getparams()

        # Step 3: Combine all scenes into one WAV file.
        with wave.open(str(output_path), "wb") as final_audio:
            final_audio.setparams(audio_params)

            for wav_path, pause_after in scene_files:
                with wave.open(str(wav_path), "rb") as scene_audio:
                    scene_params = scene_audio.getparams()

                    if (
                        scene_params.nchannels != audio_params.nchannels
                        or scene_params.sampwidth != audio_params.sampwidth
                        or scene_params.framerate != audio_params.framerate
                        or scene_params.comptype != audio_params.comptype
                    ):
                        raise ValueError(f"Audio format mismatch in {wav_path.name}.")

                    final_audio.writeframes(
                        scene_audio.readframes(scene_audio.getnframes())
                    )

                # Add silence between scenes.
                pause_after = max(
                    0,
                    min(float(pause_after), 3),
                )

                silence_frames = int(audio_params.framerate * pause_after)

                silence = (
                    b"\x00"
                    * audio_params.nchannels
                    * audio_params.sampwidth
                    * silence_frames
                )

                final_audio.writeframes(silence)

    print(f"\nAudio saved successfully: {output_path}")

    return output_path
