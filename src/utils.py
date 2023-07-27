import random
import shutil

from pytube import YouTube
from pathlib import Path


def get_cwd() -> str:
    """
    Get the current working directory.

    :return:
        The current working directory.
    """
    return str(Path(__file__).parent.parent.resolve())


def check_files():
    """
    Check if files required by PANNs inference exist.
    """
    checkpoint_path = f"{Path.home()}/panns_data/Cnn14_DecisionLevelMax_mAP=0.385.pth"
    class_labels_path = f"{Path.home()}/panns_data/class_labels_indices.csv"

    # Copy files if they don't exist:
    if not Path(checkpoint_path).is_file() or not Path(class_labels_path).is_file():
        Path(f"{Path.home()}/panns_data/").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f"{get_cwd()}/data/configs/panns_inference/Cnn14_DecisionLevelMax_mAP=0.385.pth", checkpoint_path)
        shutil.copyfile(f"{get_cwd()}/data/configs/panns_inference/class_labels_indices.csv", class_labels_path)

    return checkpoint_path


def convert_to_python(value: str | None) -> bool | str | None:
    """
    Convert received form data to python value.

    :param value:
        The value to be converted.
    :return:
        The python value.
    """
    if value == 'on':
        return True
    elif value == None:
        return False
    elif value == 'None':
        return None
    else:
        return value


def random_color() -> str:
    """
    Generate a random html color.

    :return:
        The html color.
    """
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    
    return f"#{r:02x}{g:02x}{b:02x}"


def convert_color(html_color: str) -> str:
    """
    Convert a html color to hexadecimal format.

    :param html_color:
        The html color.
    :return:
        The hexadecimal color.
    """
    html_color = html_color.lstrip('#')

    red = int(html_color[0:2], 16)
    green = int(html_color[2:4], 16)
    blue = int(html_color[4:6], 16)

    return f"&H{blue:02X}{green:02X}{red:02X}&"
    

def sec_to_vtt(seconds: float | str) -> str:
    """
    Convert seconds to vtt timestamp.

    :param seconds:
        The seconds value.
    :return:
        The corresponding timestamp.
    """
    if isinstance(seconds, float):
        hh, mm, ss = sec_to_hhmmss(seconds)
        return f'{hh:0>2.0f}:{mm:0>2.0f}:{ss:0>6.3f}'
    else:
        return seconds


def sec_to_srt(seconds: float | str) -> str:
    """
    Convert seconds to srt timestamp.

    :param seconds:
        The seconds value.
    :return:
        The corresponding timestamp.
    """
    return sec_to_vtt(seconds).replace(".", ",")


def sec_to_ass(seconds: float | str) -> str:
    """
    Convert seconds to ass timestamp.

    :param seconds:
        The seconds value.
    :return:
        The corresponding timestamp.
    """
    if isinstance(seconds, float):
        hh, mm, ss = sec_to_hhmmss(seconds)
        return f'{hh:0>1.0f}:{mm:0>2.0f}:{ss:0>2.2f}'  
    else:
        return seconds


def sec_to_hhmmss(seconds: float) -> tuple[float, float, float]:
    """
    Convert seconds to hhmmss format.

    :param seconds:
        The seconds value.
    :return:
        The values for hh, mm and ss.
    """
    mm, ss = divmod(seconds, 60)
    hh, mm = divmod(mm, 60)
    return hh, mm, ss


def get_mimetype(format: str) -> str:
    """
    Get the mimetype of given output format.

    :param format:
        The given output format.
    :return:
        The corresponding mimetype.
    """
    match format:
        case 'vtt':
            return 'text/vtt'
        case 'pdf':
            return 'application/pdf'
        case 'mp4':
            return 'video/mp4'
        case 'mkv':
            return 'video/x-matroska'
        case 'srt' | 'txt':
            return 'text/plain' 


def download_video(url: str, output_dir: Path) -> Path:
    """
    Download a youtube video with a valid url.

    :param url:
        The youtube watch url.
    :param output_dir:
        The output directory path.
    """
    print("Downloading Youtube video...")

    # Set video file name:
    try:
        file_name = "youtube" + url.split("=")[1] + ".mp4"
    except:
        file_name = "youtube" + url[-8:] + ".mp4"

    # Try to download the video:
    try:
        stream = YouTube(url).streams.get_highest_resolution()
        stream.download(output_dir, file_name)
        print("100% Complete")
        return output_dir / file_name
    except Exception as e:
        print(e)
        raise Exception("Youtube download failed")


def generate_table_json(extention: str, result: dict) -> list:
    """
    Generate a json from the transcription result for the editor html table.

    :param extention:
        The selected file extention.
    :param result:
        The transcription result.
    :return:
        A list of json elements for each segment in the result.
    """
    # Create a json object for each table row:
    table_rows = []
    for i, segment in enumerate(result['segments']):
        table_row = {}

        # Create entries depending on selected extention:
        match extention:
            case ".srt":
                table_row['index'] = i
                table_row['start'] = sec_to_srt(segment['start'])
                table_row['end'] = sec_to_srt(segment['end'])
                table_row['color'] = segment['color']
                table_row['size'] = segment['size']

            case ".vtt":
                table_row['index'] = i
                table_row['start'] = sec_to_vtt(segment['start'])
                table_row['end'] = sec_to_vtt(segment['end'])
                table_row['align'] = segment['align']

            case ".ass" | ".mp4" | ".mkv":
                table_row['index'] = i
                table_row['start'] = sec_to_ass(segment['start'])
                table_row['end'] = sec_to_ass(segment['end'])
                table_row['color'] = segment['color']
                table_row['size'] = segment['size']
                table_row['align'] = segment['align']
            
        if "speaker" in segment:
            table_row['speaker'] = segment['speaker']

        table_row['text'] = segment['text'].strip()

        table_rows.append(table_row)

    return table_rows