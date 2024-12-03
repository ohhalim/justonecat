# streamlit run test_04.py 

from voice_chat import text_to_speech
from voice_chat import voice_chat
import streamlit as st
from local_components import card_container
from streamlit_extras.stylable_container import stylable_container
from os import path

# 네이버 뉴스 기사가 없을 경우 크롤링 및 벡터화 진행
from get_news import get_news
if path.exists("naver_stock_news/today_news.json"): pass
else: get_news()

import control_vectorstore as cv
if path.exists("naver_stock_news/news_vec.faiss"): pass
else: cv.make_news_vec()

import chatbot_open_ai as ai
import time

# ============================================================== #

# 크롤링 관련
from bs4 import BeautifulSoup
import requests

# 네이버페이 증권 국내 지표 확인
sise_url = 'https://finance.naver.com/sise/'
header = {'User-agent':'Mozilla/5.0'}

sise_html = BeautifulSoup(requests.get(sise_url, headers=header).text, 'html.parser')
kospi, kospi_change = sise_html.find('span', id='KOSPI_now').text, sise_html.find(id='KOSPI_change').text.strip('\n')[:-2].split()
kosdaq, kosdaq_change = sise_html.find('span', id='KOSDAQ_now').text, sise_html.find(id='KOSDAQ_change').text.strip('\n')[:-2].split()
kospi200, kospi200_change = sise_html.find('span', id='KPI200_now').text, sise_html.find(id='KPI200_change').text.strip('\n')[:-2].split()

# 한국경제 증권 해외 지표 확인
world_url = 'https://datacenter.hankyung.com/major-indices/'

dowjones_html = BeautifulSoup(requests.get(world_url + 'djia', headers=header).text, 'html.parser')
nasdaq_html = BeautifulSoup(requests.get(world_url + 'nasdaq', headers=header).text, 'html.parser')
snp500_html = BeautifulSoup(requests.get(world_url + 'sp500', headers=header).text, 'html.parser')
dowjones, dowjones_change = dowjones_html.find(class_='price').text, dowjones_html.find(class_='quot').text.strip('\n').split('\n')
nasdaq, nasdaq_change = nasdaq_html.find(class_='price').text, nasdaq_html.find(class_='quot').text.strip('\n').split('\n')
snp500, snp500_change = snp500_html.find(class_='price').text, snp500_html.find(class_='quot').text.strip('\n').split('\n')

# ============================================================== #

# 대시보드 레이아웃 정의
st.set_page_config(
    page_title="test",
    layout="wide")

st.markdown("""
    <style>
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");
        * {
            font-family: Pretendard;
        }
    </style>
""", unsafe_allow_html=True)

def stream_data(x):
    for word in x.split(" "):
        yield word + " "
        time.sleep(0.02)

first_col = st.columns([0.9, 0.1], gap='small')

with first_col[0]:
    st.markdown('## 🍟 Financial NewsSnack')

import json
with open('naver_stock_news/today_news.json', 'r') as f:
    main_news_data = json.load(f)

second_col = st.columns([0.3, 0.7])

with second_col[0]:
    st.markdown(f"### 주요뉴스")
    with st.container(height=704, border=False):
        
        # 말풍선 및 링크 연결 구현
        for idx in range(len(main_news_data)):
            title = main_news_data[idx]['title']
            link = main_news_data[idx]['url']
            
            # HTML로 말풍선과 링크 추가
            with stylable_container(
                key='news_list',
                css_styles="""
                * {
                    float: fill;
                    margin: 0.01px; 
                }
                """,
                ):
                st.markdown(
                    f"""
                    <a href="{link}" target="_blank" style="text-decoration:none; color:black;">
                        <div title="{title}" style="padding:8px; border:1px solid #ddd; border-radius:12px;">
                            {title[:30]}...
                        </div>
                    </a>
                    """,
                    unsafe_allow_html=True
                )

with second_col[1]:

    with st.container(key="stock_index"):

        head_left, head_right = st.columns([0.7, 0.3])
        with head_right:
            with stylable_container(
                key='sub_right',
                css_styles="""
                * {
                    float: right;
                    margin: 0.01px; 
                }
                """,
            ):  
                selected_tab = st.segmented_control(
                    label='주식장 선택', default='국내', options=['국내', '해외'], label_visibility='collapsed')
        with head_left:
            st.markdown(f'### {selected_tab} 증시 지표')

        detail = st.columns(3)
        if selected_tab == '국내':
            with detail[0]:
                with card_container(key='detail_col1'):
                    with stylable_container(
                        key='detail',
                        css_styles="""
                        * {
                            margin: 0px;
                            padding: 0px;
                        }
                        p {
                            font-size: 16px;
                        }
                        """
                    ):
                        st.markdown(f"<p>코스피</p><h3>{kospi}</h3><p>어제보다 {kospi_change[0]} {'하락' if kospi_change[1][0] == '-' else '상승'} ({kospi_change[1]})</p>", unsafe_allow_html=True)
            with detail[1]:
                with card_container(key='detail_col2'):
                    with stylable_container(key='detail', css_styles=''):
                        st.markdown(f"<p>코스닥</p><h3>{kosdaq}</h3><p>어제보다 {kosdaq_change[0]} {'하락' if kosdaq_change[1][0] == '-' else '상승'} ({kosdaq_change[1]})</p>", unsafe_allow_html=True)
            
            with detail[2]:
                with card_container(key='detail_col3'):
                    with stylable_container(key='detail', css_styles=''):
                        st.markdown(f"<p>코스피200</p><h3>{kospi200}</h3><p>어제보다 {kospi200_change[0]} {'하락' if kospi200_change[1][0] == '-' else '상승'} ({kospi200_change[1]})</p>", unsafe_allow_html=True)
        if selected_tab == '해외':
            with detail[0]:
                with card_container(key='detail_col1'):
                    with stylable_container(
                        key='detail',
                        css_styles="""
                        * {
                            margin: 0px;
                            padding: 0px;
                        }
                        p {
                            font-size: 16px;
                        }
                        """
                    ):
                        st.markdown(f"<p>S&P500</p><h3>{snp500}</h3><p>어제보다 {snp500_change[0]} {'하락' if snp500_change[1][0] == '-' else '상승'} ({snp500_change[1]})</p>", unsafe_allow_html=True)
            with detail[1]:
                with card_container(key='detail_col2'):
                    with stylable_container(key='detail', css_styles=''):
                        st.markdown(f"<p>나스닥</p><h3>{nasdaq}</h3><p>어제보다 {nasdaq_change[0]} {'하락' if nasdaq_change[1][0] == '-' else '상승'} ({nasdaq_change[1]})</p>", unsafe_allow_html=True)
            
            with detail[2]:
                with card_container(key='detail_col3'):
                    with stylable_container(key='detail', css_styles=''):
                        st.markdown(f"<p>다우존스</p><h3>{dowjones}</h3><p>어제보다 {dowjones_change[0]} {'하락' if dowjones_change[1][0] == '-' else '상승'} ({dowjones_change[1]})</p>", unsafe_allow_html=True)


    # 대화기록 코드: Streamlit 대화 상태 초기화
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    if "store" not in st.session_state:
        st.session_state["store"] = dict()

    chat_bot_container = st.container(height=500)

    with chat_bot_container:

        # 1.대화기록 코드: 이전 대화 내용 출력
        for idx, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                col1,col2 = st.columns([0.9, 0.1], vertical_alignment='center')

                with col1:
                    st.markdown(message["content"])

                with col2:
                    if st.button("🔊", key=f"audio_{idx}"):
                        text_to_speech(message["content"])  # 메시지 내용 음성 출력    

    session_id = 'aaa'
    metadata = ''

    # 4. 챗봇 응답 생성
    if not st.session_state.messages:
        with chat_bot_container:
            with st.chat_message("assistant"):
                greetings = ai.gpt_chatbot('인사와 함께 오늘 시장 상황이 어땠는지 알려주세요.', session_id)
                
                if "메타데이터는 다음과 같습니다:" in greetings:
                    start = greetings.find("메타데이터는 다음과 같습니다:")
                    metadata = greetings[start+17:].split("<에엔터>")
                    metadata = [d.split('<주웅간>') for d in metadata]
                    greetings = greetings[:start]
                
                st.write_stream(stream_data(greetings))
                if metadata:
                    st.markdown('참고한 기사는 다음과 같습니다.')
                    result_col = st.columns([0.3, 0.3, 0.3, 0.1])
                    for i, m in enumerate(metadata):
                        with result_col[i]:
                            with st.container(border=True):
                                st.markdown(
                                    f"""
                                    <a href="{m[1]}" target="_blank" style="text-decoration:none; color:black;">
                                        <h5 style="text-overflow : ellipsis; overflow: hidden; white-space: nowrap;">{m[0]}</h5>
                                        <p style="text-overflow : ellipsis; overflow: hidden; white-space: nowrap;">{m[1]}</p>
                                        <p style="text-overflow : ellipsis; overflow: hidden; white-space: nowrap;">{m[2]}</p>
                                    </a>
                                    """,
                                    unsafe_allow_html=True
                                )
                st.session_state.messages.append({"role": "assistant", "content": greetings})

    # 2.챗봇 코드: 사용자 입력처리
    if prompt := st.chat_input("궁금한 것이 있다면 물어보세요."):

        with chat_bot_container:

            # 3.사용자 메시지를 대화기록에 추가
            st.session_state.messages.append({"role": "user", "content": prompt})

            # 5. 사용자 메시지를 화면에 표시
            with st.chat_message("user"):
                st.markdown(prompt)

            # 4. 챗봇 응답 생성
            response = ai.gpt_chatbot(prompt, session_id)
            if "메타데이터는 다음과 같습니다:" in response:
                start = response.find("메타데이터는 다음과 같습니다:")
                metadata = response[start+17:].split("<에엔터>")
                metadata = [d.split('<주웅간>') for d in metadata]
                response = response[:start]

            # 6. 챗봇의 응답을 화면에 표시
            with st.chat_message("assistant"):
                st.write_stream(stream_data(response))
                if metadata:
                    st.markdown('참고한 기사는 다음과 같습니다.')
                    result_col = st.columns([0.3, 0.3, 0.3, 0.1])
                    for i, m in enumerate(metadata):
                        with result_col[i]:
                            with st.container(border=True):
                                st.markdown(
                                    f"""
                                    <a href="{m[1]}" target="_blank" style="text-decoration:none; color:black;">
                                        <h5 style="text-overflow : ellipsis; overflow: hidden; white-space: nowrap;">{m[0]}</h5>
                                        <p style="text-overflow : ellipsis; overflow: hidden; white-space: nowrap;">{m[1]}</p>
                                        <p style="text-overflow : ellipsis; overflow: hidden; white-space: nowrap;">{m[2]}</p>
                                    </a>
                                    """,
                                    unsafe_allow_html=True
                                )
            # 4.챗봇 응답을 대화기록에 추가
            st.session_state.messages.append({"role": "assistant", "content": response})

    # 음성 입력 버튼 추가
    if st.button("🎤 음성으로 입력하기"):
        detected_message = voice_chat()
        st.session_state.messages.append({"role": "user", "content": detected_message})
