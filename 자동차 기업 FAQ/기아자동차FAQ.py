import requests
import pandas as pd
import json
import re
import html
import csv
import 현대자동차FAQ

def KiaFAQCrawling():
    url = "https://www.kia.com/kr/services/ko/faq.search"
    response = requests.get(url)
    page = json.loads(response.text)

    return page

def Extract_title_content(p_page):
    title = [현대자동차FAQ.clean_html_text(i["question"]) for i in p_page["data"]["faqList"]["items"]]
    content = [현대자동차FAQ.clean_html_text(i["answer"]["html"]) for i in p_page["data"]["faqList"]["items"]]

    return title, content

def main():
    page = KiaFAQCrawling()
    title, content = Extract_title_content(page)
    현대자동차FAQ.Write_CSV(1, title, content, "기아자동차")
    df = 현대자동차FAQ.Final_data("기아자동차")

    print(df)
    return df

main()