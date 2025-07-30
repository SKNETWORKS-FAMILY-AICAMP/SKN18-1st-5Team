import requests
import pandas as pd
import json
import re
import html
import csv

def clean_html_text(html_text):
    # HTML entity 디코딩
    text = html.unescape(html_text)

    # <br> 태그를 띄어쓰기로 변환
    text = re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)

    # </p> 또는 <p> 를 띄어쓰기으로 변환
    text = re.sub(r'</?p[^>]*>', ' ', text, flags=re.IGNORECASE)

    # <span ...> ... </span> 제거
    text = re.sub(r'<span[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</span>', '', text, flags=re.IGNORECASE)

    # <a href=...>text</a> → text 로 변환
    text = re.sub(r'<a[^>]*href="mailto:[^"]*">([^<]*)</a>', r'\1', text, flags=re.IGNORECASE)

    # 기타 HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)

    # 다중 공백/줄바꿈 정리
    text = re.sub(r'\n+', ' ', text)               # 줄바꿈 여러 개 → 하나
    text = re.sub(r'[ \t]+', ' ', text)             # 탭/스페이스 → 하나
    text = re.sub(r' *\n *', ' ', text)            # 줄바꿈 앞뒤 공백 제거
    text = text.strip()

    text = re.sub(r'\r\n|\n\r|\r', ' ', text)

    # 중복된 공백/줄바꿈 줄이기
    text = re.sub(r'\n{2,}', ' ', text)  # 줄바꿈 2번 이상 → 1번
    text = re.sub(r'[ \t]+', ' ', text)   # 연속 공백/탭 → 하나로

    # &nbsp;는 이미 html.unescape로 공백 처리되었지만, 혹시 남아있으면 제거
    text = re.sub(r'\xa0', ' ', text)

    # &#39; → ' 같은 문자도 처리됨
    text = re.sub(r" +\n", ' ', text)  # 줄 끝 공백 제거
    text = re.sub(r"\n +", ' ', text)  # 줄 시작 공백 제거

    # 불필요한 공백 줄이기 (예: ' ▶바로가기' 전후)
    text = re.sub(r' *▶ *', ' ▶ ', text)

    # 기타 불필요한 content
    text = re.sub(r'([&][a-z0~9]+;)', ' ', text)
    text = re.sub(r'([&][#][0-9]+;)', ' ', text)
    
    return text

def HyundaiFAQ_Crawling(p_pagenum):
    url = "https://www.hyundai.com/wsvc/front/biz/frontFaq.faqListArr.do?searchKeyword=&pageNo={}&frontSupiCtgr=&frontCtgrScd=".format(p_pagenum)
    response = requests.get(url)
    page = json.loads(response.text)

    return page

def Extract_title_content(p_page):
    title = [clean_html_text(i["frontFaqTitlSbc"]) for i in p_page["data"]]
    content = [clean_html_text(i["frontFaqSbc"]) for i in p_page["data"]]

    return title, content

def Write_CSV(p_pagenum, p_title, p_content):
    data = [["기업명", "제목", "내용"] if p_pagenum == 1 else []]
    for i, j in zip(p_title, p_content):
        data.append(["현대자동차" , i, j])

    with open('현대자동차.csv', 'w' if p_pagenum == 1 else 'a', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

def Final_data():
    df = pd.read_csv("현대자동차.csv")
    return df

def main():
    pagenum = 1
    while True:
        page = HyundaiFAQ_Crawling(pagenum)
        title, content = Extract_title_content(page)
        if not title:
            df = Final_data()
            break
        Write_CSV(pagenum, title, content)
        pagenum += 1

    print(df)
    return df

main()