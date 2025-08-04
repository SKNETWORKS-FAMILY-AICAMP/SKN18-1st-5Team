import streamlit as st
import pandas as pd

####### hyundai_sale 테이블 로드(year테이블과 조인) ########
conn = st.connection("mydb", type="sql", autocommit=True)
def hyundai_load():
    query_hyundai = """
    SELECT h.*, y.year_value as year 
    FROM hyundai_sale h
    JOIN year y ON h.year_id = y.year_id
    """
    return conn.query(query_hyundai)

### integrated_statistics 테이블에서 연도별 자동차 등록현황 로드 ###
def Annual_total_load():
    query_total = """
    SELECT y.year_value as year, SUM(i.new_count) as new_count
    FROM integrated_statistics i
    JOIN year y ON i.year_id = y.year_id
    WHERE i.gender_id IS NULL 
    and i.district_id IS NULL
    GROUP BY y.year_value
    ORDER BY y.year_value
    """
    return conn.query(query_total)  

#### 연도 선택 #####
def selected_year(df_hyundai):
    try:
        if 'year' in df_hyundai.columns:
            # year 컬럼을 숫자로 변환 (안전하게)
            df_hyundai['year'] = pd.to_numeric(df_hyundai['year'], errors='coerce')
            available_years = sorted(df_hyundai['year'].dropna().unique()) 
        else:
            st.error("데이터에 연도 정보가 없습니다.")
            st.stop()

    except Exception as e:
        st.error(f"❌ 연도 데이터 처리 실패: {str(e)}")
        st.stop()  
    return available_years

##### 증감율 계산 ######

