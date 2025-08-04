import pandas as pd
import glob
import os

download_dir = r"C:\dev\\"
files = glob.glob(os.path.join(download_dir, "*.csv"))  # 모든 CSV 파일 경로 읽기
df_list = []

for file in files:
    try:
        # CSV 읽기 (인코딩 시도)
        for enc in ('utf-8', 'cp949', 'euc-kr'):
            try:
                df = pd.read_csv(file, encoding=enc)
                break
            except UnicodeDecodeError:
                df = None
        if df is None:
            raise UnicodeDecodeError(f"모든 인코딩 시도 실패: {file}")

        # '시군구'에 '계'인 행 제거
        df = df[df['시군구'] != '계']

        # '시점'에서 연도 추출 (예: "2017.01" -> "2017")
        df['연도'] = df['시점'].astype(str).str[:4]

        df_list.append(df)
        print(f"처리 완료: {os.path.basename(file)}")
    except Exception as e:
        print(f"오류 발생 ({file}): {e}")

# 모든 파일 병합 (원본 월 단위 데이터 합침)
if not df_list:
    raise RuntimeError("읽어들인 유효한 데이터가 없습니다.")

merged_raw = pd.concat(df_list, ignore_index=True)

# 최종 연도별 집계 (중복된 조합은 다시 합산)
final_agg = (
    merged_raw
    .groupby(['시도명', '시군구', '레벨01', '연도'], dropna=False)['계']
    .sum()
    .reset_index()
)

# 저장: 통합 연도별 합계
out_path = os.path.join(download_dir, "시군구_연도별_합계_통합.csv")
final_agg.to_csv(out_path, index=False, encoding='utf-8-sig')
print(f"✅ 최종 통합 파일 저장 완료: {out_path}")
