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
    
    col1, col2, col3 = st.columns(3)
    
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
    
    with col3:
        st.markdown("#### ❓ 현대자동차 FAQ")
        st.markdown("현대자동차에 대한 자주 묻는 질문을 확인할 수 있습니다.")
        if st.button("FAQ 보기", key="btn_faq", use_container_width=True):
            change_page('hyundai_faq')

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
    import pandas as pd
    import plotly.graph_objects as go
    
    # 함수 라이브러리 import
    from common.utils import hyundai_load, Annual_total_load, selected_year
    
    # DB연동(테이블 로드)
    df_hyundai = hyundai_load() # hyundai_sale 테이블
    df_total = Annual_total_load() # 연간 자동차 등록 대수 테이블
    
    # 메인 타이틀
    col_title, col_filter = st.columns([7, 1], gap="small")
    with col_title:
        st.title("🚗 현대자동차 점유율 및 판매 추세 대시보드")
        
    # 연도 선택 버튼
    with col_filter: 
        available_years = selected_year(df_hyundai)
        selected_year = st.selectbox(
            "", 
            available_years, 
            index=len(available_years) - 1, #인덱스 오류 방지지
            format_func=lambda x: f"{x}년"
        )
        # 선택된 연도를 안전하게 숫자로 변환
        try:
            selected_year = int(selected_year)
        except (ValueError, TypeError):
            st.error("연도 데이터 형식이 올바르지 않습니다.")
            st.stop()
            
    st.markdown("---")
    
    # 연도별 판매 추세 분석
    st.header("📈 현대차 판매량 추세와 증감 분석(2017~2025)")
    
    # 전체 연도 판매량 추세 차트
    if 'year' in df_hyundai.columns and 'total_count' in df_hyundai.columns:
        # 전체 연도별 현대차 판매량 집계
        yearly_sales = df_hyundai.groupby('year')['total_count'].sum().reset_index()
        yearly_sales['판매량_만대'] = yearly_sales['total_count'] / 10000
        
        # 2025년 특별 처리 (반년간 데이터를 연간 추정치로 변환)
        if 2025 in yearly_sales['year'].values:
            # 2025년 데이터가 있으면 x2를 해서 연간 추정치로 변환
            mask_2025 = yearly_sales['year'] == 2025
            yearly_sales.loc[mask_2025, 'total_count'] = yearly_sales.loc[mask_2025, 'total_count'] * 2
            yearly_sales.loc[mask_2025, '판매량_만대'] = yearly_sales.loc[mask_2025, 'total_count'] / 10000
        
        # 차트 생성
        fig_combined = go.Figure()
        
        # 전체 연도 라인 차트
        # 2025년은 추정치 표시를 위한 텍스트 생성
        text_labels = []
        for year, sales in zip(yearly_sales['year'], yearly_sales['판매량_만대']):
            if year == 2025:
                text_labels.append(f'{sales:,.1f}만대 (추정)')
            else:
                text_labels.append(f'{sales:,.1f}만대')
        
        fig_combined.add_trace(go.Scatter(
            x=yearly_sales['year'],
            y=yearly_sales['판매량_만대'],
            mode='lines+markers',
            name='전체 연도 판매량',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8, color='#1f77b4'),
            text=text_labels,
            textposition='top center',
            textfont=dict(size=10)
        ))
        
        # 선택된 연도 강조 마커
        selected_year_data = yearly_sales[yearly_sales['year'] == selected_year]
        if not selected_year_data.empty:
            # 선택된 연도가 2025년인 경우 추정치 표시
            if selected_year == 2025:
                selected_text = f"{selected_year_data['판매량_만대'].iloc[0]:,.1f}만대 (추정)"
            else:
                selected_text = f"{selected_year_data['판매량_만대'].iloc[0]:,.1f}만대"
            
            fig_combined.add_trace(go.Scatter(
                x=selected_year_data['year'],
                y=selected_year_data['판매량_만대'],
                mode='markers',
                name=f'{selected_year}년',
                marker=dict(size=15, color='red', symbol='star'),
                text=selected_text,
                textposition='top center',
                textfont=dict(size=12, color='red', weight='bold'),
                showlegend=True
            ))
        
        # y축 범위 계산
        min_sales = yearly_sales['판매량_만대'].min()
        max_sales = yearly_sales['판매량_만대'].max()
        sales_range = max_sales - min_sales
        
        # y축 범위를 판매량 차이의 10% 정도로 설정
        y_padding = sales_range * 0.1
        y_min = max(0, min_sales - y_padding)
        y_max = max_sales + y_padding
         
        fig_combined.update_layout(
             yaxis_title="판매량 (만대)",
             xaxis_title="연도",
             height=500,
             margin=dict(t=20, b=20, l=50, r=50),  # 상하좌우 마진 줄이기
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(
                range=[y_min, y_max],
                tickformat=".1f",
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=1
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=1
            )
        )
        
        st.plotly_chart(fig_combined, use_container_width=True)
    
    # 전년도 대비 판매실적 증감율 분석
    # 1. 선택된 연도 데이터 필터링
    current_year_hyundai = df_hyundai[df_hyundai['year'] == selected_year]
    previous_year_hyundai = df_hyundai[df_hyundai['year'] == selected_year - 1]
    
    # 2. year_id 기준으로 count 합계를 구하기 
    try:
        # 해당 연도의 현대자동차 판매실적
        current_sales = current_year_hyundai['total_count'].sum() if 'total_count' in current_year_hyundai.columns else 0
        # 전년도의 현대자동차 판매실적
        previous_sales = previous_year_hyundai['total_count'].sum() if 'total_count' in previous_year_hyundai.columns else 0
        
        # 증감율 계산 (전년도 데이터가 있는 경우에만)
        if previous_sales > 0:
            if selected_year == 2025:
                # 2025년도 선택 시: 2025년 판매실적을 곱하기 2로 계산
                adjusted_current_sales = current_sales *2
                growth_rate = (( adjusted_current_sales - previous_sales) / previous_sales) * 100           
            else:
                # 다른 연도는 기존 방식대로 계산
                growth_rate = ((current_sales - previous_sales) / previous_sales) * 100
             
            # 메트릭 카드
            col1, col2, col3, col4 = st.columns(4)
             
            with col1:
                if selected_year == 2025:
                    delta_value = adjusted_current_sales - previous_sales
                    st.metric(
                         f"{selected_year}년 판매실적 (추정치)", 
                         f"{adjusted_current_sales:,}대",
                         delta=f"{delta_value:+,}대",
                         help="반년간 데이터를 기반으로 한 연간 추정치"
                    )
                else:
                     st.metric(
                         f"{selected_year}년 판매실적", 
                         f"{current_sales:,}대",
                         delta=f"{current_sales - previous_sales:+,}대"
                     )
             
            with col2:
                 st.metric(f"{selected_year-1}년 판매실적", f"{previous_sales:,}대")

            with col3:
                 st.metric("전년도 대비 증감율", f"{growth_rate:.1f}%")
            with col4:
                 trend_icon = "📈" if growth_rate > 0 else "📉" if growth_rate < 0 else "➡️"
                 st.metric("추세", f"{trend_icon} {'증가' if growth_rate > 0 else '감소' if growth_rate < 0 else '동일'}")
        else:
             # 전년도 데이터가 없는 경우 (예: 2027년)
            col1, col2, col3, col4 = st.columns(4)
             
            with col1:
                if selected_year == 2025:
                     adjusted_current_sales = current_sales * 2
                     st.metric(
                         f"{selected_year}년 판매실적 (추정치)", 
                         f"{adjusted_current_sales:,}대",
                         help="반년간 데이터를 기반으로 한 연간 추정치"
                     )
                else:
                     st.metric(f"{selected_year}년 판매실적", f"{current_sales:,}대")
             
            with col2:
                 st.metric(f"{selected_year-1}년 판매실적", "-")
             
            with col3:
                 st.metric("전년도 대비 증감율", "-")
             
            with col4:
                 st.metric("추세", "-")
                  
    except Exception as e:
        st.error(f"❌ 판매실적 계산 실패: {str(e)}")
        st.stop()
    
    # 국내판매 vs 해외판매 분석
    st.markdown("---")
    st.header(f"🔵 {selected_year}년 상세분석")
    
    # 국내판매와 해외판매 데이터 확인 및 분석
    if not current_year_hyundai.empty:
        # domestic_count와 export_count 컬럼이 있는지 확인
        has_domestic = 'domestic_count' in current_year_hyundai.columns
        has_export = 'export_count' in current_year_hyundai.columns
        
        if has_domestic and has_export:
            # 국내판매와 해외판매 합계 계산
            domestic_sales = current_year_hyundai['domestic_count'].sum()
            export_sales = current_year_hyundai['export_count'].sum()
            total_sales = domestic_sales + export_sales
            
            # 전년도 국내/해외 판매량 계산
            prev_domestic_sales = previous_year_hyundai['domestic_count'].sum() if 'domestic_count' in previous_year_hyundai.columns else 0
            prev_export_sales = previous_year_hyundai['export_count'].sum() if 'export_count' in previous_year_hyundai.columns else 0
            
            # 증감율 계산 (2025년은 2배로 계산)
            if selected_year == 2025:
                adjusted_domestic_sales = domestic_sales * 2
                adjusted_export_sales = export_sales * 2
                domestic_growth = ((adjusted_domestic_sales - prev_domestic_sales) / prev_domestic_sales * 100) if prev_domestic_sales > 0 else 0
                export_growth = ((adjusted_export_sales - prev_export_sales) / prev_export_sales * 100) if prev_export_sales > 0 else 0
            else:
                domestic_growth = ((domestic_sales - prev_domestic_sales) / prev_domestic_sales * 100) if prev_domestic_sales > 0 else 0
                export_growth = ((export_sales - prev_export_sales) / prev_export_sales * 100) if prev_export_sales > 0 else 0
           

            # 파이 차트와 메트릭 카드를 나란히 배치
            col_chart, col_metrics = st.columns([1, 1])
            with col_chart:
                fig_pie = go.Figure()
                 
                fig_pie.add_trace(go.Pie(
                    labels=['국내판매', '해외판매'],
                    values=[domestic_sales, export_sales],
                    hole=0.4,
                    marker_colors=['#61A4BC', '#5B7DB1'],
                    textinfo='label',
                    textposition='inside',
                    textfont=dict(size=20, color='white')
                ))
                 
                fig_pie.update_layout(
                      title=f"{selected_year}년 국내판매 vs 해외판매 비율",
                      height=400,
                      showlegend=True,
                      legend=dict(
                          orientation="h",
                          yanchor="top",
                          y=-0.15,
                          xanchor="center",
                          x=0.5
                      ),
                      margin=dict(t=50, b=80, l=50, r=50)
                  )
                 
                st.plotly_chart(fig_pie, use_container_width=True)
                 
                with col_metrics:
                     row2_co1, row2_col2= st.columns(2) 
                     with row2_co1:
                          if selected_year == 2025:
                              st.metric(
                                  "국내판매", 
                                  f"{domestic_sales:,}대",
                              )
                          else:
                              st.metric(
                                  "국내판매", 
                                  f"{domestic_sales:,}대"
                              )
                     with row2_col2:
                          if selected_year == 2025:
                              st.metric(
                                  "해외판매", 
                                  f"{export_sales:,}대",
                              )
                          else:
                              st.metric(
                                  "해외판매", 
                                  f"{export_sales:,}대"
                              )
                     
                     # 전년도 대비 증감율 메트릭 카드
                     row3_co1, row3_col2= st.columns(2)
                     with row3_co1:
                          if selected_year == 2025:
                              st.metric(
                                  "전년도 대비 국내 증감율",
                                  f"{domestic_growth:+.1f}%",
                                  help="반년간 데이터를 기반으로 한 추정치로 계산된 증감율"
                              )
                          else:
                              st.metric(
                                  "전년도 대비 국내 증감율",
                                  f"{domestic_growth:+.1f}%"
                              )
                     with row3_col2:
                          if selected_year == 2025:
                              st.metric(
                                  "전년도 대비 해외 증감율",
                                  f"{export_growth:+.1f}%",
                                  help="반년간 데이터를 기반으로 한 추정치로 계산된 증감율"
                              )
                          else:
                              st.metric(
                                  "전년도 대비 해외 증감율",
                                  f"{export_growth:+.1f}%"
                              )
    
    # 차종별 판매 분석
    if not current_year_hyundai.empty and 'car_name' in current_year_hyundai.columns and 'total_count' in current_year_hyundai.columns:
        # car_name이 있는 데이터만 필터링
        car_data = current_year_hyundai[
            current_year_hyundai['car_name'].notna() & 
            (current_year_hyundai['car_name'] != '')
        ]
        
        if not car_data.empty:
            
             # 차종별 판매량 집계
             model_sales = car_data.groupby('car_name')['total_count'].sum().sort_values(ascending=False)
             top_3_models = model_sales.head(3)
             total_sales = model_sales.sum()
             # 상세 정보 표시
            
             if total_sales > 0:
                # 각 차종의 비율 계산
                model_percentages = {}
                for model, sales in top_3_models.items():
                    percentage = (sales / total_sales) * 100
                    model_percentages[model] = percentage
                
                
                # 상위 3개 차종과 기타를 포함한 하나의 도넛 차트
                fig_donut = go.Figure()
                
                # 상위 3개 차종 데이터 준비
                top_3_labels = list(model_percentages.keys())
                top_3_values = list(model_percentages.values())
                
                # 기타 차종 비율 계산
                others_percentage = 100 - sum(top_3_values)
                
                # 전체 라벨과 값 준비
                all_labels = top_3_labels + ['기타']
                all_values = top_3_values + [others_percentage]
                
                # 색상 설정 (상위 3개 + 기타)
                colors = ['#ffeDCD', '#ffdead', '#deb887', '#e6e6fa']
                
                fig_donut.add_trace(go.Pie(
                    labels=all_labels,
                    values=all_values,
                    hole=0.4,
                    marker_colors=colors,
                    textinfo='label+percent',
                    textposition='inside',
                    textfont=dict(size=16, color='black'),
                    hoverinfo='label+percent+value'
                ))
                
                # 중앙에 총 판매량 표시
                fig_donut.add_annotation(
                    text=f"총 판매량<br>{total_sales:,}대",
                    x=0.5, y=0.5,
                    xref='paper', yref='paper',
                    showarrow=False,
                    font=dict(size=16, color='black', weight='bold'),
                    align='center'
                )
                
                fig_donut.update_layout(
                     title=f"{selected_year}년 상위 3개 차종 판매 비중",
                     height=500,
                     showlegend=True,
                     legend=dict(
                         orientation="h",
                         yanchor="top",
                         y=-0.15,
                         xanchor="center",
                         x=0.5
                     ),
                     margin=dict(t=50, b=80, l=50, r=50)
                 )
                
    # 판매 비중 차트와 차종 변화 분석을 나란히 배치
                col_chart, col_analysis = st.columns([1, 1])
                with col_chart:
                     st.plotly_chart(fig_donut, use_container_width=True)

                with col_analysis:
                     # 전년도와 비교하여 새로 출시된 차종과 단종된 차종 분석
                    if not previous_year_hyundai.empty and 'car_name' in previous_year_hyundai.columns:
                         # 전년도 차종별 판매량 집계
                         prev_car_data = previous_year_hyundai[
                             previous_year_hyundai['car_name'].notna() & 
                             (previous_year_hyundai['car_name'] != '')
                         ]
                         
                         if not prev_car_data.empty:
                             prev_model_sales = prev_car_data.groupby('car_name')['total_count'].sum()
                             
                             # 현재 연도와 전년도 차종 비교
                             current_models = set(model_sales.index)
                             previous_models = set(prev_model_sales.index)
                             
                             # 새로 출시된 차종
                             new_models = current_models - previous_models
                             # 단종된 차종
                             discontinued_models = previous_models - current_models
                             
                             # 분석 결과 표시
                             st.subheader(f"✅ {selected_year}년 vs {selected_year-1}년 차종 변화 분석")
                             
                             
                             
                             if new_models:
                                  st.text("🆕 신규 출시 차종")
                                  new_sales_data = []
                                  for model in new_models:
                                      sales = model_sales[model]
                                      percentage = (sales / total_sales) * 100
                                      
                                      # 국내/해외 판매 정보 추가
                                      model_data = car_data[car_data['car_name'] == model]
                                      domestic_sales_model = model_data['domestic_count'].sum() if 'domestic_count' in model_data.columns else 0
                                      export_sales_model = model_data['export_count'].sum() if 'export_count' in model_data.columns else 0
                                      
                                      # 판매 지역 판단
                                      if domestic_sales_model > 0 and export_sales_model > 0:
                                          market_type = "국내+해외"
                                      elif domestic_sales_model > 0:
                                          market_type = "국내전용"
                                      elif export_sales_model > 0:
                                          market_type = "해외전용"
                                      else:
                                          market_type = "미분류"
                                      
                                      new_sales_data.append({
                                          '차종': model,
                                          '판매량': sales,
                                          '판매지역': market_type
                                      })
                                  
                                  # 새로 출시된 차종 테이블
                                  new_df = pd.DataFrame(new_sales_data)
                                  new_df = new_df.sort_values('판매량', ascending=False)
                                  st.dataframe(
                                      new_df.style.format({
                                          '판매량': '{:,}대',
                               
                                      }),
                                      use_container_width=True
                                  )
                             else:
                                st.info("🆕 **새로 출시된 차종**: 없음")
                                
                             
                             if discontinued_models:
                                  st.text("❌ 단종 차종")
                                  discontinued_sales_data = []
                                  for model in discontinued_models:
                                      sales = prev_model_sales[model]
                                      prev_total = prev_model_sales.sum()
                                      percentage = (sales / prev_total) * 100 if prev_total > 0 else 0
                                      
                                      # 전년도 국내/해외 판매 정보 추가
                                      prev_model_data = prev_car_data[prev_car_data['car_name'] == model]
                                      prev_domestic_sales_model = prev_model_data['domestic_count'].sum() if 'domestic_count' in prev_model_data.columns else 0
                                      prev_export_sales_model = prev_model_data['export_count'].sum() if 'export_count' in prev_model_data.columns else 0
                                      
                                      # 판매 지역 판단
                                      if prev_domestic_sales_model > 0 and prev_export_sales_model > 0:
                                          prev_market_type = "국내+해외"
                                      elif prev_domestic_sales_model > 0:
                                          prev_market_type = "국내전용"
                                      elif prev_export_sales_model > 0:
                                          prev_market_type = "해외전용"
                                      else:
                                          prev_market_type = "미분류"
                                      
                                      discontinued_sales_data.append({
                                          '차종': model,
                                          '전년도 판매량': sales,
                                          '전년도 판매지역': prev_market_type
                                      })
                                  
                                  # 단종된 차종 테이블
                                  discontinued_df = pd.DataFrame(discontinued_sales_data)
                                  discontinued_df = discontinued_df.sort_values('전년도 판매량', ascending=False)
                                  st.dataframe(
                                      discontinued_df.style.format({
                                          '전년도 판매량': '{:,}대',
                                          '전년도 비율': '{:.1f}%',
                                          
                                      }),
                                      use_container_width=True
                                  )
                             else:
                                st.info("❌ **단종된 차종**: 없음")
                                
                             
                             # 변화 요약 메트릭
                             st.subheader("✅ 차종 변화 요약")
                             col1, col2 = st.columns(2)
                             
                             with col1:
                                 st.metric(
                                     "현재 차종 수", 
                                     f"{len(current_models)}개",
                                     delta=f"{len(current_models) - len(previous_models):+d}개"
                                 )
                             
                             with col2:
                                 st.metric(
                                     "전년도 차종 수", 
                                     f"{len(previous_models)}개"
                                 )
                         else:
                             st.info("📊 **차종 변화 분석**: 전년도 데이터가 없습니다.")
                    else:
                         st.info("📊 **차종 변화 분석**: 전년도 데이터가 없습니다.")
    
    # 현대자동차 점유율 분석
    st.markdown("---")
    st.header("📈 연도별 현대자동차 점유율 분석")
    # 전체 연도별 점유율 계산
    if not df_hyundai.empty and not df_total.empty:
        # 연도별 현대차 판매실적과 전체 등록현황 계산
        yearly_market_share = []
        
        for year in sorted(df_hyundai['year'].unique()):
            # 해당 연도의 현대차 판매실적
            year_hyundai = df_hyundai[df_hyundai['year'] == year]
            hyundai_sales = year_hyundai['domestic_count'].sum() if 'domestic_count' in year_hyundai.columns else 0
            
            # 해당 연도의 전체 신차 등록현황
            year_total = df_total[df_total['year'] == year]
            total_new_count = year_total['new_count'].sum() if 'new_count' in year_total.columns else 0
            
            # 점유율 계산
            market_share = (hyundai_sales / total_new_count) * 100 if total_new_count > 0 else 0
            
            yearly_market_share.append({
                'year': year,
                'hyundai_sales': hyundai_sales,
                'total_new_count': total_new_count,
                'market_share': market_share
            })
        
        # 점유율 데이터프레임 생성
        market_share_df = pd.DataFrame(yearly_market_share)
        
        if not market_share_df.empty:
            # 연도별 점유율 라인 차트 생성
            fig_market_share = go.Figure()
            
            # 점유율 라인 차트
            fig_market_share.add_trace(go.Scatter(
                x=market_share_df['year'],
                y=market_share_df['market_share'],
                mode='lines+markers',
                name='현대자동차 점유율',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8, color='#1f77b4'),
                text=[f"{share:.1f}%" for share in market_share_df['market_share']],
                textposition='top center',
                textfont=dict(size=10),
                hovertemplate='%{y:.1f}%<extra></extra>'
            ))
            
            # 선택된 연도 강조 마커
            selected_year_data = market_share_df[market_share_df['year'] == selected_year]
            if not selected_year_data.empty:
                selected_share = selected_year_data['market_share'].iloc[0]
                fig_market_share.add_trace(go.Scatter(
                    x=[selected_year],
                    y=[selected_share],
                    mode='markers',
                    name=f'{selected_year}년',
                    marker=dict(size=15, color='red', symbol='star'),
                    text=f"{selected_share:.1f}%",
                    textposition='top center',
                    textfont=dict(size=12, color='red', weight='bold'),
                    showlegend=True,
                    hovertemplate='%{y:.1f}%<extra></extra>'
                ))
            
            # y축 범위 계산
            min_share = market_share_df['market_share'].min()
            max_share = market_share_df['market_share'].max()
            share_range = max_share - min_share
            
            # y축 범위를 점유율 차이의 10% 정도로 설정
            y_padding = share_range * 0.1
            y_min = max(0, min_share - y_padding)
            y_max = min(100, max_share + y_padding)
            
            fig_market_share.update_layout(
                title="연도별 현대자동차 점유율 추이",
                yaxis_title="점유율 (%)",
                xaxis_title="연도",
                height=500,
                margin=dict(t=20, b=20, l=50, r=50),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                yaxis=dict(
                    range=[y_min, y_max],
                    tickformat=".1f",
                    showgrid=True,
                    gridcolor='lightgray',
                    gridwidth=1
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='lightgray',
                    gridwidth=1
                )
            )
            
            st.plotly_chart(fig_market_share, use_container_width=True)
            
            # 선택된 연도의 상세 분석
            st.subheader(f"🔵 {selected_year}년 현대자동차 점유율 상세 분석")
            
            if not selected_year_data.empty:
                selected_data = selected_year_data.iloc[0]
                hyundai_sales = selected_data['hyundai_sales']
                total_new_count = selected_data['total_new_count']
                market_share = selected_data['market_share']
                other_share = 100 - market_share
                
                # 메트릭 카드
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("현대차 판매실적", f"{int(hyundai_sales):,}대")
                with col2:
                    st.metric("전체 신차 등록현황", f"{int(total_new_count):,}대")
                with col3:
                    st.metric("현대차 점유율", f"{market_share:.1f}%")
                with col4:
                    st.metric("기타 제조사", f"{other_share:.1f}%")
                
                fig_stack = go.Figure()
            