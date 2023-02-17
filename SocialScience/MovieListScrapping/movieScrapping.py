# -*- coding = utf-8 -*-
# @Time:2020/10/29 7:05 PM
# @Author: Zheng Zeng
# @File: sundance.py
# @Goal:
import sys
from builtins import type

import requests
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
import time

#change page
def main():
    #They are all for 2020 movies
    #If you want to acquire movies from other years
    #Change the third variable year
    url1 = 'https://movie.douban.com/awards/sundance/'

    url2 = '/nominees?k=a'
    years = [2019,2018,2017,2016,2015]
    levelsundance = [35,34,33,32,31]
    for i in range(len(years)):
        if i in range(2):
            acquireData1(url1,url2,years[i],levelsundance[i])
        else:
            break
    acquireData(url1,url2,years[2],levelsundance[2],16,16,12,10)
    acquireData(url1,url2,years[3],levelsundance[3],15,16,12,10)
    acquireData(url1,url2,years[4],levelsundance[4],15,16,12,12)
    shanghai1 = 'https://movie.douban.com/awards/siff/'
    shanghai2 = '/nominees?k=a'
    levelshanghai = [22,21,20,19,18]
    for i in range(len(years)):
        acquireData1(shanghai1,shanghai2,years[i],levelshanghai[i])
    # sundance1 = 'https://movie.douban.com/awards/sundance/'
    # sundance2 = '/nominees?k=a'
    # acquireData(sundance1,sundance2,35,'Sundance')
    # beijing = 'https://movie.douban.com/awards/bjiff/9/nominees'
#url = url1+str(i*20)+url2
def saveData(data,path):
    data.to_csv(path,header=False,mode='w',index = False)
def acquireData1(url1,url2,year,festival):
    # header
    header = {'content-type': 'text/html; charset=utf-8',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36'}
    # cookie
    cookie = {
        'Cookie':'viewed="2567698"; bid=viXzBneGrF8; gr_user_id=0334e848-9bbf-4d73-8898-d4843912e813; __utmc=30149280; _vwo_uuid_v2=D01EB491254F592B484FB2A07969757CE|b12b4c74ae211f2fc1917e89765461ee; __gads=ID=90dd3cb3600fbce3:T=1600906474:S=ALNI_MbgIYMcj5ViQlPJtQIhc74doHZixg; ll="128332"; __utmz=30149280.1600946804.5.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; __utmv=30149280.22348; __yadk_uid=5pTDDY5ooVxNqvQYQUmA7hwUbV686tvz; ap_v=0,6.0; __utma=30149280.1922991655.1600906474.1600995655.1603810552.9; __utmt=1; push_noty_num=0; push_doumail_num=0; dbcl2="223483866:0vAj5ECVXdk"; ck=apVC; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1603810706%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; _pk_id.100001.8cb4=dcf57d72cc7a2e72.1600929321.6.1603810706.1600963200.; _pk_ses.100001.8cb4=*; __utmb=30149280.5.10.1603810552'
    }
    # url
    url = url1+str(festival)+url2
    print('Start scrapping data of movies from %d, %s' % (year,festival) )
    time.sleep(2)
    try:
        html = requests.get(url, headers =header , cookies = cookie)
        soup = BeautifulSoup(html.content,'html.parser')
        title = soup.select('div.article>h1')
        # names = soup.select('div.rst_info>h4>a')
        # directors = soup.select('div.rst_info>p.r_metas>a')
        awardnames = soup.select('div.levl2.channels>h3')
        # types = soup.select('div.levl3>h4')
        # print(title[0].text)
        # print('length of title', len(title))
        # # print(names)
        # print('length of names', len(names))
        # print(types)
        groups = soup.select('div.levl2.channels')
        nominated = soup.select('div.rst_info')
        namepattern = re.compile(r'<a href=".*">(.*?)</a></h4>')
        directorpattern = re.compile(r'<a href=".*">(.*?)</a></p>')
        directors = []
        names = re.findall(namepattern,str(groups[0]))

        for nom in nominated:
            item = str(nom)
            director = re.findall(directorpattern,item)
            if director ==[]:
                director = 'Unkown'
                directors.append(director)
            else:
                directors.append(director[0])
            print(title,director)
        datalen = min(len(names),len(directors))
        print(datalen)
        movienames = names[0:datalen]
        directornames = directors[0:datalen]
        data = pd.DataFrame()
        data['Name'] = movienames
        data['Director'] = directornames
        typepattern = re.compile(r'<h4.*>(.*?)</h4>')
        doc = 15
        drama = 31
        wcdrama = 33
        wocdoc = 55

        types = re.findall(typepattern,str(groups[0]))
        typess = []
        for type in types:
            if type !='':
                typess.append(type)
        print(len(typess))
        movietype = [typess[0] for i in range(doc+1)]
        for i in range(16):
            movietype.append(typess[1])
        for i in range(12):
            movietype.append(typess[2])
        for i in range(12):
            movietype.append(typess[3])
        print(len(movietype))
        data['Year'] = [year for i in range(datalen)]
        data['MovieType'] = movietype
        data['Award'] = [awardnames[0].text for i in range(datalen)]
        print(data.head(5))
        filename = title[0].text.strip()
        path = filename+'.csv'
        saveData(data,path)
    except IndexError:
        print(IndexError)
    except ValueError as e:
        print("Valueerror",sys.exc_info())

        time.sleep(2)

def acquireData(url1,url2,year,festival,doc,drama,wcdoc,wcdrama):
    # header
    header = {'content-type': 'text/html; charset=utf-8',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36'}
    # cookie
    cookie = {
        'Cookie': 'viewed="2567698"; bid=viXzBneGrF8; gr_user_id=0334e848-9bbf-4d73-8898-d4843912e813; __utmc=30149280; _vwo_uuid_v2=D01EB491254F592B484FB2A07969757CE|b12b4c74ae211f2fc1917e89765461ee; __gads=ID=90dd3cb3600fbce3:T=1600906474:S=ALNI_MbgIYMcj5ViQlPJtQIhc74doHZixg; ll="128332"; __utmz=30149280.1600946804.5.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; __utmv=30149280.22348; __yadk_uid=5pTDDY5ooVxNqvQYQUmA7hwUbV686tvz; ap_v=0,6.0; __utma=30149280.1922991655.1600906474.1600995655.1603810552.9; __utmt=1; push_noty_num=0; push_doumail_num=0; dbcl2="223483866:0vAj5ECVXdk"; ck=apVC; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1603810706%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; _pk_id.100001.8cb4=dcf57d72cc7a2e72.1600929321.6.1603810706.1600963200.; _pk_ses.100001.8cb4=*; __utmb=30149280.5.10.1603810552'
    }
    # url
    url = url1 + str(festival) + url2
    print('Start scrapping data of movies from %d, %s' % (year, festival))
    time.sleep(2)
    try:
        html = requests.get(url, headers=header, cookies=cookie)
        soup = BeautifulSoup(html.content, 'html.parser')
        title = soup.select('div.article>h1')
        # names = soup.select('div.rst_info>h4>a')
        # directors = soup.select('div.rst_info>p.r_metas>a')
        awardnames = soup.select('div.levl2.channels>h3')
        # types = soup.select('div.levl3>h4')
        # print(title[0].text)
        # print('length of title', len(title))
        # # print(names)
        # print('length of names', len(names))
        # print(types)
        groups = soup.select('div.levl2.channels')
        nominated = soup.select('div.rst_info')
        namepattern = re.compile(r'<a href=".*">(.*?)</a></h4>')
        directorpattern = re.compile(r'<a href=".*">(.*?)</a></p>')
        directors = []
        names = re.findall(namepattern, str(groups[0]))

        for nom in nominated:
            item = str(nom)
            director = re.findall(directorpattern, item)
            if director == []:
                director = 'Unkown'
                directors.append(director)
            else:
                directors.append(director[0])
            print(title, director)
        datalen = min(len(names), len(directors))
        print(datalen)
        movienames = names[0:datalen]
        directornames = directors[0:datalen]
        data = pd.DataFrame()
        data['Name'] = movienames
        data['Director'] = directornames
        typepattern = re.compile(r'<h4.*>(.*?)</h4>')
        types = re.findall(typepattern, str(groups[0]))
        typess = []
        for type in types:
            if type != '':
                typess.append(type)
        print(len(typess))
        movietype = [typess[0] for i in range(doc)]
        for i in range(drama):
            movietype.append(typess[1])
        for i in range(wcdrama):
            movietype.append(typess[2])
        for i in range(wcdoc):
            movietype.append(typess[3])
        print(len(movietype))
        data['Year'] = [year for i in range(datalen)]
        data['MovieType'] = movietype
        data['Award'] = [awardnames[0].text for i in range(datalen)]
        print(data.head(5))
        filename = title[0].text.strip()
        path = filename + '.csv'
        saveData(data, path)
    except IndexError:
        print(IndexError)
    except ValueError as e:
        print("Valueerror", sys.exc_info())

        time.sleep(2)
if __name__ == '__main__':
    main()
