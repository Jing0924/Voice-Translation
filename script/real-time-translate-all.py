from common_utils import record_audio, speech_to_text, translate_text, text_to_speech, play_audio

if __name__ == "__main__":
    # 錄製音頻
    audio_file = record_audio(duration=5, output_file="output.wav")
    
    # 將音頻轉換為文本
    text = speech_to_text(audio_file, language_code="zh-TW")
    print(f"Recognized text: {text}")
    
    # 翻譯文本到多種語言
    languages = {
        "en": "English",
        "ja": "Japanese",
        "ko": "Korean",
        "fr": "French",
        "es": "Spanish",
        "de": "German"
    }
    
    for lang_code, lang_name in languages.items():
        translated_text = translate_text(text, target_language=lang_code)
        print(f"Translated text ({lang_name}): {translated_text}")
        
        # 將翻譯後的文本轉換為語音
        audio_output = f"output_{lang_code}_audio.wav"
        audio_path = text_to_speech(translated_text, lang=lang_code, output_file=audio_output)
        
        # 播放語音
        play_audio(audio_path)