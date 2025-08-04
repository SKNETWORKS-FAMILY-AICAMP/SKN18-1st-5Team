import pandas as pd


download_dir = f"C:\\dev\\mini_1\\현대.xlsx"
out_path = f"C:\\dev\\mini_1\\현대.csv"

df = pd.read_excel(download_dir, sheet_name="Sheet1")  # openpyxl을 자동 사용
df.to_csv(out_path, index=False, encoding="utf-8-sig")  # 한글 깨짐 방지
