import os
import pyaudio
import wave
import io
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech

# 提示：目前該專案只支持中文轉英文、日文、韓文、法文、西班牙文、德文和馬來語。

# 設置 Google Cloud 專案路徑
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/onlynice/Projects/STP/private_key/stp-by-jing-b0ab74d91c6c.json'

# 初始化 Google Cloud 客戶端
speech_client = speech.SpeechClient()
translate_client = translate.Client()
text_to_speech_client = texttospeech.TextToSpeechClient()

# 音頻錄製設置
RATE = 16000
CHUNK = int(RATE / 10)

# 確保 output 目錄存在
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def record_audio(duration=5, output_file="output.wav"):
    """錄製音頻並保存到指定文件"""
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

    output_path = os.path.join(OUTPUT_DIR, output_file)
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print(f"Audio saved to {output_path}")
    return output_path

def speech_to_text(file_path, language_code="zh-TW"):
    """將音頻文件轉換為文本"""
    with io.open(file_path, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )
    response = speech_client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript

def translate_text(text, target_language):
    """翻譯文本到目標語言"""
    translation = translate_client.translate(text, target_language=target_language)
    return translation['translatedText']

def text_to_speech(text, lang, output_file):
    """將文本轉換為語音並保存到文件"""
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
    output_path = os.path.join(OUTPUT_DIR, output_file)
    with open(output_path, "wb") as out:
        out.write(response.audio_content)
    print(f"Audio saved to {output_path}")
    return output_path

def play_audio(file_path):
    """播放音頻文件"""
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