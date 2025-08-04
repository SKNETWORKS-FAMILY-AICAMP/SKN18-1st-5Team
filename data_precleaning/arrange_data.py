import pandas as pd
import glob
import os

# col 정리(도시 data)
def city_arrange():
    for year in range(2025,2016,-1):
        download_dir = f"C:\\dev\\mini_1\\data\\{year}\\" 
        df = pd.read_csv(download_dir+f'{year}_통계표.csv')
        df_long = pd.melt(df, id_vars=["지역"], var_name="용도", value_name="등록대수")
        new_download_dir = "C:\\dev\\mini_1\\data\\통계표(연도별)\\"
        df_long.to_csv(new_download_dir+f"{year}_city통계.csv", index=False)

# col 정리(sex_data)     
def sex_combine():
    for year in range(2025,2024,-1):
        download_dir = f"C:\\dev\\mini_1\\data\\{year}\\" 
        df = pd.read_csv(download_dir+f'{year}_연령.csv')
        df_long = pd.melt(df, id_vars=["성별"], var_name="지역", value_name="등록대수")
        new_download_dir = "C:\\dev\\mini_1\\data\\통계표(연령별)\\"
        df_long.to_csv(new_download_dir+f"{year}_연령통계.csv", index=False)
 
# 연도별로 되어있는 파일 병합       
def year_combine():
    download_dir = f"C:\\dev\\mini_1\\data\\통계표(연도별)\\" 
    files = glob.glob(download_dir+"*.csv")  # 모든 CSV 파일 경로 읽기
    # 연도별 파일 합치기
    df_list = []
    for file in files:
        file_name = os.path.basename(file)
        year = file_name.split('_')[0] # 파일명에서 연도 추출
        df = pd.read_csv(download_dir+file_name)
        df['연도'] = int(year)
        df_list.append(df)

    merged_df = pd.concat(df_list) # 하나의 DataFrame으로 병합
    merged_df.to_csv(f"C:\\dev\\mini_1\\data\\"+"city_data.csv", index=False) # 저장

year_combine()
