from common_utils import record_audio, speech_to_text, translate_text, text_to_speech, play_audio

if __name__ == "__main__":
    # 錄製音頻
    audio_file = record_audio(duration=5, output_file="output.wav")
    
    # 將音頻轉換為文本
    text = speech_to_text(audio_file, language_code="zh-TW")
    print(f"Recognized text: {text}")
    
    # 翻譯文本為西班牙文
    translated_text_es = translate_text(text, target_language='es')
    print(f"Translated text (Spanish): {translated_text_es}")
    
    # 將翻譯後的文本轉換為語音
    audio_output = "output_es_audio.wav"
    audio_path = text_to_speech(translated_text_es, lang='es', output_file=audio_output)
    
    # 播放語音
    play_audio(audio_path)