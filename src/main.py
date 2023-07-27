import stable_whisper

from pathlib import Path
from utils import random_color
from translation import translate_segments, source_languages, target_languages
from diarization import nemo_diarization, segment_speaker_mapping
from sound_detection import sound_event_detection


def main(input_path: Path, whisper_model: str, source_language: str | None, target_language: str | None, diarization: bool, sound_detection: bool, output_format: str) -> tuple[dict, str, str]:
    """
    Manage the entire transcription process.

    :param input_path:
        The input file path.
    :param whisper_model:
        The whisper model.
    :param source_language:
        The source language.
    :param target_language:
        The target language.
    :param diarization:
        Whether the speaker diarization should be executed.
    :param sound_detection:
        Whether the sound event detection should be executed.
    :param output_format:
        The output format.
    :return:
        The transcription result, server message and updated target language.
    """
    message = 'success'

    # Execute the transcription of Whisper and update languages:
    whisper_result = transcribe_audio(input_path, whisper_model, source_language)
    if source_language == None: 
        source_language = whisper_result['language'].upper()
    if target_language == None:
        target_language = source_language


    if source_language not in target_language:
        # Execute the translation of DeepL:
        if source_language in source_languages and target_language in target_languages:
            whisper_result = translate_segments(whisper_result, source_language=source_language, target_language=target_language)
        else:
            message = 'Diese Sprache wird von DeepL Translator nicht unterstützt. Deine Datei wurde nicht übersetzt.'

    
    if diarization:
        # Execute the speaker diarization of Nvidia NeMo and merge results:
        nemo_result = nemo_diarization(input_path)
        result = segment_speaker_mapping(whisper_result, nemo_result, target_language)
    else:
        result = whisper_result

    
    if sound_detection:
        # Execute the sound event detection of PANNs inference:
        sed_result = sound_event_detection(input_path, diarization, target_language)
        
        # Merge and sort result:
        result['segments'] += sed_result
        result['segments'] = sorted(result['segments'], key=lambda x: x['start'])

    return set_style(result, output_format), message, target_language


def transcribe_audio(file_path: Path, whisper_model: str, language: str | None) -> dict:
    """
    Manage the transcription of Whisper.

    :param file_path:
        The input file path.
    :param whisper_model:
        The pretrained whisper model.
    :param language:
        The source language of the audio file.
    :return:
        The transcription result.
    """
    print("Transcribing audio...")

    if isinstance(language, str):
        language = language.lower()

    # Load model and transcribe audio:
    model = stable_whisper.load_model(whisper_model)
    result = model.transcribe(str(file_path), regroup="sp=./?/!+1_sl=80", language=language, verbose=False, fp16=False)

    return result.to_dict()


def set_style(result: dict, output_format: str) -> dict:
    """
    Set the subtitle style options depending on the output format.

    :param result:
        The transcription result.
    :param output_format:
        The output format.
    :return:
        The updated transcription result.
    """
    colors = {}
    # Set color, size and align for each segment:
    for segment in result['segments']:
        if 'speaker' in segment:
            # Generate random colors:
            speaker = segment['speaker']
            if speaker in colors:
                segment['color'] = colors[speaker]
            else:
                color = random_color()
                segment['color'] = color
                colors[speaker] = color
        else:
            segment['color'] = "#f0f0f0"

        if output_format == "srt":
            segment['size'] = "50"
        else:
            segment['size'] = "16"

        text = segment['text'].strip()
        if text.startswith("(") and text.endswith(")"):
            segment['align'] = "8"
        else:
            segment['align'] = "2"

    return result