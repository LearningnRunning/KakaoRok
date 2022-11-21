import pprint
import random
from collections import Counter

import pandas as pd

# matki_DB 경로설정
tmp_df = pd.read_csv("./matki_DB.csv")
region_lst = list(set(tmp_df["region"].to_list()))

print()
for i, v in enumerate(region_lst):
    print(i, ": ", v)
print()
print("깐깐한 리뷰어들이 극찬한 음식점을 찾아줍니다.")
region = int(input("검색할 지역을 입력해주세요 : "))
print()

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
    print(i, ": ", v)

print()
cat1 = input("카테고리를 설정해주세요(번호) : ")
print()


restaurantAverageRating = 3
personalAverageScore = 4.3
thisRestaurantScore = 4
RestaurantType = cat[int(cat1)]
result_df = tmp_df[
    (tmp_df["region"].isin([region_lst[region]]))
    & (tmp_df["score_min"] >= restaurantAverageRating)
    & (tmp_df["rate"] <= personalAverageScore)
    & (tmp_df["reviewAt"] >= thisRestaurantScore)
    & (tmp_df["cat1"] == RestaurantType)
]
print()
print("-" * 80)
print(RestaurantType, "(음식점, 깐깐한 리뷰어 수)")
print("-" * 80)
result_lst = Counter(result_df["name"].to_list()).most_common()
for result in result_lst:
    try:
        print("-" * 80)
        print(result)
        personalAverageScoreRow = 3.2
        thisRestaurantScore = 2.0
        row_df = tmp_df[
            (tmp_df["name"] == result[0])
            & (tmp_df["rate"] >= personalAverageScore)
            & (tmp_df["reviewAt"] <= thisRestaurantScore)
        ]
        if len(row_df) >= 3:
            print("불호가 너무 많은 식당입니다. 불호 개수 : {}".format(len(row_df)))
            continue
        detail = result_df[result_df["name"] == result[0]].iloc[0, :]
        if type(detail["likePoint"]) != float:
            likePoint = detail["likePoint"].split("@")
            likePointCnt = detail["likePointCnt"].split("@")
            likePointList = []
            for l, c in zip(likePoint, likePointCnt):
                tmp = l + ": " + c
                likePointList.append(tmp)
                likePoint_tmp = "/ ".join(likePointList)

            print(likePoint_tmp)
        print()
        print(detail["cat2"])

    except Exception as err:
        print(err)
        continue
print("-" * 80)
# choicelist = random.choice(list(result_lst))
# print("랜덤 픽 : ", choicelist)
print("-" * 80)
