import webbrowser
import json
import warnings
warnings.filterwarnings('ignore', '.*nopython.*', )

from utils import get_cwd, generate_table_json, download_video, convert_to_python, get_mimetype
from file_writer import create_output
from flask import Flask, render_template, send_file, jsonify, request
from main import main
from datetime import datetime
from pathlib import Path

app = Flask(__name__)


@app.errorhandler(404)
def not_found_error(error):
    """
    Handle 404 not found error.
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 internal server error.
    """
    response = jsonify(message='Auf dem Server ist ein Fehler aufgetreten. Bitte versuche es später nochmal.')
    response.status_code = 500
    return response


@app.route('/')
def index():
    """
    Render index template.
    """
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download_file():
    """
    Send file for download.
    """
    return send_file(output_path, mimetype=get_mimetype(output_format), as_attachment=True)


@app.route('/edit', methods=['POST'])
def open_editor():
    """
    Send table data and render editor template.
    """
    ext = output_path.suffix
    return render_template('editor.html', data=generate_table_json(ext, result))


@app.route('/save', methods=['POST'])
def save_changes():
    """
    Save user segment changes in result.
    """
    segments = []
    segment = {}
    i = '0'

    # Convert form data to segments:
    for name, value in request.form.items():
        key, index = name.split('-')

        if index != i:
            segments.append(segment)
            segment = {}
            i = index

        segment[key] = value

    segments.append(segment)

    # Update result and create new file:
    global output_path, result
    result['segments'] = segments
    output_path = create_output(result, input_path, output_format, language)

    return jsonify(message='success')


@app.route('/submit', methods=['POST'])
def handle_input():
    """
    Process user input data and prepare result.
    """
    # Collect user input data:
    global output_format
    output_format = request.form.get('output-format')
    source_language = request.form.get('source-language')
    target_language = request.form.get('target-language')
    whisper_model = request.form.get('whisper-model')
    speaker_diarization = request.form.get('speaker-diarization')
    sound_detection = request.form.get('sound-event-detection')
    json_data = request.form.get('json')
    active_tab = json.loads(json_data)['active_tab']

    print("Data successfully received...")

    
    # Convert some values to python:
    speaker_diarization = convert_to_python(speaker_diarization)
    sound_detection = convert_to_python(sound_detection)
    source_language = convert_to_python(source_language)
    target_language = convert_to_python(target_language)

    # Prepare output directory:
    global input_path, output_dir
    output_dir = Path(get_cwd() + f"/data/output/{datetime.now().strftime('%Y%m%d%H%M%S')}/")
    output_dir.mkdir(parents=True, exist_ok=True)

    if active_tab == "url-tab":
        # Download youtube video:
        youtube_url = request.form.get('youtube-url')
        input_path = download_video(youtube_url, output_dir)
    else:
        # Save input file:
        file = request.files['file']
        input_path = output_dir / file.filename
        file.save(input_path)


    # Run transcription process:
    global output_path, result, language
    result, message, language = main(input_path, whisper_model, source_language, target_language, speaker_diarization, sound_detection, output_format)

    # Write result to file:
    output_path = create_output(result, input_path, output_format, language)

    # Send response:
    response = jsonify(message=message)
    response.status_code == 200
    
    return response


if __name__ == '__main__':
    webbrowser.open("http://localhost:5000/")
    app.run(debug=False)