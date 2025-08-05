import csv
import requests
import json
import os
import 현대자동차FAQ

def KiaFAQCrawling(p_category):
    url = "https://www.kia.com/kr/services/ko/faq.search?searchTag=kwp:kr/faq/{}".format(p_category)
    response = requests.get(url)
    page = json.loads(response.text)

    return page

def Extract_title_content(p_page):
    title = [현대자동차FAQ.clean_html_text(i["question"]) for i in p_page["data"]["faqList"]["items"]]
    content = [현대자동차FAQ.clean_html_text(i["answer"]["html"]) for i in p_page["data"]["faqList"]["items"]]

    return title, content

def Write_CSV(p_pagenum, p_title, p_content, p_company, p_category):
    data = [["기업명", "카테고리" ,"제목", "내용"] if p_pagenum == 1 else []]
    for i, j in zip(p_title, p_content):
        data.append([p_company , p_category, i, j])
    try:
        os.mkdir("csv_data")
    except:
        pass
    
    with open('./csv_data/{}(카테고리별).csv'.format(p_company), 'w' if p_pagenum == 1 else 'a', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

def main():
    kia_category = {"TOP 10":"top10", "차량 구매":"purchase", "차량 정비":"maintenance",\
                     "기아멤버스":"members", "홈페이지":"homepage", "PBV":"pbv", "기타":"etc"}
    page_num = 1
    for i in kia_category:
        page = KiaFAQCrawling(kia_category[i])
        title, content = Extract_title_content(page)
        Write_CSV(page_num, title, content, "기아자동차", i)
        if page_num == 1: page_num = 2
    df = 현대자동차FAQ.Final_data("기아자동차(카테고리별)")

    print(df)
    return df
if __name__ == "__main__":
    main()