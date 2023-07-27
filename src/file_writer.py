import os
import shutil
import subprocess

from utils import sec_to_srt, sec_to_vtt, sec_to_ass, convert_color
from pathlib import Path
from fpdf import FPDF


def create_output(result: dict, input_path: Path, output_format: str, language: str) -> Path:
    """
    Manage output file creation.

    :param result:
        The transcription result.
    :param input_path:
        The input file path.
    :param output_format:
        The output file format.
    :param language:
        The result language.
    :return:
        The output file path.
    """
    # Remove old directories:
    directories = sorted(input_path.parent.parent.iterdir(), key=os.path.getmtime)
    if len(directories) >= 10:
        num = len(directories) - 10
        for directory in directories[0:num]:
            shutil.rmtree(directory)

    # Process output format:
    match output_format:
        case 'srt':
            return write_to_srt(result, input_path)

        case 'vtt':
            return write_to_vtt(result, input_path)

        case 'ass':
            return write_to_ass(result, input_path)

        case 'txt':
            return write_to_txt(result, input_path)
        
        case 'pdf':
            return write_to_pdf(result, input_path)
        
        case 'mkv':
            return generate_soft_subtitled_video(result, input_path, language)

        case 'mp4':
            return generate_hard_subtitled_video(result, input_path)
        

def write_to_file(output_path: Path, content: str) -> Path:
    """
    Write content into a file.

    :param output_path:
        The output file path.
    :param content:
        The file content.
    :return:
        The output file path.
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(content)

    print("File created: " + output_path.name)
    return output_path


def write_to_srt(result: dict, output_path: Path) -> Path:
    """
    Write the transcription result into a srt file.

    :param result:
        The transcription result.
    :param output_path:
        The output file path.
    :return:
        The updated output file path.
    """
    # Change file extention and convert result to string:
    output_path = output_path.with_suffix(".srt")
    srt_content = "\n\n".join(segment_to_srt(s, i) for i, s in enumerate(result['segments']))

    return write_to_file(output_path, srt_content)


def write_to_vtt(result: dict, output_path: Path) -> Path:
    """
    Write the transcription result into a vtt file.

    :param result:
        The transcription result.
    :param output_path:
        The output file path.
    :return:
        The updated output file path.
    """
    # Change file extention and convert result to string:
    output_path = output_path.with_suffix(".vtt")
    vtt_content = "WEBVTT\n\n" + "\n\n".join(segment_to_vtt(s, i) for i, s in enumerate(result['segments']))

    return write_to_file(output_path, vtt_content)


def write_to_ass(result: dict, output_path: Path) -> Path:
    """
    Write the transcription result into an ass file.

    :param result:
        The transcription result.
    :param output_path:
        The output file path.
    :return:
        The updated output file path.
    """
    # Prepare additional ass content:
    styles = {'Name': 'Default', 'Fontname': 'Arial', 'Fontsize': '16', 'PrimaryColour': '&Hffffff',
              'SecondaryColour': '&Hffffff', 'OutlineColour': '&H0', 'BackColour': '&H0', 'Bold': '0',
              'Italic': '0', 'Underline': '0', 'StrikeOut': '0', 'ScaleX': '100', 'ScaleY': '100',
              'Spacing': '0', 'Angle': '0', 'BorderStyle': '1', 'Outline': '1', 'Shadow': '0',
              'Alignment': '2', 'MarginL': '10', 'MarginR': '10', 'MarginV': '10', 'Encoding': '0'}
    
    format_row = f"Format: {', '.join(map(str, styles.keys()))}"
    style_row = f"Style: {','.join(map(str, styles.values()))}"

    ass_content = f"[Script Info]\nScriptType: v4.00+\nPlayResX: 384\nPlayResY: 288\nScaledBorderAndShadow: yes\n\n" \
                  f"[V4+ Styles]\n{format_row}\n{style_row}\n\n" \
                  f"[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n\n"
    
    # Change file extention and convert result to string:
    output_path = output_path.with_suffix(".ass")
    ass_content += "\n".join(segment_to_ass(s, i) for i, s in enumerate(result['segments']))

    return write_to_file(output_path, ass_content)


def write_to_txt(result: dict, output_path: Path) -> Path:
    """
    Write the transcription result into a txt file.

    :param result:
        The transcription result.
    :param output_path:
        The output file path.
    :return:
        The updated output file path.
    """
    # Change file extention and convert result to string:
    output_path = output_path.with_suffix(".txt")
    txt_content = "\n".join(segment_to_txt(s) for s in result['segments'])

    return write_to_file(output_path, txt_content)


def write_to_pdf(result: dict, output_path: Path) -> Path:
    """
    Write the transcription result into a pdf file.

    :param result:
        The transcription result.
    :param output_path:
        The output file path.
    :return:
        The updated output file path.
    """
    # Change file extention:
    output_path = output_path.with_suffix(".pdf")

    # Prepare pdf:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.set_margin(25)

    # Create txt file:
    txt_path = write_to_txt(result, output_path)
    txt_file = open(txt_path, "r", encoding="utf-8")
    
    # Convert txt to pdf:
    pdf.write(10, txt=txt_file.read())
    txt_file.close()

    pdf.output(output_path)

    print("File created: " + output_path.name)
    return output_path


def generate_soft_subtitled_video(result: dict, input_path: Path, language: str) -> Path:
    """
    Generate a video with soft subtitles out of the transcription result and the input video.

    :param result:
        The transcription result.
    :param input_path:
        The input video file path.
    :param language:
        The result language.
    :return:
        The output video file path.
    """
    # Create ass file and prepare paths:
    ass_path = write_to_ass(result, input_path)
    output_path = input_path.parent / (input_path.stem + "_sub.mkv")

    print("Adding subtitles to video...")
    
    # Ffmpeg command:
    command = f'ffmpeg -y -i "{input_path}" -i "{ass_path}" -c copy -metadata:s:s:0 title=[{language}] "{output_path}" -loglevel error'

    # Create output file:
    subprocess.run(command)

    print("File created: " + output_path.name)
    return output_path


def generate_hard_subtitled_video(result: dict, input_path: Path) -> Path:
    """
    Generate a video with hard subtitles out of the transcription result and the input video.

    :param result:
        The transcription result.
    :param input_path:
        The input video file path.
    :return:
        The output video file path.
    """
    # Create ass file and prepare paths:
    ass_path = str(write_to_ass(result, input_path)).replace("\\", "/").split(":")[1]
    output_path = input_path.parent / (input_path.stem + "_sub.mp4")

    print("Adding subtitles to video...")

    # Ffmpeg command:
    command = f'ffmpeg -y -i "{input_path}" -vf "ass={ass_path}" "{output_path}" -loglevel error'

    # Create output file:
    subprocess.run(command)

    print("File created: " + output_path.name)
    return output_path


def segment_to_srt(segment: dict, index: int) -> str:
    """
    Convert a segment of the transcription result to a srt string.

    :param segment:
        A segment of the transcription result.
    :param index:
        The index of the segment in the transcription result.
    :return:
        The corresponding srt string.
    """
    # Set speaker:
    speaker = f"[{segment['speaker']}]: " if 'speaker' in segment and segment['speaker'].strip() != "" else ""

    if 'color' in segment and 'size' in segment:
        # Set style:
        text = f'<font color="{segment["color"]}" size="{segment["size"]}">{speaker}{segment["text"].strip()}</font>'
    else:
        text = f"{speaker}{segment['text'].strip()}"

    return f"{index}\n" \
           f"{sec_to_srt(segment['start'])} --> {sec_to_srt(segment['end'])}\n" \
           f"{text}"


def segment_to_vtt(segment: dict, index: int) -> str:
    """
    Convert a segment of the transcription result to a vtt string.

    :param segment:
        A segment of the transcription result.
    :param index:
        The index of the segment in the transcription result.
    :return:
        The corresponding vtt string.
    """
    # Set speaker:
    speaker = f"[{segment['speaker']}]: " if 'speaker' in segment and segment['speaker'].strip() != "" else ""

    # Set style:
    if 'align' in segment:
        match segment['align']:
            case "2":
                style = "line:100%"
            case "5":
                style = "line:50%"
            case "8":
                style = "line:0%"
    else:
        style = ""

    return f"{index}\n" \
           f"{sec_to_vtt(segment['start'])} --> {sec_to_vtt(segment['end'])} {style}\n" \
           f"{speaker}{segment['text'].strip()}"


def segment_to_ass(segment: dict, index: int) -> str:
    """
    Convert a segment of the transcription result to an ass string.

    :param segment:
        A segment of the transcription result.
    :param index:
        The index of the segment in the transcription result.
    :return:
        The corresponding ass string.
    """
    # Set speaker:
    speaker = f"[{segment['speaker']}]: " if 'speaker' in segment and segment['speaker'].strip() != "" else ""

    if 'color' in segment and 'size' in segment and 'align' in segment:
        # Set style:
        style = "{" + f"\\c&{convert_color(segment['color'])}&\\fs{segment['size']}\\an{segment['align']}" + "}"
    else:
        style = ""

    return f"Dialogue: {index},{sec_to_ass(segment['start'])},{sec_to_ass(segment['end'])},Default,,0,0,0,,{style}{speaker}{segment['text'].strip()}"


def segment_to_txt(segment: dict) -> str:
    """
    Convert a segment of the transcription result to a txt string.

    :param segment:
        A segment of the transcription result.
    :return:
        The corresponding txt string.
    """
    # Set speaker:
    speaker = f"[{segment['speaker']}]: " if 'speaker' in segment and segment['speaker'].strip() != "" else ""

    return f"{speaker}{segment['text'].strip()}"