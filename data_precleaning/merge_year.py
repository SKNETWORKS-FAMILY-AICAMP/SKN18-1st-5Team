import pandas as pd
import numpy as np
import os

sheetnumber=3

# 데이터가 저장된 폴더 경로 설정
for year in range(2024,2016,-1):
    folder_path = f"C:\\dev\\mini_1\\data\\{year}\\{year}_{sheetnumber}번"
    # 1번 시트 17개 지역 × 4개 용도별 데이터를 누적할 0으로 초기화된 행렬 생성
    # 3번 시트 2개 성별 x 17개 지역별 데이터를 누적할 0으로 초기화된 행렬 생성
    sum_matrix = np.zeros((2, 17))

    # 처리한 파일 수를 세기 위한 변수 초기화
    file_count = 0

    # 폴더 내 모든 파일을 하나씩 순회
    for filename in os.listdir(folder_path):
        # 확장자가 .xlsx이고 임시파일(~$)이 아닌 경우만 처리
        if filename.endswith(".xlsx") and not filename.startswith("~$"):
            # 파일의 전체 경로 생성
            file_path = os.path.join(folder_path, filename)
            print(f"\n📂 처리 중: {filename}")

            try:
                # 1번시트 엑셀 파일의 '01.통계표' 시트에서 B~E열 데이터 읽기
                # 3번시트 엑셀 파일의 '04.성별_연령별' 시트에서 B~R열 데이터 읽기
                # header=None: 데이터에 컬럼명이 없음을 명시
                # skiprows=1: 첫 행을 건너뛰고 두 번째 행부터 데이터 읽기
                # 1번 시트 nrows=17: 17행만 읽기 (지역 개수와 맞춤)
                # 3번 시트 nrows=2: 2행만 읽기(성별 개수와 맞춤춤)
                df = pd.read_excel(
                    file_path,
                    sheet_name="04.성별_연령별",
                    usecols="B:R",
                    header=None,
                    skiprows=1,
                    nrows=2
                )

                # 읽어온 데이터의 형태 출력 (행, 열 개수)
                print(f"파일: {filename} 데이터 shape: {df.shape}")
                # 상위 5행 데이터 출력으로 내용 확인
                print(df.head())

                # 모든 데이터를 숫자형으로 변환, 변환 불가능한 값은 NaN 처리 후 0으로 대체
                df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

                #1번시트 읽은 데이터가 (17행, 4열)인지 확인하여 일치할 때만 누적 합산
                #3번시트 읽은 데이터가 (2행, 17열)인지 확인하여 일치할 때만 누적 합산
                if df.shape == (2, 17):
                    sum_matrix += df.to_numpy()  # 위치별 값 누적
                    file_count += 1              # 처리된 파일 수 증가
                else:
                    # 데이터 크기가 맞지 않을 경우 경고 출력 및 해당 파일 건너뜀
                    print(f"⚠️ 데이터 행/열 수 불일치, 건너뜀: {df.shape}")

            except Exception as e:
                # 예외 발생 시 에러 메시지 출력하고 다음 파일로 넘어감
                print(f"⚠️ 오류 발생 {filename}: {e}")

    # 17개 지역명을 리스트로 정의 (엑셀 데이터와 순서 일치 필요)
    지역 = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
            '경기', '충북', '충남', '전남', '경북', '경남', '제주', '강원', '전북']

    # 3번 시트: 성별 컬럼명 리스트
    성별 = ['남자', '여자']

    # 누적한 행렬을 데이터프레임으로 변환하고, 지역명 컬럼을 가장 앞에 삽입
    result_df = pd.DataFrame(sum_matrix, columns=지역)
    result_df.insert(0, '성별', 성별)  # 성별 컬럼을 첫 번째에 삽입

    # 처리한 파일 수 출력
    print(f"\n📌 총 처리 파일 수: {file_count}")

    # 누적 결과 데이터프레임 전체 출력 (인덱스 제외)
    print("\n🎯 최종 누적 결과:")
    print(result_df.to_string(index=False))

    # 누적 결과를 CSV 파일로 저장 (한글 깨짐 방지용 utf-8 인코딩 사용)
    result_df.to_csv(f"C:\\dev\\mini_1\\data\\{year}\\{year}_시군구.csv", index=False, encoding="utf-8")