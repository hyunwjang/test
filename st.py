import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

try:
    from PIL import *
except AttributeError: #module has no attribute ImageN
    import Image
    import ImageDraw
    import ImageFont
st.title('데이터 분석가를 꿈꾸는 장현우..')


image = Image.open('jang.jpg')

st.image(image, width =200)

st.write("데이터 분석이도 심리학의 기반이라 생각하기에 이리로 오게 되었습니다.")

st.subheader("나를 소개합니다")
selected_item = st.radio("학력", ("2017. 04 ~ 2019. 02", "2009. 02 ~ 2013. 02", "2009"))

if selected_item == "2017. 04 ~ 2019. 02":
    st.write("학점은행제 심리학과")
elif selected_item == "2009. 02 ~ 2013. 02":
    st.write("송호대학교 호텔관광과")
    
    # imageh = Image.open('highs.jpg')
    # st.image(imageh, width =200)
    
elif selected_item == "2009":
    st.write("세명컴퓨터고등학교 전기과")
    
    
if st.button("경력"):
      st.write("유니에스  (2018. 01 ~ 재직중)")
      st.write(" 청년내일채움공제 담당업무를 하고 있습니다.(노무,사무,상담)")
      
news_num =  st.number_input('페이지수', 100)
query  = st.text_input('네이버 검색어', '부동산')
# news_num  = 100
#news_num =  st.number_input(페이지수, value)

date = str(datetime.now())
date = date[:date.rfind(':')].replace(' ', '_')
date = date.replace(':','시') + '분'


# query = input('검색 키워드를 입력하세요 : ')
# news_num = int(input('총 필요한 뉴스기사 수를 입력해주세요(숫자만 입력) : '))
query = query.replace(' ', '+')


news_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}'

req = requests.get(news_url.format(query))
soup = BeautifulSoup(req.text, 'html.parser')


news_dict = {}
idx = 0
cur_page = 1

print()
print('크롤링 중...')

while idx < news_num:
### 네이버 뉴스 웹페이지 구성이 바뀌어 태그명, class 속성 값 등을 수정함(20210126) ###
    
    table = soup.find('ul',{'class' : 'list_news'})
    li_list = table.find_all('li', {'id': re.compile('sp_nws.*')})
    area_list = [li.find('div', {'class' : 'news_area'}) for li in li_list]
    a_list = [area.find('a', {'class' : 'news_tit'}) for area in area_list]
    
    for n in a_list[:min(len(a_list), news_num-idx)]:
        news_dict[idx] = {'title' : n.get('title'),
                          'url' : n.get('href') }
        idx += 1

    cur_page += 1

    pages = soup.find('div', {'class' : 'sc_page_inner'})
    next_page_url = [p for p in pages.find_all('a') if p.text == str(cur_page)][0].get('href')
    
    req = requests.get('https://search.naver.com/search.naver' + next_page_url)
    soup = BeautifulSoup(req.text, 'html.parser')

print('크롤링 완료')

print('데이터프레임 변환')
df = pd.DataFrame(news_dict).T

st.write(query,"  ", str(news_num)+ "개" )

st.dataframe(df.style.highlight_max(axis=0))

# st.write("st.table api")
# st.table(df)
from wordcloud import WordCloud

df_2 = df.drop(['url'], axis = 1)
from sklearn.feature_extraction.text import CountVectorizer

cvect = CountVectorizer()
dtm = cvect.fit_transform(df["title"])

feature_names = cvect.get_feature_names_out()
df_4 = pd.DataFrame(dtm.toarray(), columns=feature_names)
df8 = pd.DataFrame(df_4.sum())
df8.reset_index(inplace=True)
# print(df8)
df8.columns = ['title', 'count']
df_1 = df8
# print(df_1)
wc = df_1.set_index('title').to_dict()['count']
font = ImageFont.load_default()
#font = ImageFont.load("arial.pil")
#font = 'C:\Windows\Fonts\HMFMPYUN.ttf'
wordCloud = WordCloud(font_path=font,
                      width=400, height=400, 
                      scale=2.0,
                      max_font_size=250).generate_from_frequencies(wc)
fig = plt.figure()
plt.imshow(wordCloud)
plt.axis("off")
plt.show()
st.pyplot(fig)
