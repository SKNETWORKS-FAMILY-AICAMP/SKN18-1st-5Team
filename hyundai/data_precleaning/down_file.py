from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

# 1. 다운로드 받을 파일 연도 범위 설정
START_YEAR = 2017
END_YEAR = 2017

# 2. 연도별 반복복
for year in range(START_YEAR, END_YEAR + 1):
    # 연도별 다운로드 폴더 생성성
    download_dir = f"C:\\dev\\mini_1\\data\\{year}" 
    os.makedirs(download_dir, exist_ok=True) #해당 연도 폴더가 없으면 생성
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options) 
    driver.get("https://stat.molit.go.kr/portal/cate/statMetaView.do?hRsId=58&hFormId=5498")
    time.sleep(3)

    # li 항목 전체 찾기
    items = driver.find_elements(By.CSS_SELECTOR, "ul.file-sch-list > li")

    for item in items:
        try:
            em_text = item.find_element(By.TAG_NAME, "em").text.strip()
            if str(year) in em_text and "자동차" in em_text:
                print(f"다운로드 대상: {em_text}")
                a_tag = item.find_element(By.TAG_NAME, "a")
                driver.execute_script("arguments[0].click();", a_tag)
                time.sleep(5)  # 다운로드 대기
        except Exception as e:
            print("오류 발생:", e)
    driver.quit()
