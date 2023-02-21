# -*- coding = utf-8 -*-
# @Time:2020/10/25 6:29 PM
# @Author: Zheng Zeng
# @File: tweeter_nlp.py
# @Goal:
import nltk
from nltk.tokenize import word_tokenize
import re
import pandas as pd
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
def main():

    tweets = pd.read_excel('/Users/zhengzeng/Desktop/Stanford RA/DataCrawling/tweeters.xls',sheet_name='Sheet1',header=0)
    print(tweets.head(5))
    tweeters  = tweets['tweets']
    syndict = {'Body':'Three-Body','sci fi':'science fiction','Problem':'Three-Body Problem',
               'Game':'Game-of-Thrones','Thrones':'Game-of-Thrones','Body Three':'Three-Body',
               'Three':'Three-Body','Xi':'Xi-Jinping','Jinping':'Xi-Jinping'}
    stopword = ['Netflix','said','.',',','?','!','and','the','then',
                 'they','by','on','in','at','is','a','as','an','to','can','not','ourselves','announced',
                'statement','it','has','will','year','well','one','right','film','made',
                'other','One','Trilogy','written','two','gonna','trilogy','us','finished',
                'think','everything','TODAY','now','generally','Three','Body','Problem','body','three',
                'problem','long','part','ve','got','Ooh','way','stuff','read','looking','almost',
                'late','thing','may','series','really']
    cleaned_tweet = []
    for tweet in tweeters:
        cleaned = clean_news(tweet)
        processed = news_processing(cleaned,stopwords=stopword,dict=syndict)
        cleaned_tweet.append(processed)
    print('total tweets:', len(cleaned_tweet))
    fulltext = '/'.join(cleaned_tweet)
    print(len(fulltext))
    draw_wc(fulltext)
    text2 = '/'.join(tweeters)
    draw_wc(text2)
def clean_news(news):
    pattern = re.compile(r'\n')
    cleaned = re.sub(pattern,'',news)
    return cleaned
# def news_nlp(text):
def draw_wc(text):
    img = Image.open('/Users/zhengzeng/Desktop/Stanford RA/News Data/WC_PIC.jpeg')
    img_array = np.array(img)
    cloud = WordCloud(background_color='white',mask=img_array,font_path='Comic Sans MS.ttf')
    cloud.generate_from_text(text)
    draw_wordcloud(cloud,'tweet_cloud.jpg')
    return cloud
def news_processing(text1,stopwords,dict):
    words = text1.split(' ')
    print(words)
    print(len(words))
    outlist = []
    for word in words:
        if word not in stopwords:
            if not remove_digits(word):
                continue
            if word !='\t':
                word = word.strip()
                word = combine_syn(word, syn_dict=dict)
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