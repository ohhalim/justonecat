import os
import requests
import speech_recognition as sr
from pydub import AudioSegment
import io

# 설정 가능한 변수
output_filename = "output_audio.mp3"
url = "https://api.elevenlabs.io/v1/text-to-speech/eleven_multilingual_v2"  # Eleven Labs 모델 URL
headers = {
    "xi-api-key": "YOUR_ELEVEN_LABS_API_KEY",  # Eleven Labs API 키를 입력하세요.
    "Content-Type": "application/json"
}

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
        print(f"음성 생성 실패: {response.status_code} - {response.text}")
        return None

# 음성 인식 함수
def voice_chat():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("음성을 입력하세요. (말하기를 시작하세요.)")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language='ko-KR')  # 한국어 인식
            return text
        except sr.UnknownValueError:
            print("음성을 인식할 수 없습니다.")
            return None
        except sr.RequestError:
            print("음성 인식 서비스에 문제가 발생했습니다.")
            return None

# 메인 실행 부분
if __name__ == "__main__":
    user_input = voice_chat()  # 음성으로 질문 입력
    if user_input:
        print(f"입력된 텍스트: {user_input}")
        
        # 응답을 음성으로 변환
        audio_segment = text_to_speech(user_input)  # 입력된 질문을 음성으로 변환
        if audio_segment:
            print("음성이 성공적으로 생성되었습니다!")
            # 생성된 음성을 재생
            os.system(f"start {output_filename}")  # Windows
            # os.system(f"afplay {output_filename}")  # MacOS
        else:
            print("음성 생성에 실패했습니다.")
