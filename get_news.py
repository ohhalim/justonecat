def get_news():
    from bs4 import BeautifulSoup
    import requests

    # 네이버페이 증권 오늘의 주요 뉴스
    start_url = 'https://finance.naver.com/news/mainnews.naver'
    header = {'User-agent':'Mozilla/5.0'}

    html = BeautifulSoup(requests.get(start_url, headers=header).text, 'html.parser')
    pgrr = html.find('td', class_='pgRR')

    last_page = int(pgrr.a['href'].split('=')[-1])

    import re
    import time

    article_list = []
    select_summary = 0  # 0은 요약 안 함. 1은 요약함.

    for page in range(1, last_page + 1):
        print(f'{page}페이지 진행 중...')
        list_url = start_url + f'?&page={page}'
        list_html = BeautifulSoup(requests.get(list_url, headers=header).text, 'html.parser')
        list_html.find('ul', class_='newsList').select('dd > a')[0]['href']

        bridges = list_html.find('ul', class_='newsList').select('dd > a')
        for bridge in bridges:
            bridge_html = BeautifulSoup(requests.get('https://finance.naver.com' + bridge['href'], headers=header).text, 'html.parser')
            
            # 기사 url
            article_url = str(bridge_html.select_one('script')).split("'")[1]

            article_html = BeautifulSoup(requests.get(article_url, headers=header).text, 'html.parser')

            # 기사 제목
            title = article_html.select_one('h2', class_='media_end_head_headline').span.text
            
            # 기사 작성 시각
            date = article_html.find('span', class_='media_end_head_info_datestamp_time _ARTICLE_DATE_TIME')['data-date-time']

            # 기사 내용. 정규식을 통한 전처리 과정은 GPT의 힘을 빌림.
            article = article_html.find('article')
            blanked = re.sub(r'(?<=[^\d])\.(?=\S)|(?<=[\d])\.(?=[^\d\s])', r'. ', article.text)
            content = re.sub(r'\n+', '\n', blanked)
            article_list.append({'title':title, 'url':article_url, 'date':date, 'content':content})
            time.sleep(0.01)

    import os
    import json

    os.makedirs('naver_stock_news', exist_ok=True)

    suffix = '_summary' if select_summary == 1 else ''

    with open('naver_stock_news/today_news' + suffix + '.json', 'wt', encoding='utf-8') as f:
        json.dump(article_list, f, ensure_ascii=False, indent=4)