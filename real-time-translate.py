import os
import pyaudio
import wave
import io
import time
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech

# 設置 Google Cloud 專案路徑
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/onlynice/Desktop/STP_python/stp-by-jing-b0ab74d91c6c.json'

# 初始化 Google Cloud 客戶端
speech_client = speech.SpeechClient()
translate_client = translate.Client()
text_to_speech_client = texttospeech.TextToSpeechClient()

# 音頻錄製設置
RATE = 16000
CHUNK = int(RATE / 10)

# 錄製音頻函數
def record_audio(duration=5):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Finished recording.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 保存音頻文件
    wf = wave.open("output.wav", 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# 將音頻文件轉換為文本
def speech_to_text(file_path):
    with io.open(file_path, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="zh-TW",  # 輸入語言為中文
    )
    response = speech_client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript

# 翻譯文本
def translate_text(text, target_language='en'):  # 目標語言為英文
    translation = translate_client.translate(text, target_language=target_language)
    return translation['translatedText']

# 翻譯文本到日文
def translate_text_to_japanese(text):
    translation = translate_client.translate(text, target_language='ja')
    return translation['translatedText']

# 文本轉語音
def text_to_speech(text, lang='en'):
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
    with open("output_audio.wav", "wb") as out:
        out.write(response.audio_content)
    play_audio("output_audio.wav")

# 播放音頻文件
def play_audio(file_path):
    chunk = 1024
    wf = wave.open(file_path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    record_audio()
    text = speech_to_text("output.wav")
    print(f"Recognized text: {text}")
    translated_text_en = translate_text(text, target_language='en')
    print(f"Translated text (English): {translated_text_en}")
    translated_text_ja = translate_text_to_japanese(text)
    print(f"Translated text (Japanese): {translated_text_ja}")
    text_to_speech(translated_text_en, lang='en-US')