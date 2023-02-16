# -*- coding = utf-8 -*-
# @Time:2020/9/26 1:03 PM
# @Author: Zheng Zeng
# @File: nlp_analysis.py
# @Goal:
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
def main():
    '''
    data1 = pd.read_csv('Douban_Full.csv',header=0)
    data2 = pd.read_csv('Douban_Full2.csv',header = 0)
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
    img = Image.open('images.jpeg')
    img_array = np.array(img)
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

'''

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
def draw_wordcloud(wc,path):
    fig = plt.figure(1)
    plt.imshow(wc)
    plt.axis('off') # no axis is shown
    plt.show()
    plt.savefig(path,dpi = 500)
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
if __name__ == '__main__':
    main()