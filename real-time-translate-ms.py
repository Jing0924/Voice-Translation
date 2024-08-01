import os
import pyaudio
import wave
import io
import time
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech

# Tetapkan laluan projek Google Cloud
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/onlynice/Projects/STP/private_key/stp-by-jing-b0ab74d91c6c.json'

# Inisialisasi klien Google Cloud
speech_client = speech.SpeechClient()
translate_client = translate.Client()
text_to_speech_client = texttospeech.TextToSpeechClient()

# Tetapan rakaman audio
RATE = 16000
CHUNK = int(RATE / 10)

# Fungsi untuk merakam audio
def record_audio(duration=5):
    audio = pyaudio.PyAudio()
    try:
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("Rakaman selesai.")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    # Simpan fail audio
    with wave.open("output.wav", 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

# Tukar fail audio kepada teks
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

# Terjemahkan teks kepada Bahasa Melayu
def translate_text_to_malay(text):
    translation = translate_client.translate(text, target_language='ms')
    return translation['translatedText']

# Tukar teks Bahasa Melayu kepada suara
def text_to_speech(text, lang='ms'):
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

# Mainkan fail audio
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
    print(f"Teks yang dikenali: {text}")
    translated_text_ms = translate_text_to_malay(text)
    print(f"Teks yang diterjemahkan (Bahasa Melayu): {translated_text_ms}")
    text_to_speech(translated_text_ms, lang='ms')