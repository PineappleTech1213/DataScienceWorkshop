# -*- coding = utf-8 -*-
# @Time:2020/10/16 7:42 PM
# @Author: Zheng Zeng
# @File: news_nltk.py
# @Goal:
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
import nltk
from nltk.tokenize import word_tokenize
import re
import pandas as pd
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def main():
    nltk.download('punkt')
    with open("/Users/zhengzeng/Desktop/Stanford RA/News Data/news.txt",'r',encoding='latin-1') as f:
        doc = f.readlines()
    f.close()
    syndict = {'Body':'Three-Body','sci fi':'science fiction','Problem':'Three-Body Problem',
               'Game':'Game of Thrones','Thrones':'Game of Thrones','Body Three':'Three Body',
               'Three':'Three Body'}
    stopword = ['Netflix','said','.',',','?','!','and','the','then',
                 'they','by','on','in','at','is','a','as','an','to','can','not','ourselves','announced',
                'statement','it','has','will','year','well','one','right','film','made',
                'other']
    # print(doc)
    clean_doc = []
    for news in doc:
        cleaned_news = clean_news(news)
        if cleaned_news == '':
            pass
        else:
            cleaned_news = news_processing(cleaned_news,stopword,syndict)
            # print(cleaned)
            clean_doc.append(cleaned_news)
    text = '/'.join(clean_doc)
    cloud = draw_wc(text)
    draw_wordcloud(cloud,'newsWC.jpg')

def clean_news(news):
    pattern = re.compile(r'\n')
    k = 'Ó'
    p = 'Õ'
    q = 'Ò'
    cleaned = re.sub(pattern,'',news).replace(k,'\'').replace(p,'\'').replace(q,'')
    return cleaned
# def news_nlp(text):
def draw_wc(text):
    img = Image.open('/Users/zhengzeng/Desktop/Stanford RA/News Data/WC_PIC.jpeg')
    img_array = np.array(img)
    cloud = WordCloud(background_color='white',mask=img_array,font_path='Comic Sans MS.ttf')
    cloud.generate_from_text(text)
    draw_wordcloud(cloud,'newscloud.jpg')
    return cloud

# def wordcount(words):
#     dictionary = {}
#     for word in words:
#         if word in dictionary.keys():
#             dictionary[word] +=1
#         else:
#             dictionary[word] = 1
#     return dictionary
def news_processing(text1,stopwords,dict):
    words = text1.split(' ')
    #print(words)
    outlist = []
    for word in words:
        word = combine_syn(word, syn_dict=dict)
        if word not in stopwords:
            if not remove_digits(word):
                continue
            if word !='\t':
                word = word.strip()
                outlist.append(word)
    fulltext = '/'.join(outlist)
    return fulltext
def remove_digits(input_str):
    punc = u'0123456789.'
    output_str = re.sub(r'[{}]+'.format(punc), '', input_str)
    return output_str
def combine_syn(input_str,syn_dict):
    if input_str in syn_dict.keys():
        output_str = syn_dict.get(input_str)
    else:
        output_str = input_str
    return output_str
def draw_wordcloud(wc,path):
    fig = plt.figure(1)
    plt.imshow(wc)
    plt.axis('off') # no axis is shown
    plt.show()
    plt.savefig(path,dpi = 1000)
if __name__ == '__main__':
    main()