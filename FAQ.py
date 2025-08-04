import streamlit as st
import pymysql

# DB 연결 함수
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root1234',
        database='car',
        charset='utf8mb4'
    )

# 카테고리 목록
def get_categories():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT name FROM faq_category")
        result = cursor.fetchall()
    conn.close()
    return result

# FAQ 가져오기
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
        return cursor.fetchall()
    conn.close()

# 페이지 수 계산
def get_page_numbers(total_faqs, limit=10):
    return (total_faqs // limit) + (1 if total_faqs % limit != 0 else 0)

# FAQ 출력
def display_faqs(faqs):
    if not faqs:
        st.write("검색된 내용이 없습니다.")
    else:
        for question, answer, category in faqs:
            with st.expander(f"[{category}] {question}"):
                st.write(answer)

# 앱 메인
def main():
    st.title("현대자동차 FAQ")
    st.subheader("자주하는 질문을 확인해보세요.")

    # 카테고리 목록 + 탭 생성
    categories = get_categories()
    category_names = ["전체"] + [c[0] for c in categories]
    tabs = st.tabs(category_names)

    for category_name, tab in zip(category_names, tabs):
        with tab:
            # 고유 키 생성
            page_key = f"page_number_{category_name}"
            input_key = f"search_input_{category_name}"
            match_key = f"match_option_{category_name}"
            button_key = f"search_btn_{category_name}"
            trigger_key = f"search_triggered_{category_name}"

            # 상태 초기화
            if page_key not in st.session_state:
                st.session_state[page_key] = 1
            if trigger_key not in st.session_state:
                st.session_state[trigger_key] = True

            # 검색 UI
            def on_search_change():
                st.session_state[page_key] = 1
                st.session_state[trigger_key] = True

            search_text = st.text_input("궁금한 점을 검색해 보세요", key=input_key, on_change=on_search_change)
            exact_match = st.radio("검색옵션", ("질의 제목", "내용"), key=match_key) == "내용"

            if st.button("검색", key=button_key):
                st.session_state[page_key] = 1
                st.session_state[trigger_key] = True

            if st.session_state[trigger_key]:
                # 총 개수 조회
                total_faqs = len(get_faqs(category_name, search_text, exact_match, 0, 1000))
                total_pages = get_page_numbers(total_faqs)
                current_page = st.session_state[page_key]
                offset = (current_page - 1) * 10

                # 페이지네이션
                col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
                with col1:
                    if st.button("맨처음", key=f"first_{category_name}"):
                        st.session_state[page_key] = 1
                with col2:
                    if st.button("이전 페이지", key=f"prev_{category_name}") and current_page > 1:
                        st.session_state[page_key] -= 1
                with col4:
                    if st.button("다음 페이지", key=f"next_{category_name}") and current_page < total_pages:
                        st.session_state[page_key] += 1
                with col5:
                    if st.button("페이지 끝", key=f"last_{category_name}"):
                        st.session_state[page_key] = total_pages

                current_page = st.session_state[page_key]
                offset = (current_page - 1) * 10
                # FAQ 출력
                faqs = get_faqs(category_name, search_text, exact_match, offset)
                display_faqs(faqs)
                with col3:
                    st.markdown(f"**페이지 {current_page} / {total_pages}**")

if __name__ == "__main__":
    main()
