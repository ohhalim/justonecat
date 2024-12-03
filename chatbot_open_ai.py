import streamlit as st
import control_vectorstore as cv
import os

# API 키 로드. 여기는 각자 시연 환경에 맞게 바꿀 것.
with open('openai_api.key', 'r') as f:
    api_key = f.read()

os.environ["OPENAI_API_KEY"] = api_key

# 모델 및 랭체인 정의 ================================================================ #

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from operator import itemgetter

# 모델 초기화
model = ChatOpenAI(model="gpt-4o-mini")
vector_store = cv.get_news_vec()
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# 시스템 프롬프트 정의
prompt = PromptTemplate.from_template("""
반드시 이미 주어져 있는 맥락(Context)만을 기반으로 해서 사용자의 질문에 대해 한국어로 답변하도록 한다.
이때 다음과 같은 조건에 따라 메타데이터(metadata)를 출력하자.

- 메타데이터는 맥락(Context)의 가장 아래줄에 딕셔너리 형태로 존재한다.
- 메타데이터는 title, url, date 속성이 있다.
- 답변을 다 한 후, 답변의 끝에서 띄어쓰기를 하지 말고 반드시 메타데이터를 다음과 같은 형식으로 출력하자.
    
    [예시]
    메타데이터는 다음과 같습니다: title<주웅간>url<주웅간>date

- 한 개는 반드시 출력한다. 만약에, 다른 기사들에 대해서도 직접 판단했을 때 처음에 출력한 메타데이터와 비슷한 수준의 관련성을 가진다고 판단되면, 아래와 같이 <에엔터>를 붙이고 기사 제목부터 위와 동일한 형식으로 다른 메타데이터를 계속해서 출력한다.

    [예시]
    메타데이터는 다음과 같습니다: title<주웅간>url<주웅간>date<에엔터>title<주웅간>url<주웅간>date
    ...

- 사용자의 질문에 대해 답변할 때 참조할 데이터가 없다면 메타데이터를 출력하지 않는다.

#Previous Chat History:
{chat_history}

#Question: 
{question} 

#Context: 
{context} 

#Answer:
"""
)

# 언어모델(LLM) 생성
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

# 단계 8: 체인(Chain) 생성
chain = (
    {
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question"),
        "chat_history": itemgetter("chat_history"),
    }
    | prompt
    | llm
    | StrOutputParser()
)

# 세션 ID를 기반으로 세션 기록을 가져오는 함수
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in st.session_state["store"]:
        st.session_state["store"][session_id] = ChatMessageHistory()
    return st.session_state["store"][session_id]


# 대화를 기록하는 RAG 체인 생성
rag_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,  # 세션 기록을 가져오는 함수
    input_messages_key="question",  # 사용자의 질문이 템플릿 변수에 들어갈 key
    history_messages_key="chat_history",  # 기록 메시지의 키
)

# ============================================================================ #

# OpenAI API 호출 함수
def gpt_chatbot(user_message, session_id):
    """
    OpenAI API를 호출하여 사용자의 메시지에 대한 응답을 생성합니다.
    
    Args:
        user_message (str): 사용자의 입력 메시지.

    Returns:
        str: 챗봇의 응답 또는 오류 메시지.
    """
    try:
        response = rag_with_history.invoke(
            {"question": user_message},
            config={ "configurable" : {"session_id": session_id}}
        )
        return response
    
    except Exception as e:
        return f"오류 발생: {str(e)}"
