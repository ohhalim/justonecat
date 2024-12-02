import os
import requests
from pydub import AudioSegment
import io
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 설정: OpenAI API 키
os.environ["OPENAI_API_KEY"] = "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"

# 설정 가능한 변수
output_filename = "output_audio.mp3"
url = "https://api.elevenlabs.io/v1/text-to-speech/eleven_multilingual_v2"  # Eleven Labs 모델 URL
headers = {
    "xi-api-key": "YOUR_ELEVEN_LABS_API_KEY",  # Eleven Labs API 키를 입력하세요.
    "Content-Type": "application/json"
}

# 음성 생성 함수
def generate_audio(text):
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

# OpenAI API 호출 함수
def chat_with_openai(user_input):
    # 모델 초기화
    model = ChatOpenAI(model="gpt-4o-mini")
    
    # 사용자 메시지 생성
    human_message = HumanMessage(content=user_input)
    
    # 챗봇 응답 얻기
    response = model([human_message])
    return response.content

# Streamlit UI 설정
st.title("음성 챗봇")
user_input = st.text_input("텍스트를 입력하세요:")

if st.button("음성 입력 시작"):
    if user_input:
        # OpenAI API에 질문하여 응답 얻기
        bot_response = chat_with_openai(user_input)
        st.write(f"챗봇 응답: {bot_response}")

        # 응답을 음성으로 변환
        audio_segment = generate_audio(bot_response)
        if audio_segment:
            st.success("음성이 성공적으로 생성되었습니다!")
            # Streamlit에서 오디오 재생
            st.audio(output_filename)
        else:
            st.error("음성 생성에 실패했습니다.")
    else:
        st.warning("텍스트를 입력하세요.")

