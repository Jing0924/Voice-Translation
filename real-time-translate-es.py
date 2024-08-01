import os
import pyaudio
import wave
import io
import time
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech

# Set Google Cloud project path
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/onlynice/Projects/STP/private_key/stp-by-jing-b0ab74d91c6c.json'

# Initialize Google Cloud clients
speech_client = speech.SpeechClient()
translate_client = translate.Client()
text_to_speech_client = texttospeech.TextToSpeechClient()

# Audio recording settings
RATE = 16000
CHUNK = int(RATE / 10)

# Record audio function
def record_audio(duration=5):
    audio = pyaudio.PyAudio()
    try:
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("Finished recording.")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    # Save audio file
    with wave.open("output.wav", 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

# Convert audio file to text
def speech_to_text(file_path):
    with io.open(file_path, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="zh-TW",
    )
    response = speech_client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript

# Translate text to Spanish
def translate_text_to_spanish(text):
    translation = translate_client.translate(text, target_language='es')
    return translation['translatedText']

# Convert Spanish text to speech
def text_to_speech(text, lang='es'):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=lang,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = text_to_speech_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    audio_file_name = f"output_{lang}_audio.wav"
    with open(audio_file_name, "wb") as out:
        out.write(response.audio_content)
    play_audio(audio_file_name)

# Play audio file
def play_audio(file_path):
    chunk = 1024
    with wave.open(file_path, 'rb') as wf:
        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            data = wf.readframes(chunk)
            while data:
                stream.write(data)
                data = wf.readframes(chunk)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

if __name__ == "__main__":
    record_audio()
    text = speech_to_text("output.wav")
    print(f"Recognized text: {text}")
    translated_text_es = translate_text_to_spanish(text)
    print(f"Translated text (Spanish): {translated_text_es}")
    text_to_speech(translated_text_es, lang='es')