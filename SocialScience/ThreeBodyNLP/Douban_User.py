#to remove duplicates in scrapped data
#can also be used to join douban user data with the comments

import pandas as pd
import numpy as np
'''
data = pd.read_csv('Douban_Comments.csv',header = 0)
dat= pd.read_csv('Douban_user.csv',index_col=0,header=0)

douban = pd.merge(dat,data,left_on='User_link',right_on='User_link')
print(douban.info)
print(douban.describe())
douban.to_csv('Douban_Full.csv',header=True,index=False)
'''

douban1 = pd.read_csv('Douban_Full.csv',header = 0)
douban2 = pd.read_csv('Douban_Full2.csv',header= 0)
douban1 = douban1.drop_duplicates()
print(len(douban1))
douban1.to_csv('Douban_Full.csv',header = True,index=False)
print(len(douban2))
douban2.drop_duplicates().to_csv('Douban_Full2.csv',header=True,index=False)
print(len(douban2.drop_duplicates()))
