import sys

import requests
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
import time
import os
from urllib import  request
#acquire book id :34444648 and design a loop to read all short comments
#static website
from pandas import ExcelWriter
import openpyxl
url = "https://book.douban.com/subject/2567698/comments/"


#change page
def main():

    url3 = 'https://book.douban.com/subject/6518605/comments/?start='
    past_comment_url = "&limit=20&status=P&sort=new_score"
    now_comment_url = ""
    future_comment_url = ""
    #DataScrapping
    #Data Structure Created
    saveData(pd.DataFrame([('Time','Star','Recommendation','Likes','Comment','User_link','Comment_Type')]))
    acquireData(url3,now_comment_url,'Now')
    acquireData(url3,past_comment_url,'Past')
    acquireData(url3,future_comment_url,'Future')
#url = url1+str(i*20)+url2
def saveData(data):
    # save_path1 = "Douban_Comments.csv"
    save_path2 = "Douban_Comment_2.csv"

    data.to_csv(save_path2,header=False,mode='a+',index = False)
    # f = open(save_path2,mode = 'a+')
    # f.writelines(data)
    # f.close()
    # with ExcelWriter(save_path2,mode = 'a') as writer:
    #     data.to_excel(writer, header=False, sheet_name='Douban_Comments',encoding='utf-8')
def acquireData(url2,url3,status):
    # header
    header = {'content-type': 'text/html; charset=utf-8',
              'User-Agent': ''}
    # cookie
    cookie = {
        "Cookies:":""
    }
    # url
    i = 0
    #addresses = pd.Series(dtype='str')
    findlink = re.compile(r'<a href="(.*?)">')
    findLikes = re.compile(r'<span class="vote-count".*>(\d*?)</span>')
    findComments = re.compile(r'class="short">(.*)</span>')
    print('Start scrapping data from the %s readers' % status)
    time.sleep(2)
    while True:
        address = url2+str(i*20)+url3
        #addresses.append(pd.Series(address),ignore_index=True)
        print( "\n the page we are going to mine is page %d",i+1)
        try:
            html = requests.get(address, headers =header , cookies = cookie)
            soup = BeautifulSoup(html.content,'html.parser')
            comment_items  = soup.find_all('div', attrs = {'class':'comment'}) #html labels and attributes
            #print(len(comment_items))
            if len(comment_items) == 0 :
                print("No more comments.")
                break
            for item in comment_items:
                item = str(item)
                # print(item)
                try:
                    if re.findall(findRating, item) ==[] or re.findall(findRecom, item) == []:
                        data1 = [(re.findall(findTime, item)[0],
                                  'none','none',
                                  re.findall(findLikes, item)[0],
                                  re.findall(findComments, item)[0],
                                  re.findall(findlink, item)[0],status)]
                        print("This comment gives no rating.")
                    else:
                        data1 = [(re.findall(findLikes,item)[0],
                                  re.findall(findComments,item)[0],
                                 re.findall(findlink,item)[0],status)]
                        print('one entry is collected')
                    data2 = pd.DataFrame(data1)
                    saveData(data2)
                except IndexError:
                    print(IndexError)
                    continue
        except ValueError as e:
            print("Valueerror",data1)
            break
        #addresses = pd.DataFrame(addresses)
        #addresses.to_csv('Comment_Addresses.csv',header=False,mode = "a+")
        i +=1
        time.sleep(2)
if __name__ == '__main__':
    main()