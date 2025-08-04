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

# 카테고리 목록 가져오기 (name만 선택)
def get_categories():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT name FROM faq_category")  # id 대신 name만 선택
        categories = cursor.fetchall()
    conn.close()
    return categories

# FAQ 목록 가져오기
def get_faqs(category_name, search_text, exact_match, offset, limit=10):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # exact_match == False → "질의 제목", exact_match == True → "내용"
        field = "answer" if exact_match else "question"
        
        if category_name == "전체":
            query = f"SELECT question, answer FROM faq WHERE {field} LIKE %s LIMIT {limit} OFFSET {offset}"
            cursor.execute(query, (f'%{search_text}%',))
        else:
            query = f"""
                SELECT f.question, f.answer 
                FROM faq f
                JOIN faq_category fc ON f.category_id = fc.name
                WHERE fc.name = %s AND f.{field} LIKE %s
                LIMIT {limit} OFFSET {offset}
            """
            cursor.execute(query, (category_name, f'%{search_text}%',))
        
        faqs = cursor.fetchall()
    conn.close()
    return faqs


# FAQ 항목 처리
def display_faqs(faqs):
    if not faqs:  # 검색 결과가 없을 경우 메시지 표시
        st.write("검색된 내용이 없습니다.")
    else:
        for faq in faqs:
            question, answer = faq
            with st.expander(question):
                st.write(answer)

# 페이지네이션
def get_page_numbers(total_faqs, limit=10):
    total_pages = (total_faqs // limit) + (1 if total_faqs % limit != 0 else 0)
    return total_pages

# Streamlit 앱 구성
def main():
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1
    if "search_triggered" not in st.session_state:
        st.session_state.search_triggered = True  # 최초 진입 시 자동 표시

    st.title("현대자동차 FAQ")

    # 카테고리 선택
    categories = get_categories()
    category_names = ["전체"] + [cat[0] for cat in categories]
    selected_category_name = st.sidebar.selectbox("카테고리", category_names)

    # 카테고리 변경 시 자동 표시
    if "last_selected_category" in st.session_state:
        if st.session_state.last_selected_category != selected_category_name:
            st.session_state.page_number = 1
            st.session_state.search_triggered = True  # 자동 FAQ 표시
    st.session_state.last_selected_category = selected_category_name

    # 검색 입력
    search_text = st.text_input("검색어를 입력하세요", key="search_input")

    # 검색옵션
    exact_match = st.radio("검색옵션", ("질의 제목", "내용")) == "내용"

    # 검색 버튼
    if st.button("검색"):
        st.session_state.page_number = 1
        st.session_state.search_triggered = True

    # 검색 혹은 자동 진입 조건 만족 시 FAQ 표시
    if st.session_state.search_triggered:
        total_faqs = len(get_faqs(selected_category_name, search_text, exact_match, offset=0, limit=1000))
        total_pages = get_page_numbers(total_faqs)
        page_number = st.session_state.page_number
        offset = (page_number - 1) * 10

        # 페이징 버튼
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
