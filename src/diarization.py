import json
import shutil
import subprocess

from pathlib import Path
from utils import get_cwd
from omegaconf import OmegaConf
from nemo.utils import logging
logging.setLevel(logging.ERROR)
from nemo.collections.asr.models.msdd_models import NeuralDiarizer
from translation import translate

temp_dir = Path(get_cwd() + "/data/temp/")


def convert_to_mono(input_path: Path, output_path: Path) -> Path:
    """
    Convert a given input file to a mono wav file.

    :param input_path:
        The input file path.
    :param output_path:
        The output file path.
    :return:
        The updated output file path.
    """
    output_path = output_path / "mono_file.wav"
    
    # Ffmpeg command:
    command = f'ffmpeg -y -i "{input_path}" -ac 1 "{output_path}" -loglevel error'

    # Convert file to mono:
    subprocess.run(command)

    return output_path


def nemo_diarization(file_path: Path) -> list:
    """
    Manage the speaker diarization of Nvidia NeMo.

    :param file_path:
        The input file path.
    :return:
        The speaker diarization result.
    """
    print("Diarizing speakers...")

    # Create temp directory and convert input file to mono:
    temp_dir.mkdir(parents=True, exist_ok=True)
    output_path = convert_to_mono(file_path, temp_dir)

    # Prepare config data:
    meta = {
        'audio_filepath': f'{output_path}', 
        'offset': 0, 
        'duration': None, 
        'label': 'infer', 
        'text': '-', 
        'rttm_filepath': None, 
        'uem_filepath' : None
    }
    with open(temp_dir / 'input_manifest.json','w', encoding='utf-8') as manifest:
        json.dump(meta, manifest)
        manifest.write('\n')

    config = OmegaConf.load(get_cwd() + "/data/configs/nemo/diar_infer_telephonic.yaml")
    config.diarizer.manifest_filepath = str(temp_dir / 'input_manifest.json')
    config.diarizer.out_dir = str(temp_dir)

    # Run diarization:
    msdd_model = NeuralDiarizer(cfg=config)
    msdd_model.diarize()

    return get_speaker_list(output_path.stem)


def get_speaker_list(file_name: str) -> list:
    """
    Read in the rttm file of the NeMo diarization and return a list of segments.

    :param file_name:
        The rttm file name.
    :return:
        A list of segments containing the speakers.
    """
    nemo_result = []

    # Convert nemo rttm file to list of segments:
    with open(f"{temp_dir}/pred_rttms/{file_name}.rttm", "r",  encoding="utf-8") as rttm:
        lines = rttm.readlines()

        for line in lines:
            parts = line.split(" ")
            speaker = parts[11].replace("_", " ").capitalize()
            segment = {
                "end": float(parts[5]) + float(parts[8]),
                "speaker": speaker
            }

            if nemo_result:
                # Get previous segment:
                previous = nemo_result[-1]

                if speaker == previous["speaker"]:
                    # Update end timestamp to merge both segments to one:
                    previous["end"] = float(parts[5]) + float(parts[8])
                else:
                    # Expand both border timestamps to fill gap:
                    end = previous["end"]
                    start = float(parts[5])
                    mid = end + ((start - end) / 2)

                    previous["end"] = mid
                    segment["start"] = mid
                    nemo_result.append(segment)
            else:
                # if first segment:
                segment["start"] = 0.0
                nemo_result.append(segment)

    # Cleanup temp files:
    shutil.rmtree(temp_dir)

    return nemo_result


def segment_speaker_mapping(whisper_result: dict, nemo_result: list, target_language: str) -> dict:
    """
    Map the speakers and the transcription result.

    :param whisper_result:
        The transcription result of Whisper.
    :param nemo_result:
        The speaker diarization result of NeMo.
    :param target_language:
        The target language of the final result.
    :return:
        The mapped result containing the speakers and the text.
    """

    # Loop through whisper segments:
    for whisper_segment in whisper_result["segments"]:
        
        # Calculate mean:
        start = float(whisper_segment["start"])
        end = float(whisper_segment["end"])
        mean = (start + end) / 2

        # Search for a matching nemo segment:
        for nemo_segment in nemo_result:
            if nemo_segment["start"] <= mean <= nemo_segment["end"]:
                name, number = nemo_segment["speaker"].split(" ")
                break
        else:
            # Take last speaker if no matching segment was found:
            name, number = nemo_result[-1]["speaker"].split(" ")
            
        whisper_segment["speaker"] = f"{translate(name, target_language)} {number}"

    return whisper_result