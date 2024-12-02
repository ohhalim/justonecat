# streamlit run test_03.py 

from chatbot_open_ai import gpt_chatbot
from load_kospi_data import upload_data
import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from local_components import card_container
import json 
import streamlit_shadcn_ui as ui 
from streamlit_elements import elements, mui, html
import openai
import streamlit as st
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv 
import os 

langage = 'kor'


# 대시보드 레이아웃 정의
st.set_page_config(
    page_title="test",
    layout="wide")


first_col = st.columns((0.66,0.33), gap='small')
with first_col[0]:
    with st.container(height=100):
            st.markdown('### 오늘의 증권뉴스')
with first_col[1]:           
    with st.container(height=100):
            st.markdown('###### 언어변경')
            col_1,col_2,col_3 = st.columns([2,2,2], gap="small")
            with col_1:
                if st.button('kor'):
                    st.write('한국어')
            with col_2:
                if st.button('eng'):
                    st.write('영어')
            with col_3:
                if st.button('jap'):
                    st.write('일본어')


# 'kor'이 선택 되었을 떄,
if langage == 'kor':
    kospi200_data = upload_data('kospi200_data.csv')
    KOSDAQ_data = upload_data('KOSDAQ_data.csv')
    kospi_data = upload_data('kospi_data.csv')
    main_news_data = upload_data('main_news_data.csv')

# 'eng'이 선택 되었을 떄,
elif langage == 'eng':
    kospi200_data = upload_data('kospi200_data_eng.csv')
    KOSDAQ_data = upload_data('KOSDAQ_data_eng.csv')
    kospi_data = upload_data('kospi_data_eng.csv')
    main_news_data = upload_data('main_news_data_eng.csv')

# 'jap'이 선택 되었을 떄,
elif langage == 'jap':
    kospi200_data = upload_data('kospi200_data.csv_jap')
    KOSDAQ_data = upload_data('KOSDAQ_data.csv_jap')
    kospi_data = upload_data('kospi_data.csv_jap')
    main_news_data = upload_data('main_news_data.csv_jap')



second_col = st.columns((0.33,0.44,0.22), gap='small')


with second_col[0]:
    with st.container(height=100):      
         st.markdown('#### 오늘의 뉴스')


### 열 순서 주의!
with second_col[2]:
    with st.container(height=100):
                 selected_tab = st.radio(
                    "지수 선택",
                    options=["코스닥", "코스피", "코스피200"],
                    horizontal=True,
                    label_visibility="collapsed"
                 )


# 코스닥, 코스피, 코스피200
with second_col[1]:  
    with st.container(height=100):
             # 선택된 지수에 따라 데이터 표시
            if selected_tab == "코스닥":
                st.markdown('##### 코스닥')
                col1, col2 = st.columns(2)  # 가로로 출력되게 하기 위해 열 설정
                with col1:
                    st.markdown(f"**날짜:{KOSDAQ_data['Date'][0]}**")
                with col2:
                    st.markdown(f"**종가: {KOSDAQ_data['Closing Price'][0]}**")

            elif selected_tab == "코스피":
                st.markdown('##### 코스피')
                col1, col2 = st.columns(2)
                with col1:                
                    st.markdown(f"**날짜: {kospi_data['Date'][0]}**")
                with col2:                
                    st.markdown(f"**종가: {kospi_data['Closing Price'][0]}**")

            elif selected_tab == "코스피200":
                st.markdown('##### 코스피200')
                col1, col2 = st.columns(2)
                with col1:                
                    st.markdown(f"**날짜: {kospi200_data['Date'][0]}**")
                with col2:                
                    st.markdown(f"**종가: {kospi200_data['Closing Price'][0]}**")

third_col = st.columns((0.33, 0.66), gap='small')

with third_col[0]:
    with st.container(height=500,key='card'):

        with st.container():
            st.markdown(f"**주요뉴스**")
            
        # 말풍선 및 링크 연결 구현
        for idx in range(len(main_news_data)):
            title = main_news_data["제목"][idx]
            link = main_news_data["링크"][idx]
            
            # HTML로 말풍선과 링크 추가
            #
            st.markdown(
                f"""
                <a href="{link}" target="_blank" style="text-decoration:none; color:black;">
                    <div title="{title}" style="padding:10px; border:1px solid #ddd; border-radius:5px; margin-bottom:10px;">
                        {title[:30]}...
                    </div>
                </a>
                """,
                unsafe_allow_html=True
    )


# 대화기록 코드: Streamlit 대화 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []

with third_col[1]:
    chat_bot_container = st.container(height= 500)

    with chat_bot_container:

        # 1.대화기록 코드: 이전 대화 내용 출력
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # 2.챗봇 코드: 사용자 입력처리
    if prompt := st.chat_input("말씀해주세요."):
        
        with chat_bot_container:

            # 3.사용자 메시지를 대화기록에 추가
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # 4. 챗봇 응답 생성
            response = '임시 챗봇입니다. ' # gpt_chatbot(prompt)
            # 4.챗봇 응답을 대화기록에 추가
            st.session_state.messages.append({"role": "assistant", "content": response})

            # 5. 사용자 메시지를 화면에 표시
            with st.chat_message("user"):
                st.markdown(prompt)
            # 6. 챗봇의 응답을 화면에 표시
            with st.chat_message("assistant"):
                st.markdown(response)
