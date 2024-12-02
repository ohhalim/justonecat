import os
import requests
import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
import io

# 설정 가능한 변수
output_filename = "output_audio.mp3"
url = f"https://api.elevenlabs.io/v1/text-to-speech/{'Xb7hH8MSUJpSbSDYk0k2'}/stream"  # Eleven Labs 모델 URL
headers = {
    "xi-api-key": "sk_ac045c4a7e4c91f9cf1297482d5ab0a8d13097ad8cb586fe", # Eleven Labs API 키를 입력하세요.
    "Content-Type": "application/json"
}

# 음성 인식 함수
def voice_chat():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("음성을 입력하세요. (말하기를 시작하려면 '음성 입력 시작' 버튼을 클릭하세요.)")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language='ko-KR')  # 한국어 인식
            return text
        except sr.UnknownValueError:
            st.error("음성을 인식할 수 없습니다.")
            return None
        except sr.RequestError:
            st.error("음성 인식 서비스에 문제가 발생했습니다.")
            return None

# 음성 생성 함수
def text_to_speech(text):
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.3,
            "similarity_boost": 1,
            "style": 1,
            "use_speaker_boost": True
        }
    }

    response = requests.post(url, json=data, headers=headers, stream=True)

    if response.status_code == 200:
        audio_content = b""
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                audio_content += chunk

        segment = AudioSegment.from_mp3(io.BytesIO(audio_content))
        segment.export(output_filename, format="mp3")
        return segment
    else:
        st.error(f"음성 생성 실패: {response.status_code} - {response.text}")
        return None

# Streamlit UI 설정
st.title("음성 입력 및 출력 챗봇")

if st.button("음성 입력 시작"):
    user_input = voice_chat()  # 음성으로 질문 입력
    if user_input:
        st.write(f"입력된 텍스트: {user_input}")
        
        # 응답을 음성으로 변환
        audio_segment = text_to_speech(user_input)  # 입력된 질문을 음성으로 변환
        if audio_segment:
            st.success("음성이 성공적으로 생성되었습니다!")
            # Streamlit에서 오디오 재생
            st.audio(output_filename)
        else:
            st.error("음성 생성에 실패했습니다.")
