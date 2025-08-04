"""
차트 생성 관련 모듈

이 모듈은 Altair를 사용한 다양한 차트 생성 기능을 담당합니다.
- 연도별 증감률 차트 생성
- 시도별 차량 등록대수 차트 생성
- 성별 차량 등록대수 차트 생성
"""

import altair as alt

def create_growth_rate_charts(year_data, new_car_data):
    """
    연도별 증감률 차트 생성 함수
    
    Args:
        year_data (DataFrame): 연도별 차량대수 데이터
        new_car_data (DataFrame): 연도별 신차등록 데이터
    
    Returns:
        tuple: (total_combined_chart, new_car_chart, processed_year_data)
            - total_combined_chart: 차량대수와 증감률을 결합한 차트
            - new_car_chart: 신차등록 차트
            - processed_year_data: 처리된 연도별 데이터
        
    이 함수는 연도별 차량대수와 신차등록 데이터를 받아서
    증감률을 계산하고 두 개의 차트를 생성합니다.
    """
    # 데이터 유효성 검사
    if year_data.empty or new_car_data.empty:
        return None, None, None
    
    # 데이터 결합 및 처리
    # year_data와 new_car_data를 연도(year) 기준으로 병합
    year_data = year_data.merge(new_car_data, on='year', how='left')
    
    # 증감률 계산
    year_data['total_count_100k'] = year_data['total_count'] / 100000  # 십만 단위로 변환
    year_data['prev_count'] = year_data['total_count_100k'].shift(1)   # 이전 연도 데이터 (한 행씩 뒤로 이동)
    
    # 증감률 계산 공식: ((현재값 - 이전값) / 이전값) * 100
    year_data['growth_rate'] = ((year_data['total_count_100k'] - year_data['prev_count']) / year_data['prev_count'] * 100).fillna(0)
    
    # 데이터 타입 변환 및 포맷팅
    year_data['year'] = year_data['year'].astype(int)  # 연도를 정수형으로 변환
    year_data['growth_rate_display'] = year_data['growth_rate'].round(2)  # 증감률을 소수점 둘째자리까지 반올림
    
    # 차량대수 데이터 처리 (십만 단위)
    year_data['total_count_100k_int'] = (year_data['total_count'] / 100000).astype(int)  # 차량대수를 십만 단위로 변환
    year_data['new_count_100k_int'] = (year_data['new_count'] / 100000).astype(int)      # 신차등록을 십만 단위로 변환
    
    # 차량대수 및 증감률 차트용 데이터 준비
    chart_data = year_data[['year', 'total_count_100k_int', 'growth_rate_display']].copy()
    chart_data['year_int'] = chart_data['year'].astype(int)  # 연도를 정수형으로 변환
    
    # 1. 차량대수 막대 그래프 생성
    total_chart = alt.Chart(chart_data).mark_bar(color='#4C78A8').encode(
        x=alt.X('year_int:O', title='연도', axis=alt.Axis(format='d',labelAngle=0)),  # X축: 연도 (정수형, 라벨 각도 0)
        y=alt.Y('total_count_100k_int:Q', title='차량대수 (십만 대)'),                 # Y축: 차량대수 (십만 단위)
        tooltip=[  # 마우스 오버 시 표시될 툴팁
            alt.Tooltip('year_int:O', title='연도'),
            alt.Tooltip('total_count_100k_int:Q', title='차량대수 (십만 대)')
        ]
    )
    
    # 2. 증감률 선 그래프 생성
    growth_chart = alt.Chart(chart_data).mark_line(color='red', point=True, strokeWidth=3).encode(
        x=alt.X('year_int:O', title='연도'),                    # X축: 연도
        y=alt.Y('growth_rate_display:Q', title='증감률 (%)'),   # Y축: 증감률 (%)
        tooltip=[  # 마우스 오버 시 표시될 툴팁
            alt.Tooltip('year_int:O', title='연도'),
            alt.Tooltip('growth_rate_display:Q', title='증감률 (%)')
        ]
    )
    
    # 3. 차량대수와 증감률 차트 결합 (이중 Y축)
    total_combined_chart = alt.layer(total_chart, growth_chart).resolve_scale(
        y='independent'  # Y축을 독립적으로 설정 (이중 Y축)
    ).properties(
        width=600,      # 차트 너비
        height=300,     # 차트 높이
        title='차량대수 및 증감률 현황'  # 차트 제목
    )
    
    # 4. 신차등록 차트용 데이터 준비
    new_car_chart_data = year_data[['year', 'new_count_100k_int']].copy()
    new_car_chart_data['year_int'] = new_car_chart_data['year'].astype(int)
    
    # 5. 신차등록 막대 그래프 생성
    new_car_chart = alt.Chart(new_car_chart_data).mark_bar(color='#F58518').encode(
        x=alt.X('year_int:O', title='연도', axis=alt.Axis(format='d',labelAngle=0)),  # X축: 연도
        y=alt.Y('new_count_100k_int:Q', title='신차등록 (십만 대)'),                   # Y축: 신차등록 (십만 단위)
        tooltip=[  # 마우스 오버 시 표시될 툴팁
            alt.Tooltip('year_int:O', title='연도'),
            alt.Tooltip('new_count_100k_int:Q', title='신차등록 (십만 대)')
        ]
    ).properties(
        width=600,      # 차트 너비
        height=300,     # 차트 높이
        title='신차등록 현황'  # 차트 제목
    )
    
    return total_combined_chart, new_car_chart, year_data

def create_city_car_chart(city_data):
    """
    시도별 차량 등록대수 차트 생성 함수
    
    Args:
        city_data (DataFrame): 시도별 차량 타입별 등록대수 데이터
    
    Returns:
        DataFrame: 피벗 테이블 형태의 차트 데이터 (None if empty)
        
    이 함수는 시도별 차량 타입별 등록대수 데이터를 받아서
    Streamlit의 bar_chart에서 사용할 수 있는 피벗 테이블 형태로 변환합니다.
    """
    # 데이터 유효성 검사
    if city_data.empty:
        return None
    
    # 십만 단위로 변환
    city_data['count_100k'] = city_data['count'] / 100000
    
    # 피벗 테이블 생성: 시도명을 인덱스로, 차량 타입을 컬럼으로, 등록대수를 값으로
    pivot_data = city_data.pivot(index='city_name', columns='car_type_name', values='count_100k').fillna(0)
    
    # 소수점 이하 제거 (정수로 변환)
    pivot_data = pivot_data.map(lambda x: int(x))
    
    return pivot_data

def create_gender_chart(gender_city_data):
    """
    성별 차량 등록대수 차트 생성 함수
    
    Args:
        gender_city_data (DataFrame): 시도별 성별 차량 등록대수 데이터
    
    Returns:
        alt.Chart: Altair 차트 객체 (None if empty)
        
    이 함수는 시도별 성별 차량 등록대수 데이터를 받아서
    Altair를 사용한 막대 차트를 생성합니다.
    """
    # 데이터 유효성 검사
    if gender_city_data.empty:
        return None
    
    # 십만 단위로 변환
    gender_city_data['count_100k'] = gender_city_data['count'] / 100000
    
    # 피벗 테이블 생성: 시도명을 인덱스로, 성별을 컬럼으로, 등록대수를 값으로
    gender_pivot = gender_city_data.pivot(index='city_name', columns='gender_name', values='count_100k').fillna(0)
    
    # 소수점 이하 제거 (정수로 변환)
    gender_pivot = gender_pivot.map(lambda x: int(x))
    
    # Altair 차트 생성을 위한 데이터 형태 변환 (long format)
    # 피벗 테이블을 다시 long format으로 변환하여 Altair에서 사용
    gender_data_long = gender_pivot.reset_index().melt(id_vars='city_name', var_name='성별', value_name='차량대수')
    
    # 성별 색상 매핑 정의
    # 여성: 분홍색(#FF69B4), 남성: 파란색(#4169E1)
    color_scale = alt.Scale(domain=['여자', '남자'], range=['#FF69B4', '#4169E1']) 
    
    # Altair 막대 차트 생성
    chart = alt.Chart(gender_data_long).mark_bar().encode(
        x=alt.X('city_name:N', title='시'),                    # X축: 시도명 (명목형)
        y=alt.Y('차량대수:Q', title='차량대수'),                # Y축: 차량대수 (수량형)
        color=alt.Color('성별:N', scale=color_scale, title='성별'),  # 색상: 성별 (명목형, 커스텀 색상)
        tooltip=['city_name', '성별', '차량대수']               # 마우스 오버 시 표시될 툴팁
    ).properties(
        width=600,   # 차트 너비
        height=400   # 차트 높이
    )
    
    return chart 