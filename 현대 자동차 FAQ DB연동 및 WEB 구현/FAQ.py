import streamlit as st
import pymysql

# MySQL 연결
def get_db_connection():
    connection = pymysql.connect(
        host='localhost', 
        user='Hyundai', 
        password='hyundai', 
        database='hyundai_faq_db',
        charset='utf8mb4'
    )
    return connection

# 카테고리 목록 가져오기
def get_categories():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT name FROM faq_category")
        categories = cursor.fetchall()
    conn.close()
    return categories

# FAQ 목록 가져오기 (카테고리 이름도 함께 조회)
def get_faqs(category_name, search_text, exact_match, offset, limit=10):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        field = "answer" if exact_match else "question"

        if category_name == "전체":
            query = f"""
                SELECT f.question, f.answer, fc.name 
                FROM faq f
                JOIN faq_category fc ON f.category_id = fc.name
                WHERE f.{field} LIKE %s
                LIMIT {limit} OFFSET {offset}
            """
            cursor.execute(query, (f'%{search_text}%',))
        else:
            query = f"""
                SELECT f.question, f.answer, fc.name 
                FROM faq f
                JOIN faq_category fc ON f.category_id = fc.name
                WHERE fc.name = %s AND f.{field} LIKE %s
                LIMIT {limit} OFFSET {offset}
            """
            cursor.execute(query, (category_name, f'%{search_text}%',))

        faqs = cursor.fetchall()
    conn.close()
    return faqs

# FAQ 항목 출력 (카테고리 이름 포함)
def display_faqs(faqs):
    if not faqs:
        st.write("검색된 내용이 없습니다.")
    else:
        for faq in faqs:
            question, answer, category_name = faq
            question_with_category = f"[{category_name}]{question}"
            with st.expander(question_with_category):
                st.write(answer)

# 페이지네이션 계산
def get_page_numbers(total_faqs, limit=10):
    total_pages = (total_faqs // limit) + (1 if total_faqs % limit != 0 else 0)
    return total_pages

# 검색어 변경 콜백
def on_search_change():
    st.session_state.page_number = 1
    st.session_state.search_triggered = True

# Streamlit 앱 실행
def main():
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1
    if "search_triggered" not in st.session_state:
        st.session_state.search_triggered = True

    st.title("현대자동차 FAQ")

    # 카테고리 불러오기
    categories = get_categories()
    category_names = ["전체"] + [cat[0] for cat in categories]

    # 검색 입력
    search_text = st.text_input("검색어를 입력하세요", key="search_input", on_change=on_search_change)

    # 옵션과 카테고리 선택
    col_opt, col_cat = st.columns([1, 1])
    with col_opt:
        exact_match = st.radio("검색옵션", ("질의 제목", "내용")) == "내용"
    with col_cat:
        selected_category_name = st.selectbox("카테고리", category_names)

    # 카테고리 변경 시 자동 리셋
    if "last_selected_category" in st.session_state:
        if st.session_state.last_selected_category != selected_category_name:
            st.session_state.page_number = 1
            st.session_state.search_triggered = True
    st.session_state.last_selected_category = selected_category_name

    # 검색 버튼
    if st.button("검색"):
        st.session_state.page_number = 1
        st.session_state.search_triggered = True

    # FAQ 검색 및 출력
    if st.session_state.search_triggered:
        total_faqs = len(get_faqs(selected_category_name, search_text, exact_match, offset=0, limit=1000))
        total_pages = get_page_numbers(total_faqs)
        page_number = st.session_state.page_number
        offset = (page_number - 1) * 10

        # 페이지 이동 버튼
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        with col1:
            if st.button("맨처음"):
                st.session_state.page_number = 1
        with col2:
            if st.button("이전 페이지") and page_number > 1:
                st.session_state.page_number -= 1
        with col4:
            if st.button("다음 페이지") and page_number < total_pages:
                st.session_state.page_number += 1
        with col5:
            if st.button("페이지 끝"):
                st.session_state.page_number = total_pages

        page_number = st.session_state.page_number
        offset = (page_number - 1) * 10

        faqs = get_faqs(selected_category_name, search_text, exact_match, offset)
        display_faqs(faqs)

        with col3:
            st.write(f"페이지 {page_number} / {total_pages}")

if __name__ == "__main__":
    main()
