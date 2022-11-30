import os
import random
import re
from collections import Counter
from time import sleep

import folium
import numpy as np
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from folium.plugins import MarkerCluster
from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from streamlit_folium import st_folium

st.sidebar.header("맛키맛키 ")
name = st.sidebar.selectbox("menu", ["Welcome", "kakaoRok", "KakaoCrawler"])

if name == "Welcome":
    st.write("# Hello")

    st.write("## 실행방법")
    st.write(" 터미널 창\n streamlit run app.py")
    st.write("## 환경설정")
    st.write("폴더 내의 크롬드라이버 버전 맞추기!")

    st.write("## 사용방법")
    st.write("### 1. 맛키맛키_ 걍 input 하라는대로!")
    st.write(
        '### 2. 크롤러_ 예를 들어 "부산 서면" 이라고 친다면 부산 서면 맛집 450개를 스크래핑하여 matki_DB 데이터에 추가됩니다! '
    )

elif name == "kakaoRok":
    # matki_DB 경로설정
    tmp_df = pd.read_csv("./matki_DB.csv")
    region_lst = list(dict.fromkeys(tmp_df["region"].to_list()))

    st.write()
    st.write("깐깐한 리뷰어들이 극찬한 음식점을 찾아줍니다.")

    cat = [
        "베이커리,카페",
        "패스트푸드",
        "샌드위치,샐러드",
        "육류",
        "해산물",
        "한식",
        "일식",
        "양식",
        "중식",
        "기타",
        "면류",
        "술집",
        "찌개,국밥",
    ]

    for i, v in enumerate(cat):
        st.write(i, ": ", v)

    input_cat = st.text_input("카테고리를 설정해주세요(번호) : ")
    if input_cat:

        restaurantAverageRating = 3
        personalAverageScore = 4.3
        thisRestaurantScore = 4
        RestaurantType = cat[int(input_cat)]
        result_df = tmp_df[
            (tmp_df["score_min"] >= restaurantAverageRating)
            & (tmp_df["rate"] <= personalAverageScore)
            & (tmp_df["reviewAt"] >= thisRestaurantScore)
            & (tmp_df["cat1"] == RestaurantType)
        ]
        st.write()
        st.write("# {}(음식점, 깐깐한 리뷰어 수)".format(RestaurantType))

        result_lst = Counter(result_df["name"].to_list()).most_common()
        m = folium.Map(location=[37.5197424168999, 126.940030048557], zoom_start=12)
        marker_cluster = MarkerCluster().add_to(m)
        for result in result_lst:
            try:
                personalAverageScoreRow = 3.2
                thisRestaurantScore = 2.0
                row_df = tmp_df[
                    (tmp_df["name"] == result[0])
                    & (tmp_df["rate"] >= personalAverageScore)
                    & (tmp_df["reviewAt"] <= thisRestaurantScore)
                ]

                detail = result_df[result_df["name"] == result[0]].iloc[0, :]
                if type(detail["likePoint"]) != float:
                    likePoint = detail["likePoint"].split("@")
                    likePointCnt = detail["likePointCnt"].split("@")
                    likePointList = []
                    for l, c in zip(likePoint, likePointCnt):
                        tmp = l + ": " + c
                        likePointList.append(tmp)
                        likePoint_tmp = "/ ".join(likePointList)
                if len(row_df) >= 3:
                    bad_review = "불호가 너무 많은 식당입니다. 불호 개수 : {}".format(len(row_df))
                    iframe = "{0} <br> {1}".format(result[0], bad_review)
                else:
                    iframe = "{0} / {1}명 <br> {2} <br>{3}".format(
                        result[0], result[1], likePoint_tmp, detail["cat2"]
                    )
                popup = folium.Popup(iframe, min_width=200, max_width=500)

                folium.Marker(
                    [detail["lat"], detail["lon"]],
                    icon=folium.Icon(color="green"),
                    popup=popup,
                    tooltip=name,
                ).add_to(marker_cluster)
            except Exception as err:
                st.write(err)
                continue
        st_data = st_folium(m, width=1080)


elif name == "KakaoCrawler":
    st.write("# 검색할 맛집을 입력해주세요.")
    region = st.text_input("OO 맛집으로 검색됩니다.")
    if region:
        options = webdriver.ChromeOptions()
        options.add_argument("lang=ko_KR")
        options.add_argument("headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("disable-gpu")
        executable_path = "./chromedriver"  # 크롬 드라이버 위치 수정

        # driver = webdriver.Chrome(os.path.join(os.getcwd(), chromedriver_path), options=options)  # chromedriver 열기
        # 크롤링할 사이트 주소를 정의합니다.
        source_url = "https://map.kakao.com/"

        # 크롬 드라이버를 사용합니다 (맥은 첫 줄, 윈도우는 두번째 줄 실행)
        # driver = webdriver.Chrome(path)
        driver = webdriver.Chrome(executable_path=executable_path, options=options)

        # 카카오 지도에 접속합니다
        driver.get(source_url)

        # 검색창에 검색어를 입력합니다
        searchbox = driver.find_element(By.XPATH, "//input[@id='search.keyword.query']")
        searchbox.send_keys("{0} 맛집".format(region))

        # 검색버튼을 눌러서 결과를 가져옵니다
        searchbutton = driver.find_element(
            By.XPATH, "//button[@id='search.keyword.submit']"
        )
        driver.execute_script("arguments[0].click();", searchbutton)

        # 검색 결과를 가져올 시간을 기다립니다
        sleep(2)

        # 검색 결과의 페이지 소스를 가져옵니다
        html = driver.page_source

        driver.find_element(By.XPATH, "/html/body/div[10]/div/div/div/span").click()
        sleep(2)
        # 더보기 클릭
        driver.find_element(By.XPATH, "//*[@id='info.search.place.more']").click()
        sleep(2)
        # 1~ 5페이지 링크 얻기
        page_urls = []
        cnt = 0
        while driver.find_element(
            By.XPATH, '//a[@id="info.search.page.no5"]'
        ).is_displayed():
            for i in range(1, 6):
                page = driver.find_element(By.ID, "info.search.page.no" + str(i))
                page.click()
                sleep(2)
                urls = driver.find_elements(By.LINK_TEXT, "상세보기")
                for j in range(len(urls)):
                    url = urls[j].get_attribute("href")
                    st.write(url)
                    page_urls.append(url)
            if (not bool(10 % 5)) & (
                not bool(
                    driver.find_elements(By.XPATH, '//button[@class="next disabled"]')
                )
            ):
                driver.find_elements(By.XPATH, '//button[@id="info.search.page.next"]')[
                    0
                ].click()

        columns = [
            "region",
            "name",
            "addresse",
            "cat1",
            "cat2",
            "review_num",
            "blog_review_num",
            "score_min",
            "likePoint",
            "likePointCnt",
            "rate",
            "reviewerCnt",
            "reviewAt",
            "review",
            "reviews_date",
            "reviewer_id",
        ]
        # 사업장명, 주소, 음식종류1,음식종류2(메뉴),리뷰수,별점,리뷰
        df = pd.DataFrame(columns=columns)

        for i, page_url in enumerate(page_urls):

            # 상세보기 페이지에 접속합니다
            driver.get(page_url)
            wait = WebDriverWait(driver, 3)
            element = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "link_place"))
            )
            st.write(i)

            if driver.find_elements(
                By.XPATH, '//div[@class="box_grade_off"]'
            ):  # 후기를 제공하지 않는 맛집 넘기기
                continue

            # 사업장명

            name = driver.find_element(By.XPATH, '//div[@class="inner_place"]/h2').text

            # 사업장 주소
            address = driver.find_element(By.XPATH, '//span[@class="txt_address"]').text

            # 평균 별점
            score_min = driver.find_element(
                By.XPATH,
                '//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/div/a[1]/span[1]',
            ).text

            # 리뷰수
            review_num = driver.find_element(By.XPATH, '//span[@class="color_g"]').text[
                1:-2
            ]

            # 블로그리뷰수
            blog_review_num = driver.find_element(
                By.XPATH, '//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/div/a[2]/span'
            ).text

            # 음식 종류
            cat1 = driver.find_element(
                By.XPATH, '//*[@id="mArticle"]/div[1]/div[1]/div[2]/div/div/span[1]'
            ).text

            # 메뉴
            cat2 = []

            menus = driver.find_elements(By.CLASS_NAME, "info_menu")
            for menu in menus:
                cat2.append(menu.text)

            # 식당 장점
            likePoints = driver.find_elements(By.XPATH, '//*[@class="txt_likepoint"]')
            likePointCnts = driver.find_elements(
                By.XPATH, '//*[@class="num_likepoint"]'
            )
            likePoint, likePointCnt = "", ""
            for p, c in zip(likePoints, likePointCnts):
                likePoint += p.text + "@"
                likePointCnt += c.text + "@"

            if driver.find_elements(
                By.XPATH, '//*[@id="mArticle"]/div[7]/div[3]/a/span[1]'
            ):
                # 리뷰 더보기 최대로
                while not bool(
                    driver.find_elements(
                        By.XPATH, '//a[@class="link_more link_unfold"]'
                    )
                ):
                    tmp_clk = driver.find_elements(By.XPATH, '//*[@class="txt_more"]')
                    wait = WebDriverWait(driver, 1)
                    element = wait.until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "link_more"))
                    )
                    try:
                        if tmp_clk[0].text == "후기 더보기":
                            tmp_clk[0].click()
                    except Exception as e:
                        st.write("클릭 예외가 발생되었습니다.")
                        pass

            try:
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                contents_div = soup.find(
                    name="div", attrs={"class": "evaluation_review"}
                )

                # 별점을 가져옵니다.
                rateNcnt = contents_div.find_all(
                    name="span", attrs={"class": "txt_desc"}
                )
                rateCnts = rateNcnt[::2]
                rates = rateNcnt[1::2]

                # 개인이 해당 식당에 남긴 별점
                rateAts = driver.find_elements(
                    By.XPATH, '//div[@class="grade_star size_s"]/span/span'
                )

                # 리뷰를 가져옵니다.
                reviews = contents_div.find_all(
                    name="p", attrs={"class": "txt_comment"}
                )

                # 리뷰를 쓴 날짜를 가져옵니다.
                reviews_dates = contents_div.find_all(
                    name="span", attrs={"class": "time_write"}
                )

                # 리뷰 아이디 가져오기
                reviews_ids = contents_div.find_all(
                    name="a", attrs={"class": "link_user"}
                )
                st.write("rateAts", len(rateAts), "reviews", len(reviews))
                # 데이터프레임으로 정리합니다.
                for rate, rateCnt, rateAt, review, reviews_date, reviews_id in zip(
                    rates, rateCnts, rateAts, reviews, reviews_dates, reviews_ids
                ):
                    rateAt = int(rateAt.get_attribute("style")[7:-2]) / 20
                    row = [
                        region,
                        name,
                        address,
                        cat1,
                        cat2,
                        review_num,
                        blog_review_num,
                        score_min,
                        likePoint,
                        likePointCnt,
                        rate.text,
                        rateCnt.text,
                        rateAt,
                        review.find(name="span").text,
                        reviews_date.text,
                        reviews_id.text,
                    ]
                    series = pd.DataFrame([row], columns=columns)
                    df = pd.concat([df, series])
            except Exception as e:
                st.write("예외가 발생되었습니다.", e)
        df = df.drop_duplicates(
            subset=["review", "reviewer_id", "reviews_date"], keep="first"
        )
        driver.close()

        cat = {
            "베이커리,카페": [
                "폴바셋",
                "파리크라상",
                "파리바게뜨",
                "투썸플레이스",
                "커피전문점",
                "커피빈",
                "카페마마스",
                "카페",
                "제과,베이커리",
                "던킨",
                "도넛",
                "디저트카페",
                "북카페",
                "스타벅스",
            ],
            "패스트푸드": ["KFC", "햄버거", "피자", "치킨", "노브랜드버거", "맥도날드", "버거킹"],
            "육류": [
                "하남돼지집",
                "곱창,막창",
                "닭요리",
                "장어",
                "샤브샤브",
                "스테이크,립",
                "삼겹살",
                "양꼬치",
                "오발탄",
                "연타발",
                "육류,고기",
            ],
            "해산물": ["해물,생선", "해산물뷔페", "회", "조개", "게,대게", "굴,전복", "매운탕,해물탕", "아구", "복어"],
            "술집": ["호프,요리주점", "칵테일바", "술집", "실내포장마차"],
            "찌개,국밥": ["해장국", "추어", "찌개,전골", "감자탕", "곰탕", "국밥", "설렁탕", "이화수전통육개장"],
            "한식": ["한식", "한정식", "도시락", "돈까스,우동", "떡볶이", "불고기,두루치기", "분식", "순대", "소호정"],
            "일식": ["퓨전일식", "초밥,롤", "참치회", "장어", "일식집", "일본식주점", "일식"],
            "기타": ["퓨전요리", "족발,보쌈", "경복궁", "경성양꼬치", "뷔페", "온더보더", "인도음식", "족발,보쌈"],
            "양식": [
                "패밀리레스토랑",
                "터키음식",
                "태국음식",
                "동남아음식",
                "베트남음식",
                "아시아음식",
                "아웃백스테이크하우스",
                "양식",
                "이탈리안",
            ],
            "중식": ["중식", "중국요리"],
            "면류": ["국수", "냉면", "일본식라면"],
            "샌드위치,샐러드": ["샐러디", "써브웨이", "샌드위치"],
        }

        def cat_change(string):
            for k, v in list(cat.items()):
                if string in v:
                    string = k
            return string

        df["cat1"] = df["cat1"].apply(cat_change)
        matki_all = pd.read_csv("./matki_DB.csv")
        matki_all = pd.concat([matki_all, df])
        # matki_all.drop_duplicates(subset=['review', 'reviewer_id'], keep='last')
        matki_all.to_csv(
            "matki_DB.csv", index=False, encoding="utf-8-sig"
        )  # index label을 따로 저장하지 않기
