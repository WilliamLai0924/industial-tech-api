import io
import pandas as pd

def get_evalue_plans(file_bytes):
    try:
        df = pd.read_excel(file_bytes, engine='openpyxl')
    except Exception as e:
        raise f"讀取 Excel 文件時發生錯誤：{str(e)}"
    
    result = df.sort_values(by='日期', ascending=True).head()
    return result;