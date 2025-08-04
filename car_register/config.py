"""
설정 및 초기화 관련 모듈
- 애플리케이션 초기화
- 페이지 설정
- 사이드바 네비게이션 생성
- 페이지 전환 기능
"""

import streamlit as st

def initialize_app():
    """
    애플리케이션 초기 설정 함수
    - 페이지 제목, 아이콘, 레이아웃 설정
    - 세션 상태 초기화 (현재 페이지 정보)
    """
    # Streamlit 페이지 기본 설정
    st.set_page_config(
        page_title="자동차 등록 현황",  # 브라우저 탭에 표시될 제목
        page_icon="🚗",                # 브라우저 탭에 표시될 아이콘
        layout="wide",
        initial_sidebar_state="auto"                # 전체 화면 레이아웃 사용
    )
    
    # CSS를 사용하여 페이지 너비를 1000px로 설정하고 양 옆 여백 추가
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
    
    # 세션 상태 초기화 - 현재 페이지 정보 저장
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'main'  # 기본 페이지를 메인으로 설정

def create_navigation():
    """
    사이드바 네비게이션 생성 함수
    - 메인 페이지, 전국 현황, 현대 현황 버튼 생성
    - 각 버튼 클릭 시 해당 페이지로 이동
    """
    # 사이드바에 메뉴 제목 표시
    st.sidebar.markdown("### 📋 메뉴")
    
    # 메인 페이지 버튼
    if st.sidebar.button("🏠 메인", use_container_width=True):
        change_page('main')  # 메인 페이지로 이동
    
    # 전국 현황 페이지 버튼
    if st.sidebar.button("📊 전국 현황", use_container_width=True):
        change_page('national')  # 전국 현황 페이지로 이동
    
    # 현대 현황 페이지 버튼
    if st.sidebar.button("🏢 현대 현황", use_container_width=True):
        change_page('hyundai')  # 현대 현황 페이지로 이동

def change_page(page):
    """
    페이지 변경 함수: 이동할 페이지 이름 ('main', 'national', 'hyundai')
    """
    # 세션 상태에 현재 페이지 정보 저장
    # 이 정보는 app.py의 main() 함수에서 사용되어 해당 페이지를 렌더링
    st.session_state.current_page = page 