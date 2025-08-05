import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="자동차 등록 현황 대시보드",
    layout="wide",
    initial_sidebar_state="collapsed"  # 사이드바 기본 숨김
)

# 모듈 import
from pages import render_main_page
from app01 import render_national_page
from hyundai import render_hyundai_page
from FAQ import  faq_main

def main():
    """메인 애플리케이션"""
    
    # 세션 상태 초기화
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'main'
    
    # 사이드바 스타일 설정
    st.markdown("""
    <style>
    /* 사이드바 버튼 스타일 */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
        margin-bottom: 8px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* 현재 페이지 버튼 강조 */
    .current-page-button {
        background-color: #1f77b4 !important;
        color: white !important;
        border-color: #1f77b4 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 페이지 매핑
    page_mapping = {
        "메인": "main",
        "전국 현황": "national", 
        "현대 현황": "hyundai",
        "FAQ": "hyundai_faq"
    }
    
    # 역방향 매핑 (페이지 상태 -> 한글 이름)
    reverse_mapping = {v: k for k, v in page_mapping.items()}
    
    # 현재 페이지에 해당하는 한글 이름 찾기
    current_page_korean = reverse_mapping.get(st.session_state.current_page, "메인")
    
    # 사이드바 네비게이션
    st.sidebar.title("바로가기")
    # 사이드바에 네비게이션 버튼들 배치
    # 현재 페이지에 따라 버튼 스타일 변경
    current_page = st.session_state.current_page
    
    # 메인 페이지 버튼
    if current_page == 'main':
        st.sidebar.markdown("**🏠 메인** (현재 페이지)")
    else:
        if st.sidebar.button("🏠 메인", key="sidebar_main", use_container_width=True):
            st.session_state.current_page = 'main'
            st.rerun()
    
    # 전국 현황 버튼
    if current_page == 'national':
        st.sidebar.markdown("**📊 전국 현황** (현재 페이지)")
    else:
        if st.sidebar.button("📊 전국 현황", key="sidebar_national", use_container_width=True):
            st.session_state.current_page = 'national'
            st.rerun()
    
    # 현대 현황 버튼
    if current_page == 'hyundai':
        st.sidebar.markdown("**🚗 현대 현황** (현재 페이지)")
    else:
        if st.sidebar.button("🚗 현대 현황", key="sidebar_hyundai", use_container_width=True):
            st.session_state.current_page = 'hyundai'
            st.rerun()
    
    # FAQ 버튼
    if current_page == 'hyundai_faq':
        st.sidebar.markdown("**❓ FAQ** (현재 페이지)")
    else:
        if st.sidebar.button("❓ FAQ", key="sidebar_faq", use_container_width=True):
            st.session_state.current_page = 'hyundai_faq'
            st.rerun()

    
    # 페이지별 내용 표시
    if st.session_state.current_page == 'main':
        render_main_page()
    elif st.session_state.current_page == 'national':
        render_national_page()
    elif st.session_state.current_page == 'hyundai':
        render_hyundai_page()
    elif st.session_state.current_page == 'hyundai_faq':
        # FAQ.py 모듈 실행
        faq_main()

if __name__ == "__main__":
    main()