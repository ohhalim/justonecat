import streamlit as st
from utils import print_message, StreamHandler 
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import ChatMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

import os   

st.set_page_config(page_title="ChatGPT", page_icon=":speech_balloon:")
st.title("ChatGPT") 

os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"] 

if "messages" not in st.session_state:
    st.session_state.messages = []

if "store" not in st.session_state:
    st.session_state["store"] = dict()

with st.sidebar:
    session_id = st.text_input("Session ID", value="abc123")

print_message()

def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    if session_ids not in st.session_state["store"]:

    
        st.session_state["store"][session_ids] = ChatMessageHistory()
    return st.session_state["store"][session_ids]

if user_input := st.chat_input("메세지를 입력해주세요."):
    st.chat_message("user").write(f"{user_input}")
    st.session_state["messages"].append(ChatMessage(role="user", content=user_input))   

    
    with st.chat_message("assistant"):
        stream_hander = StreamHandler(st.empty())

        # 1. 모델 생성 
    llm = ChatOpenAI(streaming=True, callbacks=[stream_hander])

    # 2. 프롬프트 생성
    prompt = ChatPromptTemplate.from_messages([
        ("system", "질문에 짧고 간결하게 답변해 주세요"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    chain = prompt | llm 

    chain_with_memory = (
        RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_message_key="question",
            history_messages_key="history",
        )    
    )


    response = chain_with_memory.invoke(
        {"question": user_input},
        config={"configurable": {"session_id": session_id}},
    )

    st.session_state["messages"].append(
        ChatMessage(role="assistant", content=response.content)
    )

