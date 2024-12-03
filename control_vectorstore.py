# 문서 로드
import json
import faiss
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
import os

# API 키 로드
with open('openai_api.key', 'r') as f:
    api_key = f.read()

os.environ["OPENAI_API_KEY"] = api_key

# 임베딩
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002") 

def make_news_vec():
    # JSON 파일 로드
    with open('naver_stock_news/today_news.json', 'r') as f:
        articles = json.load(f)

    docs = list()

    for a in articles:
        detail = a.pop('content', '')
        docs.append(Document(page_content=detail + '\n\n' + 'metadata=' + str(a), metadata=a))

    # FAISS 백터 저장소 생성 후 faiss 파일로 저장
    vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)
    vectorstore.save_local(folder_path='naver_stock_news', index_name="news_vec_index")

def get_news_vec():
    vectorstore = FAISS.load_local(folder_path='naver_stock_news', index_name='news_vec_index', embeddings=embeddings,
                                allow_dangerous_deserialization=True)
    return vectorstore