import deepl

from utils import get_cwd
from textblob import TextBlob

# Get DeepL API key and available languages:
with open(get_cwd() + '/deepl.key', 'r') as key_file:
    DEEPL_KEY = key_file.read()
translator = deepl.Translator(DEEPL_KEY)
source_languages = [lang.code for lang in translator.get_source_languages()]
target_languages = [lang.code for lang in translator.get_target_languages()]


def translate(string: str, target_language: str) -> str:
    """
    Translate a text from English to another language if target language is valid.

    :param string:
        The text to be translated.
    :param target_language:
        The target language.
    :return:
        The translated text.
    """
    if "EN" in target_language or target_language not in target_languages:
        return string
    else:
        return translator.translate_text(string, source_lang="EN", target_lang=target_language).text


def translate_segments(result: dict, source_language: str, target_language: str) -> dict:
    """
    Translate the segments of a transcription result.

    :param result:
        The transciption result.
    :param source_language:
        The source language.
    :param target_language:
        The target language.
    :return:
        The result with the translated segments.
    """
    print("Translating text...")

    sentences = TextBlob(result['text']).sentences

    translated_segments = []
    start = 0
    # Loop through sentences:
    for sentence in sentences:
        sentence = " " + sentence.raw.strip()
        translated = translator.translate_text(sentence, source_lang=source_language, target_lang=target_language).text

        parts = ""
        previous_length = 0
        # Loop through segments:
        for i in range(start, len(result['segments'])):
            segment = result['segments'][i]
            text = segment['text']
            parts += text

            # Calculate length of segment in translated sentence:
            length = round((len(text) * len(translated)) / len(sentence))

            # Break if sentence complete:
            if parts == sentence:
                if previous_length != -1:
                    segment['text'] = translated[previous_length:]
                    translated_segments.append(segment)

                start = i+1
                break
            elif parts != sentence and previous_length != -1:
                # Determine new length based on words:
                index = translated.find(" ", previous_length + length)

                segment['text'] = translated[previous_length:index] if index != -1 else translated[previous_length:]

                translated_segments.append(segment)
                previous_length = index

    result['segments'] = translated_segments

    print("100% Complete")

    return result