import streamlit as st

# 모듈 import
from config import initialize_app, create_navigation
from pages import render_main_page, render_national_page, render_hyundai_page
import FAQ

def main():
    """메인 애플리케이션"""
    # 초기화
    initialize_app()
    
    # 사이드 바 네비게이션
    create_navigation()
    
    # 페이지별 내용 표시
    if st.session_state.current_page == 'main':
        render_main_page()
    elif st.session_state.current_page == 'national':
        render_national_page()
    elif st.session_state.current_page == 'hyundai':
        render_hyundai_page()
    elif st.session_state.current_page == 'hyundai_faq':
        # FAQ.py 모듈 실행
        FAQ.main()

if __name__ == "__main__":
    main()