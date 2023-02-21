# Sentiment Analysis of Readers of Three Body.

## Web Scrapping
Here is the web scrapping to obtain comments on Three Body novels from Douban website. We majorly use the acquireData() function to do the job, and then save the data on local.


```{python}
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
 ```
 
 ## NLP Analysis
 
 Here we did several things:
 1. settle down the packages to use
 ```{python}
 import jieba
import pandas as pd
import numpy as np
import nltk
from PIL import Image
from typing import List
import re
import wordcloud
from wordcloud import WordCloud
import matplotlib.pyplot as plt

```

2. write functions to clean the data : remove stopwords, special characters, combine words of the same stem or lemma.
```{python}
def remove_stopwords(text1,stopwords,dict):
    cuts = jieba.cut(text1.strip(),cut_all=True)
    print(cuts)
    outlist = []
    for word in cuts:
        word = combine_syn(word, syn_dict=dict)
        if word not in stopwords:
            if not remove_digits(word):
                continue
            if word !='\t':
                word = word.strip()
                outlist.append(word)
    fulltext = ' '.join(outlist)
    print(len(fulltext))
    return fulltext
def remove_digits(input_str):
    punc = u'0123456789.'
    output_str = re.sub(r'[{}]+'.format(punc), '', input_str)
    return output_str
def combine_syn(input_str,syn_dict):
    if input_str in syn_dict.keys():
        output_str = syn_dict[input_str]
    else:
        output_str = input_str
    return output_str
def grab_comment(data,column):
    comments = data[column]
    commentlist = []
    for comment in comments:
        comm = str(comment)
        commentlist.append(comm)
    text = ' '.join(commentlist)
    # print(text)
    return  text
```
3. Visualization using Word Cloud. 
 Run this main() function that will do all the work. Also define your own stopwords library here.
```{python}
def draw_wordcloud(wc,path):
    fig = plt.figure(1)
    plt.imshow(wc)
    plt.axis('off') # no axis is shown
    plt.show()
    plt.savefig(path,dpi = 500)
    
def main():
    data1 = pd.read_csv('your-data.csv',header=0)
    data2 = pd.read_csv('your-second-data.csv',header = 0)
    stopwords = ['。','，','！','？','吧','啊','吗','的','还是','没有','感觉','一个','这个',
                 '三体','额','噗','我','你','之','还','者','也','乎','',
                 '就是','什么','不是','可以','非常','一直']
    syn_dict3 = {'国人':'外国','美国人':'美国','中国人':'中国',
                 '权力':'权力的游戏','国外':'外国',
                 '系列剧':'系列','第一':'','外国人':'','作者':'原作者','科幻小说':'科幻'}
    # print(data1.head(10))
    # print(data2.tail(10))
    # print(data1.info)
    text1 = grab_comment(data1,'Comment')
    cleaned_t1 = remove_stopwords(text1,stopwords,syn_dict3)
    #choose an image for background.
    img = Image.open('images.jpeg')
    img_array = np.array(img)
    #initiate a word cloud object
    cloud1 =WordCloud(background_color='white',
                      mask=img_array,
                      font_path='Songti.ttc')
    cloud1.generate_from_text(cleaned_t1)
    draw_wordcloud(cloud1,'cloud1.jpeg')
    text2 = grab_comment(data2,'Comment')
    cleaned_t2 = remove_stopwords(text2)
    img2 = Image.open('images.jpeg')
    img2_array = np.array(img2)
    cloud2 = WordCloud(background_color='grey',
                       mask = img2_array,
                       font_path='Songti.ttc')
    cloud2.generate_from_text(cleaned_t2)
    draw_wordcloud(cloud2,'cloud2.jpeg')
    
    #the codes below works for weibo.

    '''
    data3 = pd.read_csv('weiboComment.csv',header = 0)
    # print(data3.head(10))
    text3 = grab_comment(data3,'Content')
    stopwords3 = ['。','，','！','？','吧','啊','吗','的','还是','没有','感觉','一个','这个',
                 '三体','额','噗','我','你','之','还','者','也','乎','',
                 '就是','什么','不是','可以','非常','一直','#','Netflix','电影','拍摄','netflix',
                  '但是','真的','David Benioff','Benioff','不要','如果',
                  '可能','虽然','作品','小三','评论','不会','不知','回应','这么',
                  '导演','呜呜','一部','已经','其实','电视剧','电视','看到','怎么',
                  '你们','不过','拍成','不能','知道',
                  '他们','自己','制作','布拉','小说','大家','觉得','编剧','出来','所以',
                  '毕竟','作为','​','游戏','三部曲','而且','拍剧']
    syn_dict3 = {'国人':'外国','美国人':'美国','中国人':'中国',
                 '权力':'权力的游戏','国外':'外国',
                 '系列剧':'系列','第一':'','外国人':'','作者':'原作者','科幻小说':'科幻'}
    cleaned_t3 = remove_stopwords(text3,stopwords3,syn_dict3)
    img3 = Image.open('images.jpeg')
    img3_array = np.array(img3)
    cloud3 = WordCloud(background_color='white',mask=img3_array,font_path='Songti.ttc')
    cloud3.generate_from_text(cleaned_t3)
    draw_wordcloud(cloud3,'cloud3.jpg')
    '''


if __name__ == '__main__':
    main()
```

### END
