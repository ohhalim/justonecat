# 문서 로드
import json
from langchain.docstore.document import Document

# json 파일 경로
json_file = "test/naver_stock_news/today_news.json"

# JSON 파일 로드
with open(json_file, 'r') as f:
    data = json.load(f)
    
# LangChain 문서 형식으로 변환
doc = Document(
    page_content=json.dumps(data),
    metadata={"source": json_file}
)

# 청킹

from langchain.text_splitter import RecursiveCharacterTextSplitter

recursive_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=10,
    length_function=len,
    is_separator_regex=False,
)

# 문서를 리스트로 감싸서 전달
splits = recursive_text_splitter.split_documents([doc])


# 임베딩

from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002") 


# FAISS 백터 저장소 생성

from langchain_community.vectorstores import FAISS

vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)

