import numpy as np
import librosa
import subprocess

from pathlib import Path
from utils import check_files
from translation import translate
# Check if required files exist:
checkpoint_path = check_files()
from panns_inference import SoundEventDetection, labels


def sound_event_detection(file_path: Path, speaker: bool, target_language: str) -> list:
    """
    Manage the sound event detection of PANNs inference.

    :param file_path:
        The input file path.
    :param speaker:
        Whether the speaker diarization has been executed.
    :param target_language:
        The target language of the transcription result.
    :return:
        The sound event detection result.
    """
    print("Detecting sound events...")


    # Get audio duration:
    global audio_duration
    cmd = f'ffprobe -i "{file_path}" -show_entries format=duration -loglevel error -of csv="p=0"'
    audio_duration = float(subprocess.run(cmd, capture_output=True, text=True).stdout)


    # Load audio and detect sound events:
    (audio, _) = librosa.core.load(str(file_path), sr=32000, mono=True)
    audio = audio[None, :]
        
    sed = SoundEventDetection(device='cpu', checkpoint_path=checkpoint_path, interpolate_mode='nearest')
    framewise_output = sed.inference(audio)


    # Get total frames:
    global total_frames
    total_frames = len(framewise_output[0])

    return frame_label_mapping(framewise_output[0], speaker, target_language)


def frame_label_mapping(framewise_output: list, speaker: bool, target_language: str) -> list:
    """
    Map the framewise output with labels and produce timestamp result.

    :param framewise_output:
        The framewise output of sound event detection.
    :param speaker:
        Whether the speaker diarization has been executed.
    :param target_language:
        The target language of the transcription result.
    """
    result = []

    currentLabel = labels[np.argmax(framewise_output[0])]
    start = 0
    # Loop through frames:
    for i in range(len(framewise_output)-1):
        index = np.argmax(framewise_output[i])
        label = labels[index]

        # Add label with timestamps if label changes:
        if label != currentLabel:
            # Add only non speech labels:
            if not "speech" in currentLabel.lower():
                segment = {"start": calculate_timestamp(start), "end": calculate_timestamp(i-1), "text": f"({translate(currentLabel, target_language)})"}

                if speaker:
                    segment['speaker'] = ""

                result.append(segment)

            start = i
            currentLabel = label

    return result


def calculate_timestamp(frame: int) -> float:
    """
    Calculate the timestamp of a given frame.

    :param frame:
        The given frame.
    :return:
        The corresponding timestamp in seconds.
    """
    return (frame * audio_duration) / total_frames