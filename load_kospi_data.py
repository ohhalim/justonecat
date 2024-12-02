# KOSPI 데이터를 로드하는 함수
import pandas as pd

def upload_data(input):
    try:
        df = pd.read_csv(input, encoding="utf-8-sig")
        if not df.empty:
            return df  
        else:
            return None
    except Exception as e:
        return {"error": str(e)}