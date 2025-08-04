"""
데이터베이스 관련 모듈
- 데이터베이스 연결
- 연도별 차량대수 데이터 조회
- 신차등록 데이터 조회
- 시도별, 성별, 시군구별 차량 등록대수 조회
"""

import streamlit as st

# DB 연결 함수
def get_database_connection():
    
    return st.connection("mydb", type="sql")

# 연도별 차량대수 합계 조회
def get_year_data(conn, start_year=2017, end_year=2024):
    return conn.query(f"""
        SELECT 
            y.year_value as year,               -- 연도
            SUM(i.count) as total_count         -- 해당 연도의 총 차량대수
        FROM integrated_statistics i
        JOIN year y ON i.year_id = y.year_id    -- 연도 테이블과 조인
        WHERE y.year_value BETWEEN {start_year} AND {end_year}  -- 연도 범위 필터링
        AND i.gender_id IS NULL                 -- 성별 구분 없는 전체 데이터
        AND i.district_id IS NULL               -- 지역 구분 없는 전체 데이터
        GROUP BY y.year_value                   -- 연도별 그룹화
        ORDER BY y.year_value                   -- 연도순 정렬
    """)

# 연도별 신차등록 수 합계 조회
def get_new_car_data(conn, start_year=2017, end_year=2024):
    return conn.query(f"""
        SELECT 
            y.year_value as year,               -- 연도
            SUM(i.new_count) as new_count       -- 해당 연도의 총 신차등록 수
        FROM integrated_statistics i
        JOIN year y ON i.year_id = y.year_id    -- 연도 테이블과 조인
        WHERE y.year_value BETWEEN {start_year} AND {end_year}  -- 연도 범위 필터링
        AND i.gender_id IS NULL                 -- 성별 구분 없는 전체 데이터
        AND i.district_id IS NULL               -- 지역 구분 없는 전체 데이터
        GROUP BY y.year_value                   -- 연도별 그룹화
        ORDER BY y.year_value                   -- 연도순 정렬
    """)

# 시도별 차량 타입별 등록대수 조회
def get_city_car_data(conn, selected_year):
    return conn.query(f"""
        SELECT 
            c.city_name,                        -- 시도명
            ct.car_type_name,                   -- 차량 타입명
            SUM(i.count) as count               -- 해당 시도, 차량 타입의 등록대수
        FROM integrated_statistics i
        JOIN city c ON i.city_id = c.city_id    -- 시도 테이블과 조인
        JOIN car_type ct ON i.car_type_id = ct.car_type_id  -- 차량 타입 테이블과 조인
        JOIN year y ON i.year_id = y.year_id    -- 연도 테이블과 조인
        WHERE y.year_value = {selected_year}    -- 지정된 연도 필터링
        AND i.gender_id IS NULL                 -- 성별 구분 없는 전체 데이터
        AND i.district_id IS NULL               -- 지역 구분 없는 전체 데이터
        GROUP BY c.city_name, ct.car_type_name  -- 시도, 차량 타입별 그룹화
        ORDER BY c.city_name, ct.car_type_name  -- 시도명, 차량 타입명 순 정렬
    """)

# 시도별 성별 차량 등록대수 조회
def get_gender_city_data(conn, selected_year):
    return conn.query(f"""
        SELECT 
            c.city_name,                        -- 시도명
            g.gender_name,                      -- 성별
            SUM(i.count) as count               -- 해당 시도, 성별의 등록대수
        FROM integrated_statistics i
        JOIN city c ON i.city_id = c.city_id    -- 시도 테이블과 조인
        JOIN gender g ON i.gender_id = g.gender_id  -- 성별 테이블과 조인
        JOIN year y ON i.year_id = y.year_id    -- 연도 테이블과 조인
        WHERE y.year_value = {selected_year}    -- 지정된 연도 필터링
        AND i.district_id IS NULL               -- 지역 구분 없는 전체 데이터
        GROUP BY c.city_name, g.gender_name     -- 시도, 성별별 그룹화
        ORDER BY c.city_name, g.gender_name     -- 시도명, 성별 순 정렬
    """)

# 시도별 총 차량 등록대수 조회
def get_city_total_data(conn, selected_year):
    return conn.query(f"""
        SELECT 
            c.city_name,                        -- 시도명
            SUM(i.count) as total_count         -- 해당 시도의 총 차량 등록대수
        FROM integrated_statistics i
        JOIN city c ON i.city_id = c.city_id    -- 시도 테이블과 조인
        JOIN year y ON i.year_id = y.year_id    -- 연도 테이블과 조인
        WHERE y.year_value = {selected_year}    -- 지정된 연도 필터링
        AND i.gender_id IS NULL                 -- 성별 구분 없는 전체 데이터
        AND i.district_id IS NULL               -- 지역 구분 없는 전체 데이터
        GROUP BY c.city_name                    -- 시도별 그룹화
        ORDER BY total_count DESC               -- 등록대수 내림차순 정렬
    """)

# 시군구별 차량 등록대수 조회
def get_district_data(conn, selected_city, selected_year):
    return conn.query(f"""
        SELECT 
            c.city_name,                        -- 시도명
            d.district_name,                    -- 시군구명
            CONCAT(c.city_name, ' ', d.district_name) as city_district_key,  -- 시도+시군구 키
            SUM(i.count) as total_count         -- 해당 시군구의 총 차량 등록대수
        FROM integrated_statistics i
        JOIN city c ON i.city_id = c.city_id    -- 시도 테이블과 조인
        JOIN district d ON i.district_id = d.district_id  -- 시군구 테이블과 조인
        JOIN year y ON i.year_id = y.year_id    -- 연도 테이블과 조인
        WHERE c.city_name = '{selected_city}'   -- 지정된 시도 필터링
        AND y.year_value = {selected_year}      -- 지정된 연도 필터링
        GROUP BY c.city_name, d.district_name, CONCAT(c.city_name, ' ', d.district_name)  -- 그룹화
        ORDER BY d.district_name                -- 시군구명 순 정렬
    """)
# 시군구별 차량 타입별 등록대수 조회
def get_car_type_district_data(conn, selected_city, selected_year): 
    return conn.query(f"""
        SELECT 
            c.city_name,                        -- 시도명
            d.district_name,                    -- 시군구명
            CONCAT(c.city_name, ' ', d.district_name) as city_district_key,  -- 시도+시군구 키
            ct.car_type_name,                   -- 차량 타입명
            SUM(i.count) as count               -- 해당 시군구, 차량 타입의 등록대수
        FROM integrated_statistics i
        JOIN city c ON i.city_id = c.city_id    -- 시도 테이블과 조인
        JOIN district d ON i.district_id = d.district_id  -- 시군구 테이블과 조인
        JOIN car_type ct ON i.car_type_id = ct.car_type_id  -- 차량 타입 테이블과 조인
        JOIN year y ON i.year_id = y.year_id    -- 연도 테이블과 조인
        WHERE c.city_name = '{selected_city}'   -- 지정된 시도 필터링
        AND y.year_value = {selected_year}      -- 지정된 연도 필터링
        GROUP BY c.city_name, d.district_name, CONCAT(c.city_name, ' ', d.district_name), ct.car_type_name  -- 그룹화
        ORDER BY d.district_name, ct.car_type_name  -- 시군구명, 차량 타입명 순 정렬
    """) 