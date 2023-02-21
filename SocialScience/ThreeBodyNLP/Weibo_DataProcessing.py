# -*- coding = utf-8 -*-
# @Time:2020/9/22 8:19 PM
# @Author: Zheng Zeng
# @File: Weibo_DataProcessing.py
# @Goal:
import requests
import time
import pandas as pd
import re
import json
from json import decoder
import sys
from bs4 import  BeautifulSoup
import pandas as pd
import jieba
def data_combine():
    w1 = pd.read_csv('Weibo_Comments1.csv',header =0)
    w2 = pd.read_csv('Weibo_Comments2.csv',header = 0)
    w = w1.append(w2)
    print(w['CommentCount'].sum())
    w.to_csv('Weibo_allComments.csv',header=0)
    print(w.info())

def main():
    #d = data_crawling()
    # = pd.DataFrame(d,columns=['User','Content'])
    # dataset.to_csv('weiboComment.csv',header=True,mode = 'w',index=False)
    dataset = pd.read_csv('weiboComment.csv',header=0)
    nlp(dataset)
def nlp(data):
    contents = data['Content']
    cut = jieba.cut(contents)

def data_crawling():
    netflix_url = 'https://s.weibo.com/weibo/%2523Netflix%25E6%258B%258D%25E5%2589%25A7%25E7%2589%2588%25E4%25B8%2589%25E4%25BD%2593%2523?topnav=1&wvr=6&b=1&page='
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
    cookie = {
        'Cookie': 'T_WM=31239011660; WEIBOCN_FROM=1110006030; XSRF-TOKEN=fe3242; SSOLoginState=1600693115; ALF=1603285115; SCF=AlP_mTLbuiTgrGeZvPlyLDDKKbVdedTrgGSSWHsxXnj3KAQSSOZX_ewhfhpizHQU8tODHPdkM0EXD4kk_7AFROk.; SUB=_2A25ybNMrDeRhGeFK41MX-C_Kwz2IHXVRrv1jrDV6PUJbktAKLWzgkW1NQvoovw6wWIPAoU16h7XRvBo9F42_6opO; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W55niMkMFKo4LbYyUnvGXdK5JpX5KzhUgL.FoMX1h2c1h2c1h22dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMNShnpSonpSonp; SUHB=0QS5MhRGGiya0F; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D100103type%253D1%2526q%253D%2523Netflix%25E6%258B%258D%25E5%2589%25A7%25E7%2589%2588%25E4%25B8%2589%25E4%25BD%2593%2523%26fid%3D100103type%253D1%2526q%253D%2523Netflix%25E6%258B%258D%25E5%2589%25A7%25E7%2589%2588%25E4%25B8%2589%25E4%25BD%2593%2523%26uicode%3D10000011'}
    data = []
    userlink = []
    for i in range(1,52):
        try:
            url = netflix_url+str(i)
            html = requests.get(url,headers =header,cookies = cookie)
            bs = BeautifulSoup(html.content,'html.parser')


            fullcontent = bs.find_all('p',{'class':'txt','node-type':'feed_list_content_full'})
            shortcontent =bs.find_all('p',{'class':'txt','node-type':'feed_list_content'})
            feed = bs.find_all('div',{'class':'card-wrap','action-type':'feed_list_item'})
            print(len(fullcontent))
            print(len(shortcontent))
            time.sleep(1)
            for item in shortcontent:
                try:
                    if re.findall('展开全文',item.text) ==[]:
                        name = item['nick-name']
                        short = item.text.replace(r'\n','').strip()
                        entry =[name,short]
                        data.append(entry)
                        print(entry)
                except KeyError:
                    print('a key error in short content.')
                    continue
            if len(fullcontent)> 0:
                for item in fullcontent:
                    try:
                        long = item.text.replace('收起全文d','').replace(r'\n','').strip()
                        entry = [item['nick-name'],long]
                        print(entry)
                        data.append(entry)
                    except KeyError:
                        print('a key error in long content.')
                        continue
            else:
                continue
            print('finish page %d' % i)
            time.sleep(2)
        except ValueError:
            print('one value is errored.')
            pass
        except KeyError:
            print('Somewhere has key error.')
            pass

    print(len(data))
    return data
def get_user_info(user,header,cookie):
    user = [user.string, user['href']]
    usersite = requests.get(user['href'], headers=header, cookies=cookie)
    bs2 = BeautifulSoup(usersite.content, 'html.parser')
    info = bs2.select('div>ul>li>span.item_text.W_fl')
    for information in info:
        print(user.string,"   ",information.strip())

if __name__ == '__main__':
    main()