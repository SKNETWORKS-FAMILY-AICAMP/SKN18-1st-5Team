"""
페이지 렌더링 관련 모듈
"""

import streamlit as st
from streamlit_folium import st_folium

# 모듈 import
from config import change_page
from database import (
    get_database_connection, get_year_data, get_new_car_data,
    get_city_car_data, get_gender_city_data, get_city_total_data,
    get_district_data, get_car_type_district_data
)
from charts import create_growth_rate_charts, create_city_car_chart, create_gender_chart
from maps import create_national_map, create_city_detail_map

def render_main_page():
    """메인 페이지 렌더링"""
    st.title("🚗 자동차 등록 현황 대시보드")
    
    st.markdown("### 📋 메인 메뉴")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 전국 자동차 등록 현황")
        st.markdown("전국의 자동차 등록 현황을 확인할 수 있습니다.")
        if st.button("전국 현황 보기", key="btn_national", use_container_width=True):
            change_page('national')
    
    with col2:
        st.markdown("#### 🏢 현대 자동차 등록 현황")
        st.markdown("현대 자동차의 등록 현황을 확인할 수 있습니다.")
        if st.button("현대 현황 보기", key="btn_hyundai", use_container_width=True):
            change_page('hyundai')

def render_national_page():
    """전국 현황 페이지 렌더링"""
    # 제목과 연도 선택을 한 줄에 배치
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("📊 전국 자동차 등록 현황")
    
    with col2:
        selected_year = st.selectbox("연도 선택", [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024])
    
    try:
        conn = get_database_connection()
        
        # 1. 연도별 차량대수 증감률 & 신차등록 그래프
        st.header("📈 연도별 차량대수 증감률 (2017~2024)")
        
        year_data = get_year_data(conn)
        new_car_data = get_new_car_data(conn)
        
        total_chart, new_car_chart, processed_year_data = create_growth_rate_charts(year_data, new_car_data)
        
        if total_chart and new_car_chart:
            st.altair_chart(total_chart, use_container_width=True)
            st.caption("차량대수: 십만 대, 증감률: %")
            
            # 그래프 사이 간격 추가
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.altair_chart(new_car_chart, use_container_width=True)
            st.caption("신차등록: 십만 대")
            
            # 그래프와 표 사이 간격 추가
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 연도별 차량대수와 신차등록 표
            if not processed_year_data.empty:
                processed_year_data['year_formatted'] = processed_year_data['year'].astype(str)
                processed_year_data['total_count_formatted'] = processed_year_data['total_count'].apply(lambda x: f"{int(x):,}")
                processed_year_data['new_count_formatted'] = processed_year_data['new_count'].apply(lambda x: f"{int(x):,}")
                
                def icon_html(val):
                    if val > 0:
                        return '<span style="color:red;">▲</span> ' + f'{val:.2f}'
                    elif val < 0:
                        return '<span style="color:blue;">▼</span> ' + f'{val:.2f}'
                    else:
                        return f'{val:.2f}'
                
                processed_year_data['growth_rate_icon'] = processed_year_data['growth_rate_display'].apply(icon_html)
                
                st.markdown(
                    processed_year_data[['year_formatted', 'total_count_formatted', 'new_count_formatted', 'growth_rate_icon']]
                    .rename(columns={'year_formatted': '연도', 'total_count_formatted': '차량대수', 'new_count_formatted': '신차등록', 'growth_rate_icon': '증감률(%)'})
                    .to_html(escape=False, index=False), unsafe_allow_html=True
                )
        
        # 2. 상세 분석
        st.markdown(f"#### 📊 {selected_year}년 상세 분석")
        
        # 시도별 차량 등록대수
        st.markdown("##### 🗺️ 광역자치단체의 차량별 등록대수")
        city_data = get_city_car_data(conn, selected_year)
        city_chart = create_city_car_chart(city_data)
        
        if city_chart is not None:
            st.bar_chart(city_chart)
            st.caption("단위: 십만 대")
        
        # 그래프 사이 간격 추가
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 성별 차량 등록대수
        st.markdown("##### 👥 광역자치단체의 성별별 차량 등록대수")
        gender_city_data = get_gender_city_data(conn, selected_year)
        gender_chart = create_gender_chart(gender_city_data)
        
        if gender_chart is not None:
            st.altair_chart(gender_chart, use_container_width=True)
            st.caption("단위: 십만 대")
        
        # 상세 분석과 지도 사이 간격 추가
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3. 지도 시각화
        st.markdown(f"#### 🗺️ {selected_year}년 광역자치단체와 기초자치단체의 지도")
        
        city_total_data = get_city_total_data(conn, selected_year)
        city_total_dict = dict(zip(city_total_data['city_name'], city_total_data['total_count']))
        
        # 세션 상태로 선택된 시 관리
        if 'selected_city_for_map' not in st.session_state:
            st.session_state.selected_city_for_map = None
        
        # 지도 2열 레이아웃
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**🗺️ 광역자치단체의 차량 등록대수**")
            m_korea = create_national_map(city_total_dict)
            st_folium(m_korea, returned_objects=[])
        
        with col2:
            st.markdown("**🗺️ 기초자치 단체의 차량 대수 현황 지도**")
            
            # 시 선택 드롭다운
            available_cities = list(city_total_dict.keys())
            selected_city_dropdown = st.selectbox(
                "광역자치단체 선택",
                options=["광역자치단체를 선택하세요"] + available_cities,
                index=0
            )
            
            if selected_city_dropdown != "광역자치단체를 선택하세요":
                st.session_state.selected_city_for_map = selected_city_dropdown
                st.success(f"✅ {selected_city_dropdown} 선택됨")
            
            if st.session_state.selected_city_for_map:
                selected_city = st.session_state.selected_city_for_map
                st.markdown(f"**🗺️ {selected_city} 광역자치단체의 기초자치단체 지도**")
                
                district_data = get_district_data(conn, selected_city, selected_year)
                car_type_district_data = get_car_type_district_data(conn, selected_city, selected_year)
                
                m = create_city_detail_map(selected_city, district_data, car_type_district_data, selected_year)
                
                if m:
                    st_folium(m, returned_objects=[])
                else:
                    st.info(f"📊 {selected_city}의 데이터가 없습니다.")
            else:
                st.info("👆 위에서 시를 선택하면 상세 지도가 표시됩니다.")
        
    except Exception as e:
        st.error(f"❌ 데이터 조회 실패: {str(e)}")

def render_hyundai_page():
    """현대 현황 페이지 렌더링"""
    st.markdown("### 🏢 현대 자동차 등록 현황")