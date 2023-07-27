# Subtitle Generator
A website for AI-based transcript and subtitle generation including a small user editor using
- [Stable Whisper](https://github.com/jianfch/stable-ts) (which is a slight modification of [OpenAI Whisper](https://github.com/openai/whisper)) for audio transcription,
- [NVIDIA NeMo](https://github.com/NVIDIA/NeMo) for speaker diarization,
- [PANNs inferece](https://github.com/qiuqiangkong/panns_inference) for sound event detection,
- [DeepL Translator](https://github.com/DeepLcom/deepl-python) for translation,
- [FFmpeg](https://ffmpeg.org/) for video/audio editing,
- [Flask](https://github.com/pallets/flask) for webframework
- and [Bootstrap](https://getbootstrap.com/) for website CSS.

This application was developed as part of a bachelor thesis.

## Example
https://github.com/philipp821/subtitle-generator/assets/117348004/58167966-d641-46bc-9653-e36362c1cab3

More examples can be found [here](/data/examples/examples.md).

## Requirements
- Python 3.10.11 (Download [here](https://www.python.org/downloads/release/python-31011/))
- Microsoft Visual C++ 14.0 or greater (Download [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/))
- FFmpeg 6.0 or greater (Download [here](https://ffmpeg.org/download.html))
- DeepL API Key (Create a free account [here](https://www.deepl.com/pro-api?cta=header-pro-api))

## Setup
1. Clone repository:
```
git clone https://github.com/philipp821/subtitle-generator.git
```
2. Move into repository directory and create virtual environment:
```
python -m venv venv
```
3. Activate virtual environment:
```
venv\Scripts\activate
```
4. Install packages:
```
pip install Cython
pip install -r requirements.txt
python -m textblob.download_corpora lite
```
5. Download [pretrained model](https://zenodo.org/record/3987831/files/Cnn14_DecisionLevelMax_mAP%3D0.385.pth?download=1) for sound event detection and store it in:
```
\data\configs\panns_inference\Cnn14_DecisionLevelMax_mAP=0.385.pth
```
6. Put your DeepL API Key in a file named `deepl.key` and store it in root directory:
```
\deepl.key
```

## Usage
- Activate virtual environment if not already done:
```
venv\Scripts\activate
```
- Run the `webserver.py` file:
```
python src\webserver.py
```
- Enter `http://localhost:5000/` in your browser if it does not open by itself.
