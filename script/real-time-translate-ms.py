from common_utils import record_audio, speech_to_text, translate_text, text_to_speech, play_audio

if __name__ == "__main__":
    # 錄製音頻
    audio_file = record_audio(duration=5, output_file="output.wav")
    
    # 將音頻轉換為文本
    text = speech_to_text(audio_file, language_code="zh-TW")
    print(f"Teks yang dikenali: {text}")
    
    # 翻譯文本為馬來文
    translated_text_ms = translate_text(text, target_language='ms')
    print(f"Teks yang diterjemahkan (Bahasa Melayu): {translated_text_ms}")
    
    # 將翻譯後的文本轉換為語音
    audio_output = "output_ms_audio.wav"
    audio_path = text_to_speech(translated_text_ms, lang='ms', output_file=audio_output)
    
    # 播放語音
    play_audio(audio_path)