import os                                # 引入操作系統模組
import pyaudio                           # 引入音頻處理模組
import wave                              # 引入音頻文件模組
import io                                # 引入I/O操作模組
import time                              # 引入時間模組
from google.cloud import speech_v1p1beta1 as speech      # 引入Google語音識別模組
from google.cloud import translate_v2 as translate       # 引入Google翻譯模組
from google.cloud import texttospeech                     # 引入Google文本轉語音模組

# 設置 Google Cloud 專案路徑
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/onlynice/Desktop/STP_python/stp-by-jing-b0ab74d91c6c.json'

# 初始化 Google Cloud 客戶端
speech_client = speech.SpeechClient()                             # 初始化語音識別客戶端
translate_client = translate.Client()                             # 初始化翻譯客戶端
text_to_speech_client = texttospeech.TextToSpeechClient()         # 初始化文本轉語音客戶端

# 音頻錄製設置
RATE = 16000                    # 設置錄製的取樣率
CHUNK = int(RATE / 10)          # 設置每塊數據的大小

# 錄製音頻函數
def record_audio(duration=5):
    audio = pyaudio.PyAudio()    # 創建 PyAudio 物件
    try:
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)  # 打開音頻流
        frames = []               # 用於存儲音頻數據的列表
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)   # 讀取數據塊
            frames.append(data)         # 添加數據到列表
        print("Finished recording.")
    finally:
        stream.stop_stream()            # 停止音頻流
        stream.close()                  # 關閉音頻流
        audio.terminate()               # 終止 PyAudio 物件

    # 保存音頻文件
    with wave.open("output.wav", 'wb') as wf:
        wf.setnchannels(1)                                         # 設置聲道數
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))    # 設置樣本寬度
        wf.setframerate(RATE)                                      # 設置取樣率
        wf.writeframes(b''.join(frames))                           # 寫入音頻數據

# 將音頻文件轉換為文本
def speech_to_text(file_path):
    with io.open(file_path, "rb") as audio_file:       # 打開音頻文件
        content = audio_file.read()                    # 讀取音頻數據
    audio = speech.RecognitionAudio(content=content)   # 創建 RecognitionAudio 物件
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # 設置音頻編碼格式
        sample_rate_hertz=RATE,                                    # 設置取樣率
        language_code="zh-TW",                                     # 設置語言代碼（中文）
    )
    response = speech_client.recognize(config=config, audio=audio)  # 調用語音識別API
    for result in response.results:                                 # 處理識別結果
        return result.alternatives[0].transcript                    # 返回識別出的文本

# 翻譯文本成韓文
def translate_text_to_korean(text):
    translation = translate_client.translate(text, target_language='ko')  # 調用翻譯API
    return translation['translatedText']                                  # 返回翻譯結果

# 韓文文本轉語音
def text_to_speech(text, lang='ko'):
    synthesis_input = texttospeech.SynthesisInput(text=text)              # 創建合成輸入物件
    voice = texttospeech.VoiceSelectionParams(
        language_code=lang,                                               # 設置語言代碼
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL                  # 設置語音性別
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16                # 設置音頻編碼格式
    )
    response = text_to_speech_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config     # 調用文本轉語音API
    )
    audio_file_name = f"output_{lang}_audio.wav"                          # 設置音頻文件名
    with open(audio_file_name, "wb") as out:
        out.write(response.audio_content)                                 # 寫入音頻數據
    play_audio(audio_file_name)                                           # 播放音頻文件

# 播放音頻文件
def play_audio(file_path):
    chunk = 1024
    with wave.open(file_path, 'rb') as wf:
        p = pyaudio.PyAudio()                                             # 創建 PyAudio 物件
        try:
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)                                  # 打開音頻流
            data = wf.readframes(chunk)                                   # 讀取音頻數據
            while data:
                stream.write(data)                                        # 播放音頻數據
                data = wf.readframes(chunk)                               # 繼續讀取音頻數據
        finally:
            stream.stop_stream()                                          # 停止音頻流
            stream.close()                                                # 關閉音頻流
            p.terminate()                                                 # 終止 PyAudio 物件

if __name__ == "__main__":
    record_audio()                                             # 錄製音頻
    text = speech_to_text("output.wav")                        # 將音頻轉換為文本
    print(f"Recognized text: {text}")                          # 輸出識別文本
    translated_text_ko = translate_text_to_korean(text)            # 翻譯文本到韓文
    print(f"Translated text (Korean): {translated_text_ko}")       # 輸出翻譯文本（韓文）
    text_to_speech(translated_text_ko, lang='ko')                    # 韓文文本轉語音並播放