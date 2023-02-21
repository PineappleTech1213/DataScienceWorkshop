# -*- coding = utf-8 -*-
# @Author: Chloe
# @File: Weibo.py
# @Goal: to scrape weibo posts related to a certain topic

import requests
import time
import pandas as pd
import re
import json
from json import decoder
import sys

def main():
    netflix_url = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D%23Netflix%E6%8B%8D%E5%89%A7%E7%89%88%E4%B8%89%E4%BD%93%23&page_type=searchall&page='
    weibo_crawling(netflix_url,'Weibo_Comments1.csv')
    #ncx_url = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D%23%E5%88%98%E6%85%88%E6%AC%A3%E8%B0%88%E7%BD%91%E9%A3%9E%E6%94%B9%E7%BC%96%E4%B8%89%E4%BD%93%23&page_type=searchall&page='
    #weibo_single_crawl(ncx_url,'Weibo_Comments2.csv')

def multi_replace(item,string):
    for k in item:
        clean_string = re.sub(k,'',string)
    return clean_string
def weibo_single_crawl(url,path):
    replaces = [u'\u200b', u'\u3000', r'\n']
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
    cookie = {
        'Cookie': 'YOUR_COOKIE'}
    try:
        html = requests.get(url, headers=header, cookies=cookie)
        jsonfile = html.json()
        for j in range(len(jsonfile['data']['cards'])):
            data = jsonfile['data']['cards'][j]
            if data['card_type'] == 9:
                if data['mblog']['isLongText'] == True:
                    weibo = [(data['mblog']['user']['screen_name'], data['mblog']['user']['gender'],
                              multi_replace(replaces, data['mblog']['longText']['longTextContent']),
                              data['mblog']['comments_count'],
                              data['mblog']['created_at'],
                              data['mblog']['reposts_count'], data['mblog']['user']['description'],
                              data['mblog']['user']['followers_count'])]
                    print( weibo)
                elif data['mblog']['isLongText'] == False:
                    weibo = [(data['mblog']['user']['screen_name'], data['mblog']['user']['gender'],
                              multi_replace(replaces, data['mblog']['raw_text']), data['mblog']['comments_count'],
                              data['mblog']['created_at'],
                              data['mblog']['reposts_count'], data['mblog']['user']['description'],
                              data['mblog']['user']['followers_count'])]
                    print(weibo)
                else:
                    continue
                entry = pd.DataFrame(weibo, columns=['UserName', 'Gender', 'Content',
                                                     'CommentCount', 'CreatedDate', 'RepostCount',
                                                     'UserDescription', 'FollowersCount'])
                if j == 1:
                    entry.to_csv(path, mode='a+', header=True, index=False)
                else:
                    entry.to_csv(path, mode='a+', header=False, index=False)
    except json.decoder.JSONDecodeError:
        print("Json decode error occurs for this page. Gonna stopped.")
        pass
    except:
        print(sys.exc_info())
    print('single crawling is done.')
def weibo_crawling(url,path):
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
    cookie = {
        'Cookie': 'T_WM=31239011660; WEIBOCN_FROM=1110006030; XSRF-TOKEN=fe3242; SSOLoginState=1600693115; ALF=1603285115; SCF=AlP_mTLbuiTgrGeZvPlyLDDKKbVdedTrgGSSWHsxXnj3KAQSSOZX_ewhfhpizHQU8tODHPdkM0EXD4kk_7AFROk.; SUB=_2A25ybNMrDeRhGeFK41MX-C_Kwz2IHXVRrv1jrDV6PUJbktAKLWzgkW1NQvoovw6wWIPAoU16h7XRvBo9F42_6opO; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W55niMkMFKo4LbYyUnvGXdK5JpX5KzhUgL.FoMX1h2c1h2c1h22dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMNShnpSonpSonp; SUHB=0QS5MhRGGiya0F; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D100103type%253D1%2526q%253D%2523Netflix%25E6%258B%258D%25E5%2589%25A7%25E7%2589%2588%25E4%25B8%2589%25E4%25BD%2593%2523%26fid%3D100103type%253D1%2526q%253D%2523Netflix%25E6%258B%258D%25E5%2589%25A7%25E7%2589%2588%25E4%25B8%2589%25E4%25BD%2593%2523%26uicode%3D10000011'}
    i = 1
    while i<6000:
        webpage = url + str(i)
        replaces = [u'\u200b',u'\u3000',r'\n']
        try:
            html = requests.get(webpage, headers=header, cookies=cookie)
            jsonfile = html.json()
            for j in range(len(jsonfile['data']['cards'])):
                data = jsonfile['data']['cards'][j]
                if data['card_type'] == 9:
                    if data['mblog']['isLongText'] ==True:
                        weibo=[(data['mblog']['user']['screen_name'],data['mblog']['user']['gender'],
                                multi_replace(replaces,data['mblog']['longText']['longTextContent']),
                                data['mblog']['comments_count'],
                                data['mblog']['created_at'],
                                data['mblog']['reposts_count'],data['mblog']['user']['description'],
                                data['mblog']['user']['followers_count'])]
                        print('page%d ,item  %d :' % (i, j), weibo)
                    elif data['mblog']['isLongText'] ==False:
                        weibo=[(data['mblog']['user']['screen_name'],data['mblog']['user']['gender'],
                                multi_replace(replaces,data['mblog']['raw_text']),data['mblog']['comments_count'],
                                data['mblog']['created_at'],
                                data['mblog']['reposts_count'],data['mblog']['user']['description'],
                                data['mblog']['user']['followers_count'])]
                        print('page%d ,item  %d:'% (i,j),weibo)
                    else:
                        continue
                    entry = pd.DataFrame(weibo, columns=['UserName', 'Gender', 'Content',
                                                         'CommentCount', 'CreatedDate', 'RepostCount',
                                                         'UserDescription', 'FollowersCount'])
                    if i ==1 and j ==1:
                        entry.to_csv(path, mode='a+',header=True,index=False)
                    else:
                        entry.to_csv(path,mode='a+',header=False,index=False)
        except json.decoder.JSONDecodeError:
            print("Json decode error occurs for this page. Gonna stopped.")
            break
        except :
            print(sys.exc_info())
        print('page %d has been scrapped.' % i)
        time.sleep(2)
        i +=1
        dataset= pd.read_csv('Weibo_Comments.csv',header = 1)
        print('Scrapping is finished. Data has %d rows' % len(dataset))

if  __name__ == '__main__':
    main()
