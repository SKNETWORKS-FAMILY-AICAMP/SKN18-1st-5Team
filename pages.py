"""
페이지 렌더링 관련 모듈
"""

import streamlit as st

def render_main_page():
    """메인 페이지 렌더링"""
    st.title("🚗 자동차 등록 현황 대시보드")
    
    st.markdown("### 📋 메인 메뉴")
    
    

    st.markdown("#### 📈 전국 자동차 등록 현황")
    st.markdown("전국의 자동차 등록 현황을 확인할 수 있습니다.")
    if st.button("📊 전국 현황", key="pages_main_national", use_container_width=True):
        st.session_state.current_page = 'national'
        st.rerun()
    
    st.markdown("#### 🏢 현대자동차")
    st.markdown("현대 자동차 판매실적에 대한 분석을 확인할 수 있습니다.")
    if st.button("🚗 현대자동차", key="pages_main_hyundai", use_container_width=True):
        st.session_state.current_page = 'hyundai'
        st.rerun()

    st.markdown("#### ❓ 현대자동차 FAQ")
    st.markdown("현대자동차에 대한 자주 묻는 질문을 확인할 수 있습니다.")
    if st.button("❓ FAQ", key="pages_main_faq", use_container_width=True):
        st.session_state.current_page = 'hyundai_faq'
        st.rerun()
    
   