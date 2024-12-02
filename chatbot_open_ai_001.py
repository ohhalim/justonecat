import openai
import streamlit as st

# OpenAI API 호출 함수
def gpt_chatbot(user_message):
    """
    OpenAI API를 호출하여 사용자의 메시지에 대한 응답을 생성합니다.
    
    Args:
        user_message (str): 사용자의 입력 메시지.

    Returns:
        str: 챗봇의 응답 또는 오류 메시지.
    """
    try:        
        response = openai.ChatCompletion.create(
            model="gpt-4",  # 모델 호출
            messages=[
                {"role": "system", "content": "자기소개해줘"},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"오류 발생: {str(e)}"


# Streamlit 앱 실행 함수
def run_chatbot():
    """
    Streamlit 기반 OpenAI GPT 챗봇을 실행하는 함수입니다.
    """
    # 대화 상태 초기화
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    st.title("OpenAI 기반 GPT 챗봇")

    # 사용자 입력
    user_input = st.text_input('질문을 입력하세요!')

    # 응답 처리
    if user_input:
        response = gpt_chatbot(user_input)
        st.session_state["messages"].append({"user": user_input, "bot": response})

    # 대화 기록 표시
    st.subheader("대화 기록")
    for msg in st.session_state["messages"]:
        st.write(f"**사용자:** {msg['user']}")
        st.write(f"**챗봇:** {msg['bot']}")

    # 대화 초기화 버튼
    if st.button("대화 초기화"):
        st.session_state["messages"] = []