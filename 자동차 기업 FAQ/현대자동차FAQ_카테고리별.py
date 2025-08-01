import csv
import requests
import json
import os
import 현대자동차FAQ_전체

def HyundaiFAQ_Crawling(p_pagenum, p_category):
    url = "https://www.hyundai.com/wsvc/front/biz/frontFaq.faqListArr.do?searchKeyword=&pageNo={}&frontSupiCtgr={}&frontCtgrScd="\
    .format(p_pagenum, p_category)
    response = requests.get(url)
    page = json.loads(response.text)

    return page

def Write_CSV(p_pagenum, p_categorynum, p_title, p_content, p_company, p_category):
    data = [["기업명", "카테고리" ,"제목", "내용"] if p_pagenum == 1 and p_categorynum == 1 else []]
    for i, j in zip(p_title, p_content):
        data.append([p_company , p_category, i, j])
    try:
        os.mkdir("csv_data")
    except:
        pass
    
    with open('./csv_data/{}(카테고리별).csv'.format(p_company), 'w' if (p_pagenum == 1 and p_categorynum == 1) else 'a', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

def main():
    category = {"차량구매":"01", "차량정비":"02", "정비예약":"03", "홈페이지":"04", "모젠서비스":"09", "블루링크":"10", \
                "특허관련":"11", "현대 디지털 키":"12"}
    categorynum = 1

    for i in category:
        pagenum = 1
        while True:
            page = HyundaiFAQ_Crawling(pagenum, category[i])
            title, content = 현대자동차FAQ_전체.Extract_title_content(page)
            if not title:
                df = 현대자동차FAQ_전체.Final_data("현대자동차(카테고리별)")
                categorynum += 1
                break
            Write_CSV(pagenum, categorynum, title, content, "현대자동차", i)
            pagenum += 1

    print(df)
    return df

main()