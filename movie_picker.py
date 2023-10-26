# -*- coding: utf-8 -*-
'''
@Time    : 2023/10/24 17:16
@Author  : Hsiehzhijun
@File    : movie_picker.py
'''
import requests
from bs4 import BeautifulSoup
import pandas as pd
import lxml
import os
from datetime import datetime
from loguru import logger
logger.add("./logs/movie_picker.log")
now = datetime.now()
current_year = now.strftime("%Y")
time_n = now.strftime("%M%S")
class Movie_picker:
    def __init__(self,year,year_to,month,month_to,sort):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://eiga.com/release/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            }
        self.params = {
            'year': year,  # '2022',
            'month': month,  # '1',
            'year_to': year_to,  # '2022',
            'month_to': month_to,  # '12',
            'sort': sort,  # 'rate',
        }


    def get_movie_html(self):
        response = requests.get('https://eiga.com/release/q/', params=self.params, headers=self.headers)
        html = response.text

        # print(html)
        soup = BeautifulSoup(html, 'lxml')
        div_movie_list = soup.find_all('div', class_="list-result list-block")
        movie_data = {}
        for div_movie in div_movie_list:
            m_id = ""
            title = ''
            producer = ""
            produced_in = ""
            video_len = ""
            origin = ""
            director = ""
            actors = ""
            rating = ""
            reviews = ""
            try:
                m_id = div_movie.attrs.get('id',[])
                movie_data[m_id] = {}
                title = div_movie.find('h2',class_="title").getText()
                movie_data[m_id]['title'] = title
                try:
                    cast_staff = div_movie.find('ul', class_="cast-staff").find_all('li')
                    for staff in cast_staff:
                        if '監督' in str(staff):
                            director = staff.find('span').getText()
                        else:
                            actors = staff.find('span').getText()
                        movie_data[m_id]['director'] = director
                        movie_data[m_id]['actors'] = actors
                except Exception as e:
                    logger.error(f'{m_id}No staff found:{e}')
                    pass
                checkin_count = div_movie.find('strong', class_="checkin-count").getText()
                movie_data[m_id]['checkin_count'] = checkin_count
                datas = div_movie.find('p', class_="data").getText().split('／')
                try:
                    for data in datas:
                        if '年製作'in data:
                            produced_in = data.strip()
                        elif '分'in data:
                            video_len = data.strip()
                        else:
                            origin = data.split(" ")[0]
                            producer = data.split(" ")[1]
                except Exception as e:
                    logger.error(f'{m_id}No datas found:{e}')
                    pass
                movie_data[m_id]['produced_in'] = produced_in
                movie_data[m_id]['origin'] = origin
                movie_data[m_id]['video_len'] = video_len
                movie_data[m_id]['producer'] = producer
                review_average = div_movie.find('a', class_="review-average")
                review_average_span = review_average.find_all('span')
                try:
                    for rev_aver in review_average_span:
                        if reviews == '' and "件" in rev_aver.getText():#or '件' in rev_aver.getText()
                            reviews = rev_aver.getText()
                        elif rating == '':
                            rating = rev_aver.getText()
                        else:
                            # print(rev_aver)
                            pass
                except Exception as e:
                    logger.error(f'{m_id}No review_average_span found:{e}')
                movie_data[m_id]['rating'] = rating
                movie_data[m_id]['reviews'] = reviews
            except Exception as e:
                logger.error(f'{m_id}:{e}')
                pass
            finally:
                movie_data[m_id]['title'] = title
                movie_data[m_id]['director'] = director
                movie_data[m_id]['actors'] = actors
                movie_data[m_id]['checkin_count'] = checkin_count
                movie_data[m_id]['produced_in'] = produced_in
                movie_data[m_id]['origin'] = origin
                movie_data[m_id]['video_len'] = video_len
                movie_data[m_id]['producer'] = producer
                movie_data[m_id]['rating'] = rating
                movie_data[m_id]['reviews'] = reviews
        return movie_data
def get_period():
    print('Please enter the period you want to query')
    result = False
    period_dict ={}
    try:
        year = str(input("The year from~to (ex:1930~2023):")).strip()
        month = str(input("The month from (ex:1~12):")).strip()
        period_dict['year_from'] = year.split("~")[0]
        period_dict['month_from'] = month.split("~")[0]
        period_dict['year_to'] = year.split("~")[1]
        period_dict['month_to'] = month.split("~")[1]
        if len(year.split("~")) == 2:
            pass
        else:
            print('ERROR in your entered,pls try again.')
            return False, {}

        if len(month.split("~")) == 2:
            pass
        else:
            print('ERROR in your entered,pls try again.')
            return False , {}

        if int(period_dict['year_from']) <= int(period_dict['year_to']) <= int(current_year):
            pass
        else:
            print('ERROR in your entered,pls try again.')
            return False , {}

        if int(period_dict['month_from']) <= int(period_dict['month_to']) and int(period_dict['month_to']) < 13:
            pass
        else:
            print('ERROR in your entered,pls try again.')
            return False , {}
        result = True
        return  result,period_dict
    except Exception as e:
        print(e)
        print('ERROR in your entered,pls try again.')
        return False , {}

if __name__ == '__main__':
    again_bool = True
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.max_columns',None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', 13)
    pd.set_option('display.width', None)
    while again_bool == True:
        os.system('cls')
        print("Search movie_list from URL: https://eiga.com/release/\n***This WebPage's language is Japanese ,pls encode with utf-8 ***\n")
        result = False
        while result == False:
            result , mv_dict = get_period()
        # mp = Movie_picker(year="2022",year_to="2022",month="1",month_to="12",sort="rate")
        print("Searching Movie_list ...")
        mp = Movie_picker(year=mv_dict['year_from'],
                          year_to=mv_dict['year_to'],
                          month=mv_dict['month_from'],
                          month_to=mv_dict['month_to'],
                          sort="rate")
        data = mp.get_movie_html()
        df = pd.DataFrame.from_dict(data, orient="index")
        print(df)
        try:
            print(f'Write to CSV...')
            df.to_csv(f"./movie_list_{mv_dict['year_from']}_{mv_dict['month_from']}-{mv_dict['year_to']}_{mv_dict['month_to']}t{time_n}.csv",encoding="utf_8")
            again = input("Search movie again?(Y or N):")
            if str(again).upper() == "Y":
                again_bool = True
            elif str(again).upper() == "N":
                again_bool = False
            else:
                print("get answer Error,back to movie search")
                again_bool = True
        except PermissionError:
            print('********\nThe file is be opened right now\nplease close movie_list_today.csv and try again\n********')
            again_bool = True


    '''<div class="list-result list-block" id="mv96522"> 
            <div class="checkin-popup-point" style="position: relative"></div> 
            <div class="img-box"> 
                <a href="/movie/96522/"><img alt="旅のはじまり" height="134" loading="lazy" src="https://eiga.k-img.com/images/movie/96522/photo/cec4aa3888f74bf2/320.jpg?1646100937" width="200"/></a> 
                <small class="time"> 劇場公開日 <span> 2022年4月8日 </span> </small> 
             </div> 
            <div class="txt-box"> 
                <h2 class="title"><a href="/movie/96522/">旅のはじまり</a></h2> 
                <p class="txt">虐待やネグレクト、非行などにより居場所を失った子どもたちの心に迫ったドキュメンタリー。虐待や家庭環境などで児童相談所を経由した15～2...</p> 
                <ul class="cast-staff"> 
                    <li><span>松本和巳</span> 監督
                     </li> 
                 </ul>
             </div> 
            <div class="movie-information"> 
                <div class="movie-information-inner"> 
                    <div class="review-tool"> 
                        <div class="review-tool-inner">
                            <a class="review-average" data-google-interstitial="false" href="/movie/96522/review/">
                                <span class="rating-star small val50">5.0</span>
                                <span class="total-number icon-after arrowopen">全
                                    <span>1</span>
                                    件
                                </span> 
                             </a>
                         </div> 
                    </div> 
                    <div class="popular-tool"> 
                        <a class="icon-movie-checkin checkin-btn" data-google-interstitial="false" data-remote="true" href="/movie/96522/checkin/?r=https%3A%2F%2Feiga.com%2Frelease%2Fq%2F%3Fmonth%3D1%26month_to%3D12%26page%3D1%26sort%3Drate%26year%3D2022%26year_to%3D2022%23mv96522" rel="nofollow"> Check-in
                            <span>
                                <strong class="checkin-count">97</strong>
                                人
                             </span>
                         </a>
                     </div>
                </div> 
            </div> 
            <div class="box-bottom"> 
                <div class="txt-block"> 
                    <p class="data"> 2022年製作 ／85分 ／日本 <br/>テンダープロ </p>
                 </div> 
                <ul class="link-btn"> 
                    <li class="btn small color01 off">
                        <span class="icon theater">映画館を探す</span>
                     </li>
                    <li> 
                        <a class="btn small" href="/movie/96522/"> 
                            <span class="icon movie">作品情報</span> 
                         </a> 
                     </li>
                </ul> 
            </div> 
        </div>'''