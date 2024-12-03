# KOSPI 데이터를 로드하는 함수
def upload_data(input):
    import pandas as pd
    try:
        df = pd.read_csv(input, encoding="utf-8")
        if not df.empty:
            return df  
        else:
            return None
    except Exception as e:
        return {"error": str(e)}