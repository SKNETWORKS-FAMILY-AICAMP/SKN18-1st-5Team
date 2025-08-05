# 자동차 등록 현황 대시보드

import streamlit as st
from streamlit_folium import st_folium
import altair as alt
import folium
import json

# ============================================================================
# 데이터베이스 관련 함수들
# ============================================================================

def get_database_connection():
    """데이터베이스 연결"""
    return st.connection("mydb", type="sql")

def get_year_data(conn, start_year=2017, end_year=2024):
    """연도별 차량대수 합계 조회"""
    return conn.query(f"""
        SELECT 
            y.year_value as year,
            SUM(i.count) as total_count
        FROM integrated_statistics i
        JOIN year y ON i.year_id = y.year_id
        WHERE y.year_value BETWEEN {start_year} AND {end_year}
        AND i.gender_id IS NULL
        AND i.district_id IS NULL
        GROUP BY y.year_value
        ORDER BY y.year_value
    """)

def get_new_car_data(conn, start_year=2017, end_year=2024):
    """연도별 신차등록 수 합계 조회"""
    return conn.query(f"""
        SELECT 
            y.year_value as year,
            SUM(i.new_count) as new_count
        FROM integrated_statistics i
        JOIN year y ON i.year_id = y.year_id
        WHERE y.year_value BETWEEN {start_year} AND {end_year}
        AND i.gender_id IS NULL
        AND i.district_id IS NULL
        GROUP BY y.year_value
        ORDER BY y.year_value
    """)

def get_city_car_data(conn, selected_year):
    """시도별 차량 타입별 등록대수 조회"""
    return conn.query(f"""
        SELECT 
            c.city_name,
            ct.car_type_name,
            SUM(i.count) as count
        FROM integrated_statistics i
        JOIN city c ON i.city_id = c.city_id
        JOIN car_type ct ON i.car_type_id = ct.car_type_id
        JOIN year y ON i.year_id = y.year_id
        WHERE y.year_value = {selected_year}
        AND i.gender_id IS NULL
        AND i.district_id IS NULL
        GROUP BY c.city_name, ct.car_type_name
        ORDER BY c.city_name, ct.car_type_name
    """)

def get_gender_city_data(conn, selected_year):
    """시도별 성별 차량 등록대수 조회"""
    return conn.query(f"""
        SELECT 
            c.city_name,
            g.gender_name,
            SUM(i.count) as count
        FROM integrated_statistics i
        JOIN city c ON i.city_id = c.city_id
        JOIN gender g ON i.gender_id = g.gender_id
        JOIN year y ON i.year_id = y.year_id
        WHERE y.year_value = {selected_year}
        AND i.district_id IS NULL
        GROUP BY c.city_name, g.gender_name
        ORDER BY c.city_name, g.gender_name
    """)

def get_city_total_data(conn, selected_year):
    """시도별 총 차량 등록대수 조회"""
    return conn.query(f"""
        SELECT 
            c.city_name,
            SUM(i.count) as total_count
        FROM integrated_statistics i
        JOIN city c ON i.city_id = c.city_id
        JOIN year y ON i.year_id = y.year_id
        WHERE y.year_value = {selected_year}
        AND i.gender_id IS NULL
        AND i.district_id IS NULL
        GROUP BY c.city_name
        ORDER BY total_count DESC
    """)

def get_district_data(conn, selected_city, selected_year):
    """시군구별 차량 등록대수 조회"""
    return conn.query(f"""
        SELECT 
            c.city_name,
            d.district_name,
            CONCAT(c.city_name, ' ', d.district_name) as city_district_key,
            SUM(i.count) as total_count
        FROM integrated_statistics i
        JOIN city c ON i.city_id = c.city_id
        JOIN district d ON i.district_id = d.district_id
        JOIN year y ON i.year_id = y.year_id
        WHERE c.city_name = '{selected_city}'
        AND y.year_value = {selected_year}
        GROUP BY c.city_name, d.district_name, CONCAT(c.city_name, ' ', d.district_name)
        ORDER BY d.district_name
    """)

def get_car_type_district_data(conn, selected_city, selected_year):
    """시군구별 차량 타입별 등록대수 조회"""
    return conn.query(f"""
        SELECT 
            c.city_name,
            d.district_name,
            CONCAT(c.city_name, ' ', d.district_name) as city_district_key,
            ct.car_type_name,
            SUM(i.count) as count
        FROM integrated_statistics i
        JOIN city c ON i.city_id = c.city_id
        JOIN district d ON i.district_id = d.district_id
        JOIN car_type ct ON i.car_type_id = ct.car_type_id
        JOIN year y ON i.year_id = y.year_id
        WHERE c.city_name = '{selected_city}'
        AND y.year_value = {selected_year}
        GROUP BY c.city_name, d.district_name, CONCAT(c.city_name, ' ', d.district_name), ct.car_type_name
        ORDER BY d.district_name, ct.car_type_name
    """)

# ============================================================================
# 차트 생성 함수들
# ============================================================================

def create_growth_rate_charts(year_data, new_car_data):
    """연도별 증감률 차트 생성"""
    if year_data.empty or new_car_data.empty:
        return None, None, None
    
    # 데이터 결합 및 처리
    year_data = year_data.merge(new_car_data, on='year', how='left')
    
    # 증감률 계산
    year_data['total_count_100k'] = year_data['total_count'] / 100000
    year_data['prev_count'] = year_data['total_count_100k'].shift(1)
    year_data['growth_rate'] = ((year_data['total_count_100k'] - year_data['prev_count']) / year_data['prev_count'] * 100).fillna(0)
    
    # 데이터 타입 변환 및 포맷팅
    year_data['year'] = year_data['year'].astype(int)
    year_data['growth_rate_display'] = year_data['growth_rate'].round(2)
    year_data['total_count_100k_int'] = (year_data['total_count'] / 100000).astype(int)
    year_data['new_count_100k_int'] = (year_data['new_count'] / 100000).astype(int)
    
    # 차트용 데이터 준비
    chart_data = year_data[['year', 'total_count_100k_int', 'growth_rate_display']].copy()
    chart_data['year_int'] = chart_data['year'].astype(int)
    
    # 차량대수 막대 그래프
    total_chart = alt.Chart(chart_data).mark_bar(color='#4C78A8').encode(
        x=alt.X('year_int:O', title='연도', axis=alt.Axis(format='d',labelAngle=0)),
        y=alt.Y('total_count_100k_int:Q', title='차량대수 (십만 대)'),
        tooltip=[
            alt.Tooltip('year_int:O', title='연도'),
            alt.Tooltip('total_count_100k_int:Q', title='차량대수 (십만 대)')
        ]
    )
    
    # 증감률 선 그래프
    growth_chart = alt.Chart(chart_data).mark_line(color='red', point=True, strokeWidth=3).encode(
        x=alt.X('year_int:O', title='연도'),
        y=alt.Y('growth_rate_display:Q', title='증감률 (%)'),
        tooltip=[
            alt.Tooltip('year_int:O', title='연도'),
            alt.Tooltip('growth_rate_display:Q', title='증감률 (%)')
        ]
    )
    
    # 차량대수와 증감률 차트 결합
    total_combined_chart = alt.layer(total_chart, growth_chart).resolve_scale(
        y='independent'
    ).properties(
        width=600,
        height=300,
        title='차량대수 및 증감률 현황'
    )
    
    # 신차등록 차트
    new_car_chart_data = year_data[['year', 'new_count_100k_int']].copy()
    new_car_chart_data['year_int'] = new_car_chart_data['year'].astype(int)
    
    new_car_chart = alt.Chart(new_car_chart_data).mark_bar(color='#F58518').encode(
        x=alt.X('year_int:O', title='연도', axis=alt.Axis(format='d',labelAngle=0)),
        y=alt.Y('new_count_100k_int:Q', title='신차등록 (십만 대)'),
        tooltip=[
            alt.Tooltip('year_int:O', title='연도'),
            alt.Tooltip('new_count_100k_int:Q', title='신차등록 (십만 대)')
        ]
    ).properties(
        width=600,
        height=300,
        title='신차등록 현황'
    )
    
    return total_combined_chart, new_car_chart, year_data

def create_city_car_chart(city_data):
    """시도별 차량 등록대수 차트 생성"""
    if city_data.empty:
        return None
    
    city_data['count_100k'] = city_data['count'] / 100000
    pivot_data = city_data.pivot(index='city_name', columns='car_type_name', values='count_100k').fillna(0)
    pivot_data = pivot_data.map(lambda x: int(x))
    
    return pivot_data

def create_gender_chart(gender_city_data):
    """성별 차량 등록대수 차트 생성"""
    if gender_city_data.empty:
        return None
    
    gender_city_data['count_100k'] = gender_city_data['count'] / 100000
    gender_pivot = gender_city_data.pivot(index='city_name', columns='gender_name', values='count_100k').fillna(0)
    gender_pivot = gender_pivot.map(lambda x: int(x))
    
    gender_data_long = gender_pivot.reset_index().melt(id_vars='city_name', var_name='성별', value_name='차량대수')
    
    color_scale = alt.Scale(domain=['여자', '남자'], range=['#FF69B4', '#4169E1'])
    
    chart = alt.Chart(gender_data_long).mark_bar().encode(
        x=alt.X('city_name:N', title='시'),
        y=alt.Y('차량대수:Q', title='차량대수'),
        color=alt.Color('성별:N', scale=color_scale, title='성별'),
        tooltip=['city_name', '성별', '차량대수']
    ).properties(
        width=600,
        height=400
    )
    
    return chart

# ============================================================================
# 지도 관련 함수들
# ============================================================================

def get_city_coordinates():
    """시별 좌표 정보 반환"""
    return {
        "서울": [37.5665, 126.9780], "부산": [35.1796, 129.0756], "대구": [35.8714, 128.6014],
        "인천": [37.4563, 126.7052], "광주": [35.1595, 126.8526], "대전": [36.3504, 127.3845],
        "울산": [35.5384, 129.3114], "세종": [36.4800, 127.2890], "경기": [37.4138, 127.5183],
        "충북": [36.8, 127.7], "충남": [36.6, 126.8], "전남": [34.8, 126.9], "경북": [36.5, 128.2],
        "경남": [35.5, 128.2], "제주": [33.4996, 126.5312], "강원": [37.8228, 128.1555], "전북": [35.7175, 127.1530],
        "창원시": [35.2278, 128.6817], "포항시": [36.0320, 129.3650], "전주시": [35.8242, 127.1480],
        "천안시": [36.8150, 127.1139], "청주시": [36.6424, 127.4890], "고양시": [37.6584, 126.8320],
        "용인시": [37.2411, 127.1776], "부천시": [37.5035, 126.7660], "안산시": [37.3219, 126.8309],
        "안양시": [37.3943, 126.9569], "성남시": [37.4449, 127.1389], "수원시": [37.2636, 127.0286]
    }

def get_city_boundaries():
    """시별 경계 좌표 반환"""
    return {
        "서울": {"min_lat": 37.4, "max_lat": 37.7, "min_lon": 126.7, "max_lon": 127.2},
        "부산": {"min_lat": 35.0, "max_lat": 35.4, "min_lon": 128.9, "max_lon": 129.3},
        "대구": {"min_lat": 35.7, "max_lat": 36.0, "min_lon": 128.4, "max_lon": 128.8},
        "인천": {"min_lat": 37.3, "max_lat": 37.6, "min_lon": 126.4, "max_lon": 126.8},
        "광주": {"min_lat": 35.0, "max_lat": 35.3, "min_lon": 126.7, "max_lon": 127.0},
        "대전": {"min_lat": 36.2, "max_lat": 36.5, "min_lon": 127.2, "max_lon": 127.5},
        "울산": {"min_lat": 35.4, "max_lat": 35.7, "min_lon": 129.2, "max_lon": 129.5},
        "세종": {"min_lat": 36.4, "max_lat": 36.7, "min_lon": 127.1, "max_lon": 127.4},
        "경기": {"min_lat": 37.0, "max_lat": 38.0, "min_lon": 126.5, "max_lon": 127.8},
        "충북": {"min_lat": 36.5, "max_lat": 37.2, "min_lon": 127.0, "max_lon": 128.5},
        "충남": {"min_lat": 36.0, "max_lat": 37.0, "min_lon": 126.0, "max_lon": 127.5},
        "전남": {"min_lat": 34.5, "max_lat": 35.5, "min_lon": 126.0, "max_lon": 127.5},
        "경북": {"min_lat": 35.5, "max_lat": 37.5, "min_lon": 127.5, "max_lon": 129.5},
        "경남": {"min_lat": 34.5, "max_lat": 36.0, "min_lon": 127.5, "max_lon": 129.5},
        "제주": {"min_lat": 33.0, "max_lat": 33.6, "min_lon": 126.0, "max_lon": 127.0},
        "강원": {"min_lat": 37.0, "max_lat": 38.5, "min_lon": 127.5, "max_lon": 129.0},
        "전북": {"min_lat": 35.0, "max_lat": 36.5, "min_lon": 126.5, "max_lon": 128.0},
        "창원시": {"min_lat": 35.1, "max_lat": 35.4, "min_lon": 128.5, "max_lon": 128.8},
        "포항시": {"min_lat": 35.8, "max_lat": 36.3, "min_lon": 129.2, "max_lon": 129.5},
        "전주시": {"min_lat": 35.7, "max_lat": 36.0, "min_lon": 127.0, "max_lon": 127.3},
        "천안시": {"min_lat": 36.7, "max_lat": 37.0, "min_lon": 127.0, "max_lon": 127.4},
        "청주시": {"min_lat": 36.5, "max_lat": 36.8, "min_lon": 127.4, "max_lon": 127.6},
        "고양시": {"min_lat": 37.6, "max_lat": 37.8, "min_lon": 126.7, "max_lon": 126.9},
        "용인시": {"min_lat": 37.1, "max_lat": 37.4, "min_lon": 127.0, "max_lon": 127.3},
        "부천시": {"min_lat": 37.4, "max_lat": 37.6, "min_lon": 126.7, "max_lon": 126.9},
        "안산시": {"min_lat": 37.2, "max_lat": 37.4, "min_lon": 126.7, "max_lon": 126.9},
        "안양시": {"min_lat": 37.3, "max_lat": 37.5, "min_lon": 126.8, "max_lon": 127.0},
        "성남시": {"min_lat": 37.4, "max_lat": 37.5, "min_lon": 127.1, "max_lon": 127.2},
        "수원시": {"min_lat": 37.2, "max_lat": 37.4, "min_lon": 126.9, "max_lon": 127.1}
    }

def create_national_map(city_total_dict):
    """전국 지도 생성"""
    city_coords = get_city_coordinates()
    m_korea = folium.Map(location=[36.5, 127.5], zoom_start=7)
    
    for city_name, coords in city_coords.items():
        if city_name in city_total_dict:
            total_count = city_total_dict[city_name]
            
            popup_html = f"""
            <div style="width: 200px;">
                <h4>{city_name}</h4>
                <p><b>총 차량대수:</b> {int(total_count):,}대</p>
                <p><small>오른쪽에서 시를 선택하세요.</small></p>
            </div>
            """
            
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{city_name}: {int(total_count):,}대",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m_korea)
    
    return m_korea

def get_district_name(feat_name):
    """GeoJSON 이름에서 군구명 추출"""
    district_mapping = {
        "부천시오정구": "부천시", "부천시소사구": "부천시", "부천시원미구": "부천시",
        "성남시분당구": "성남시", "성남시수정구": "성남시", "성남시중원구": "성남시",
        "수원시권선구": "수원시", "수원시영통구": "수원시", "수원시장안구": "수원시", "수원시팔달구": "수원시",
        "창원시마산합포구": "창원시", "창원시마산회원구": "창원시", "창원시성산구": "창원시", "창원시의창구": "창원시", "창원시진해구": "창원시",
        "포항시남구": "포항시", "포항시북구": "포항시",
        "전주시덕진구": "전주시", "전주시완산구": "전주시",
        "천안시동남구": "천안시", "천안시서북구": "천안시",
        "청주시상당구": "청주시", "청주시서원구": "청주시", "청주시청원구": "청주시", "청주시흥덕구": "청주시",
        "용인시기흥구": "용인시", "용인시수지구": "용인시", "용인시처인구": "용인시",
        "고양시덕양구": "고양시", "고양시일산동구": "고양시", "고양시일산서구": "고양시",
        "안산시단원구": "안산시", "안산시상록구": "안산시",
        "안양시동안구": "안양시", "안양시만안구": "안양시"
    }
    
    if feat_name in district_mapping:
        return district_mapping[feat_name]
    elif feat_name == "세종특별자치시":
        return "세종특별자치시"
    else:
        return feat_name

def create_city_district_key(selected_city, district_name):
    """시+군구 키 생성 함수"""
    if selected_city == "경기":
        return f"경기 {district_name}"
    elif selected_city == "세종":
        return "세종 세종특별자치시"
    else:
        return f"{selected_city} {district_name}"

def check_city_boundary(feature, selected_city, city_boundaries):
    """시 경계 내에 있는지 확인"""
    if selected_city not in city_boundaries:
        return False
    
    bounds = city_boundaries[selected_city]
    
    if feature['geometry']['type'] == 'Polygon':
        coords = feature['geometry']['coordinates'][0]
        lats = [coord[1] for coord in coords]
        lons = [coord[0] for coord in coords]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
    elif feature['geometry']['type'] == 'MultiPolygon':
        coords = feature['geometry']['coordinates'][0][0]
        lats = [coord[1] for coord in coords]
        lons = [coord[0] for coord in coords]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
    else:
        return False
    
    return (bounds['min_lat'] <= center_lat <= bounds['max_lat'] and 
            bounds['min_lon'] <= center_lon <= bounds['max_lon'])

def calculate_center_coordinates(feature):
    """폴리곤의 중심좌표 계산"""
    if feature['geometry']['type'] == 'Polygon':
        coords = feature['geometry']['coordinates'][0]
        lats = [coord[1] for coord in coords]
        lons = [coord[0] for coord in coords]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        return center_lat, center_lon
    elif feature['geometry']['type'] == 'MultiPolygon':
        coords = feature['geometry']['coordinates'][0][0]
        lats = [coord[1] for coord in coords]
        lons = [coord[0] for coord in coords]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        return center_lat, center_lon
    else:
        return None

def create_city_detail_map(selected_city, district_data, car_type_district_data, selected_year):
    """시별 상세 지도 생성"""
    city_coords = get_city_coordinates()
    city_boundaries = get_city_boundaries()
    
    if district_data.empty:
        return None
    
    # GeoJSON 로드
    with open("sigungu.geo.json", encoding="utf-8") as f:
        geojson = json.load(f)
    
    # 시+군구 키를 사용한 딕셔너리 생성
    district_count_dict = dict(zip(district_data['city_district_key'], district_data['total_count']))
    
    # GeoJSON에서 선택된 시에 해당하는 군구만 필터링
    features = []
    
    for feat in geojson['features']:
        feat_name = feat['properties'].get('name')
        if feat_name:
            district_name = get_district_name(feat_name)
            city_district_key = create_city_district_key(selected_city, district_name)
            is_in_city_boundary = check_city_boundary(feat, selected_city, city_boundaries)
            
            if city_district_key in district_count_dict and is_in_city_boundary:
                features.append(feat)
    
    city_geojson = {"type": "FeatureCollection", "features": features}
    
    # 차량별 데이터를 시+군구 키로 그룹화
    car_type_by_district = {}
    for _, row in car_type_district_data.iterrows():
        key = row['city_district_key']
        if key not in car_type_by_district:
            car_type_by_district[key] = []
        car_type_by_district[key].append({
            'car_type': row['car_type_name'],
            'count': row['count']
        })
    
    center = city_coords[selected_city] if selected_city in city_coords else [36.5, 127.5]
    m = folium.Map(location=center, zoom_start=10)
    
    max_count = max(district_count_dict.values())
    min_count = min(district_count_dict.values())
    
    def get_color(count):
        """차량대수에 따른 색상 반환 함수"""
        ratio = (count - min_count) / (max_count - min_count + 1e-6)
        return f"#{int(255*ratio):02x}00{int(255*(1-ratio)):02x}"
    
    def style_function(feature):
        """GeoJSON 스타일링 함수"""
        dname = feature['properties'].get('name')
        district_name = get_district_name(dname)
        city_district_key = create_city_district_key(selected_city, district_name)
        count = district_count_dict.get(city_district_key, 0)
        
        return {
            "fillColor": get_color(count),
            "color": "black",
            "weight": 2,
            "fillOpacity": 0.6,
        }
    
    def highlight_function(feature):
        """마우스 오버 시 하이라이트 함수"""
        return {"weight": 4, "color": "yellow"}
    
    folium.GeoJson(
        city_geojson,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["name"],
            aliases=["군구명:"],
            localize=True
        ),
        popup=folium.GeoJsonPopup(
            fields=["name"],
            aliases=["군구명:"],
            localize=True,
            labels=True,
            style="background-color: white;"
        )
    ).add_to(m)
    
    # 클릭 시 차량별 상세 정보 팝업
    for feature in city_geojson['features']:
        dname = feature['properties'].get('name')
        district_name = get_district_name(dname)
        city_district_key = create_city_district_key(selected_city, district_name)
        
        total_count = district_count_dict.get(city_district_key, 0)
        
        # 차량별 상세 정보 HTML 생성
        car_details_html = ""
        if city_district_key in car_type_by_district:
            car_details_html = "<br><b>차량별 현황:</b><br>"
            for car_info in car_type_by_district[city_district_key]:
                car_details_html += f"• {car_info['car_type']}: {int(car_info['count']):,}대<br>"
        
        # 중심좌표 계산
        center_coords = calculate_center_coordinates(feature)
        if center_coords:
            center_lat, center_lon = center_coords
            
            # 화면에 표시할 이름 생성
            display_name = "세종특별자치시" if selected_city == "세종" else city_district_key
            
            popup_html = f"""
            <div style="width: 300px;">
                <h4>{display_name}</h4>
                <p><b>총 차량대수:</b> {int(total_count):,}대</p>
                {car_details_html}
            </div>
            """
            
            folium.Marker(
                location=[center_lat, center_lon],
                popup=folium.Popup(popup_html, max_width=350),
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
    
    return m

# ============================================================================
# 애플리케이션 초기화 및 설정
# ============================================================================

def initialize_app():
    """애플리케이션 초기 설정"""
    # st.set_page_config은 메인 앱에서만 호출해야 함
    
    # CSS 스타일링
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            display: flex;
            justify-content: center;
        }
        
        .css-18e3th9 {
            max-width: 1400px;
            width: 100%;
            padding-left: 0;
            padding-right: 0;
        }
        
        .block-container {
            max-width: 1400px;
            width: 100%;
            padding-left: 0;
            padding-right: 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 세션 상태 초기화
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'main'



# ============================================================================
# 페이지 렌더링 함수들
# ============================================================================

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
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.altair_chart(new_car_chart, use_container_width=True)
            st.caption("신차등록: 십만 대")
            
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 성별 차량 등록대수
        st.markdown("##### 👥 광역자치단체의 성별별 차량 등록대수")
        gender_city_data = get_gender_city_data(conn, selected_year)
        gender_chart = create_gender_chart(gender_city_data)
        
        if gender_chart is not None:
            st.altair_chart(gender_chart, use_container_width=True)
            st.caption("단위: 십만 대")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3. 지도 시각화
        st.markdown(f"#### 🗺️ {selected_year}년 광역자치단체와 기초자치단체의 지도")
        
        city_total_data = get_city_total_data(conn, selected_year)
        city_total_dict = dict(zip(city_total_data['city_name'], city_total_data['total_count']))
        
        # 세션 상태로 선택된 시 관리 - 키를 더 구체적으로 설정
        session_key = f'selected_city_for_map_{selected_year}'
        if session_key not in st.session_state:
            st.session_state[session_key] = None
        
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
                index=0,
                key=f"city_dropdown_{selected_year}"
            )
            
            if selected_city_dropdown != "광역자치단체를 선택하세요":
                st.session_state[session_key] = selected_city_dropdown
                st.success(f"✅ {selected_city_dropdown} 선택됨")
            
            if st.session_state[session_key]:
                selected_city = st.session_state[session_key]
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
        st.error("데이터베이스 연결을 확인해주세요.")
