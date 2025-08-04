"""
지도 관련 모듈
"""

import folium
import json

# 시별 좌표 정보 반환 함수: 시도명을 키로 하고 [위도, 경도] 리스트를 값으로 하는 딕셔너리
def get_city_coordinates():
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

# 시별 경계 좌표 반환: 시도명을 키로 하고 경계 좌표(최소/최대 위도, 경도)를 값
def get_city_boundaries():
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

# 전국 지도 생성: 시도명을 키로 하고 총 차량대수를 값으로 하는 딕셔너리
def create_national_map(city_total_dict):
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

#시별 상세 지도 생성
def create_city_detail_map(selected_city, district_data, car_type_district_data, selected_year):
    city_coords = get_city_coordinates()
    city_boundaries = get_city_boundaries()
    
    if district_data.empty:
        return None
    
    # GeoJSON 로드
    with open("sigungu.geo.json", encoding="utf-8") as f:
        geojson = json.load(f)
    
    # 시+군구 키를 사용한 딕셔너리 생성 (중복된 군구 제거를 위함)
    district_count_dict = dict(zip(district_data['city_district_key'], district_data['total_count']))
    
    # GeoJSON에서 선택된 시에 해당하는 군구만 필터링
    features = []
    
    for feat in geojson['features']:
        feat_name = feat['properties'].get('name')
        if feat_name:
            district_name = get_district_name(feat_name)
            
            # 시+군구 키 생성
            city_district_key = create_city_district_key(selected_city, district_name)
            
            # 좌표 기반 필터링
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

# GeoJSON 이름에서 군구명 추출
def get_district_name(feat_name):
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

# 시+군구 키 생성 함수
def create_city_district_key(selected_city, district_name):
    if selected_city == "경기":
        return f"경기 {district_name}"
    elif selected_city == "세종":
        return "세종 세종특별자치시"
    else:
        return f"{selected_city} {district_name}"

# 시 경계 내에 있는지 확인
def check_city_boundary(feature, selected_city, city_boundaries):
    if selected_city not in city_boundaries:
        return False
    
    bounds = city_boundaries[selected_city]
    
    # 폴리곤의 중심점 계산
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
    
    # 경계 내에 있는지 확인
    return (bounds['min_lat'] <= center_lat <= bounds['max_lat'] and 
            bounds['min_lon'] <= center_lon <= bounds['max_lon'])

# 폴리곤의 중심좌표 계산
def calculate_center_coordinates(feature):
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