# -*- coding = utf-8 -*-
# @Time:2020/9/24 2:31 PM
# @Author: Zheng Zeng
# @File: nestedDouban.py
# @Goal:

import requests
import time
import pandas as pd
import re
import json
from json import decoder
import sys
import numpy as np
from bs4 import  BeautifulSoup
import pandas as pd
def main():
    #data = pd.read_csv('Douban_Comments.csv',header = 0)
    data = pd.read_csv('Douban_Comment_2.csv',header = 0)
    print(data.head(5))
    userlinks =data['User_link']
    userinfo = []
    for url in userlinks:
        try:
            user = userData(url)
            userinfo.append(user)
            print('finish one user.')
            time.sleep(0.5)
        except KeyError:
            print('Key error for one link')
            pass
        except ValueError:
            print('Value error for one link')
            pass
        except IndexError:

            print('no longer active.')
            pass
    dat = pd.DataFrame(userinfo,
    columns = ['User_link', 'Location', 'JoinDate', 'BookStatus','BooksPref', 'MovieStatus', 'MoviePref'])
    dat.to_csv('Douban_user2.csv',header=True,mode='w')
    douban = pd.merge(dat,data,left_on='User_link',right_on='User_link')
    print(douban.info)
    douban.to_csv('Douban_Full2.csv',index=False,header=True)
def userData(url):
    try:
        user = []
        user.append(url)
        # header
        header = {'content-type': 'text/html; charset=utf-8',
                  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
        # cookie
        #cookie = {
         #   'Cookie': 'bid=AQtttWCQMCo; __utmc=30149280; ll="118281"; __gads=ID=d2356cf3b2409175-2260df7282c300ed:T=1600161257:RT=1600161257:S=ALNI_MbeWFNYV4TmqdWgRhRgpDsHG96GGg; _vwo_uuid_v2=DEB4B182FAEA57955C8A18BE80FDEE095|a9165fab04d72183fa452578abd45b89; douban-fav-remind=1; __utmz=30149280.1600177171.3.3.utmcsr=movie.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/review/best/; dbcl2="223483866:My+O6tLzvj0"; ck=O_oD; push_noty_num=0; push_doumail_num=0; __utmv=30149280.22348; __yadk_uid=dZjicISnXk4ix8zJWhLLtJML3YxShIDG; gr_user_id=4988752f-0dd1-4345-8b07-057ea9487d2c; __utmc=81379588; __utmz=81379588.1600178167.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1600409209%2C%22https%3A%2F%2Fsearch.douban.com%2Fmovie%2Fsubject_search%3Fsearch_text%3D%25E4%25B8%2589%25E4%25BD%2593%26cat%3D1002%22%5D; _pk_ses.100001.3ac3=*; ap_v=0,6.0; __utma=30149280.395720426.1600160246.1600354232.1600409209.6; __utmt_douban=1; __utma=81379588.1930643767.1600178167.1600354232.1600409209.3; __utmt=1; _pk_id.100001.3ac3=d546f6dc403e1f28.1600178070.3.1600409653.1600354232.; __utmb=30149280.3.10.1600409209; __utmb=81379588.3.10.1600409209'}
        cookie ={'Cookie':'viewed="2567698"; bid=viXzBneGrF8; gr_user_id=0334e848-9bbf-4d73-8898-d4843912e813; __utmc=30149280; _vwo_uuid_v2=D01EB491254F592B484FB2A07969757CE|b12b4c74ae211f2fc1917e89765461ee; __gads=ID=90dd3cb3600fbce3:T=1600906474:S=ALNI_MbgIYMcj5ViQlPJtQIhc74doHZixg; loc-last-index-location-id="128332"; ll="128332"; push_noty_num=0; push_doumail_num=0; ct=y; __utmz=30149280.1600946804.5.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; __utmv=30149280.22348; __yadk_uid=5pTDDY5ooVxNqvQYQUmA7hwUbV686tvz; ap_v=0,6.0; gr_cs1_7e9471d2-6942-4124-8332-381fb50d7e79=user_id%3A0; __utma=30149280.1922991655.1600906474.1600959121.1600962349.7; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=6907e769-3d60-411a-9429-6e3941598042; gr_cs1_6907e769-3d60-411a-9429-6e3941598042=user_id%3A1; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_6907e769-3d60-411a-9429-6e3941598042=true; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1600963067%2C%22https%3A%2F%2Faccounts.douban.com%2Fpassport%2Flogin%22%5D; _pk_ses.100001.8cb4=*; __utmt=1; dbcl2="223483866:asJPBIjtpJ4"; ck=tc1Q; _pk_id.100001.8cb4=dcf57d72cc7a2e72.1600929321.5.1600963191.1600959120.; __utmb=30149280.15.10.1600962349'}
        res = requests.get(url,headers = header,cookies =cookie)
        bs = BeautifulSoup(res.content,'html.parser')
        location = bs.select('div.user-info>a')
        joining = bs.select('div.user-info')
        # print(joining)
        timepattern = re.compile(r'(\d{4}-\d{1,2}-\d{1,2})')
        joindate = re.findall(timepattern,str(joining))[0]
        #print(joindate)
        #about books
        pattern = re.compile(r'>(.*?)</a>')
        books = bs.select('div#book>h2>span.pl>a')
        booktype = iterate_text(pattern,books)
        bookslink= bs.select('div#book>div>ul>li.aob>a')
        bookshelf =iterate_title(bookslink)
        #about movies
        movies = bs.select('div#movie>h2>span.pl>a')
        movietype = iterate_text(pattern,movies)
        movieslink= bs.select('div#movie>div>ul>li.aob>a')
        movielist = iterate_title(movieslink)
        '''
        Now we collect all info
        '''
        user.append(location[0].text)
        user.append(joindate)
        user.append(','.join(booktype))
        user.append(bookshelf)
        user.append(','.join(movietype))
        user.append(movielist)
        print(user)

    except KeyError:
        print('This account is deleted.')
        pass
    except ValueError:
        print('There is a value error')
        pass
    except IndexError:
        print('Inactive User.')
        pass
    return user

def iterate_text(pattern, collection):
    list = []
    for item in collection:
        one = re.findall(pattern,str(item))[0]
        list.append(one)
    return list
def iterate_title(collection):
    list = []
    # print(len(collection))
    for item in collection:
        title = re.sub(r'\n','',item['title'])
        list.append(title)
    combo  = ' '.join(list)
    return combo


if __name__ == '__main__':
    main()