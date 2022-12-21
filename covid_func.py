import json
import re
import sys
import time
from urllib.parse import unquote
import chromedriver_binary
import pandas as pd
import requests
import unidecode
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from newspaper import Article
from newsplease import NewsPlease
from requests import get
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import Counter


import chromedriver_autoinstaller as chromedriver # 102errerデバック
chromedriver.install()
#url='https://www.google.com/search?q="Coronavirus"+site:https://www.reuters.com/'
#url='https://www.google.com/search?q="Coronavirus"+site:https://jp.reuters.com/'
#url='https://www.google.com/search?q="Coronavirus"+"Japan"+site:https://jp.reuters.com/'

def news_scraper(country,mindate,minmonth,minyear,maxdate,maxmonth,maxyear):
    # mindate=1
    # minmonth=1
    # minyear=2020
    # maxdate=1
    # maxmonth=1
    # maxyear=2021
    url='https://www.google.com/search?q="Covid-19"+"{}"+site:https://jp.reuters.com/&tbs=cdr%3A1%2Ccd_min%3A{}%2F{}%2F{}%2Ccd_max%3A{}%2F{}%2F{}'.format(country,mindate,minmonth,minyear,maxdate,maxmonth,maxyear)

    options = webdriver.ChromeOptions()
    #set_automation_as_head_less(options)
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    #set_ignore_certificate_error(options)
    options.add_argument('--incognito')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)

    url_list = []
        
    for i in range(10):
        try:
            links = driver.find_elements(By.XPATH,'//div[@class="yuRUbf"]/a')
            linky = [link.get_attribute('href') for link in links]
            url_list.extend(linky)
            driver.find_element(By.XPATH,'//*[@id="pnnext"]/span[2]').click()

        except NoSuchElementException:
            break
    driver.quit()
    return url_list

import pandas as pd
import nltk


#指定した日付だけnewspaper3kに通せば軽くなる。いやならないか
def news_df(url_list):
    keyword_list=[]
    title_list=[]
    date_list=[]
    summary_list=[]
    text_list=[]
    key='article'
    url_list =  [ s for s in url_list if key in s ]
    for i in range(len(url_list)):
        url=url_list[i]
        print(len(url_list))
        article = Article(url)
        article.download()
        article.parse()
        nltk.download('punkt')
        article.nlp()
        title_list.append(article.title)
        keyword_list.append(article.keywords)
        date_list.append(article.publish_date)
        summary_list.append(article.summary.replace('\n',''))
        text_list.append(article.text)
        
        
    df=pd.DataFrame(columns=['url','date','title','keyword','summary','text'])
    df['url']=url_list
    df['date']=date_list
    df['title']=title_list
    df['keyword']=keyword_list
    df['summary']=summary_list
    df['text']=text_list
    return df

def important_word(df):
    fullkeyword_list=[]
    for row in df.keyword:
        for i in range(len(row)):
            fullkeyword_list.append(row[i])     
    c = Counter(fullkeyword_list)
    print(c)

def data_cre(d,countries): #countriesは配列型、国を複数挿入可能
    
    d.fillna(0,inplace=True)
    lastday=str(d.date.iloc[-1:]).split()[1]
    print(lastday)
    n=200
    print('countries',n)
    #countries=['Japan']
    #for i in range(n):
    # countries.append(sys.argv[i+1])
    #print(countries)
    # countries=[]
    # countries.append(countrie)
    # print(countries)

    from datetime import date
    d0 = date(2020, 3, 3)
    d1 = date(int(lastday.split('-')[0]),int(lastday.split('-')[1]),int(lastday.split('-')[2]))
    delta = d1 - d0 
    days=delta.days

    dd=pd.DataFrame(
    {
    "country": countries,
    "population": range(len(countries)),
    })

    daysdate=sorted(d.date.unique())
    daysdate=daysdate[len(daysdate)-days:-1]
    #print(daysdate)
    for i in countries:
        dd.loc[dd.country==i,'population']=round(float(d.loc[(d.location==i),'population'][0:1]/1000000),2)
    print(dd)

    ddd=pd.DataFrame(
    {
    "date": daysdate,
    "deaths": range(len(daysdate)),
    "score": range(len(daysdate)),
    })
    
    for i in countries:
        print(i)
        if not os.path.isfile(i+'.csv'):
            for j in daysdate:
                if int(d.loc[(d.date==j) & (d.location==i),'total_deaths']):
                    ddd.loc[ddd.date==j,'deaths']=int(float(d.loc[(d.date==j) & (d.location==i),'total_deaths']))
            #print('int',int(d.loc[(d.date==j) & (d.location==i),'total_deaths'][0:1]))
            #print('round',int(d.loc[(d.date==j) & (d.location==i),'total_deaths'])/int(dd.loc[dd.country==i,'population']))
                ddd.loc[ddd.date==j,'score']=round(float(d.loc[(d.date==j) & (d.location==i),'total_deaths'])/int(dd.loc[dd.country==i,'population']),2)
            ddd.to_csv(i+'.csv',index=False)
    
    return days
    
    
def main(days,countries):
    for i in range(len(countries)):
        i=pd.read_csv(countries[i]+'.csv') 
        dy_score=np.gradient(i.score)
        plt.ylabel('Derivative')
        plt.plot(i.date,dy_score,label='differential')
        plt.xticks(np.arange(0,days,30*days/770),rotation=90)
        fig=plt.figure(1)
        fig.set_size_inches(10,3)
    plt.legend(countries)
    return fig

def main2(days,countries,order=6):
    print('test main2',countries)
    ax1=None
    ax2=None
    fig=None
    fig,ax1= plt.subplots() 
    fig.set_size_inches(10,3)
    ax2 = ax1.twinx()
    #ax3 = ax1.twinx()
    for i in range(len(countries)):
        df=pd.read_csv(countries[i]+'.csv')
        print(df)
        print('test'+countries[i])
        dy_score=np.gradient(df.score)
        n_conv=30
        b=np.ones(n_conv)/n_conv
        moving_average=np.convolve(dy_score,b,mode='same')
        ax1.plot(df.date,df.score)
        ax1.set_ylabel('score')
        ax2.plot(df.date,dy_score,label='differential', alpha=0.5)
        ax2.set_ylabel('differential')
        #ax3.plot(df.date,moving_average,alpha=0.1)
        arg_r_min,arg_r_max=argrelmin(moving_average,order=order),argrelmax(moving_average,order=order)
        for row in df.date[arg_r_max[0]]:
            plt.vlines(row, min(dy_score), max(dy_score), color='g', linestyles='dotted')
        for row in df.date[arg_r_min[0]]:
            plt.vlines(row, min(dy_score), max(dy_score), color='r', linestyles='dotted')
        fig.autofmt_xdate(rotation=45)
        plt.xticks(np.arange(0,days,30*days/770),rotation=90)
        fig=plt.figure(1)
        fig.set_size_inches(10,4)
    plt.legend(countries)
    df=None
    return fig

from scipy.signal import argrelmin, argrelmax
def extremum(countries,order=6): #orderの値によって極値が変わる
    arr=[]# 極小値と極大値の二次元配列を入れる
    for i in range(len(countries)):
        i=pd.read_csv(countries[i]+'.csv')
        dy_score=np.gradient(i.score)

        n_conv=30
        b=np.ones(n_conv)/n_conv
        moving_average=np.convolve(dy_score,b,mode='same')

        import datetime
        arg_r_min,arg_r_max=argrelmin(moving_average,order=order),argrelmax(moving_average,order=order)

        
        for mi in i.date[arg_r_min[0]]:
            arr1=[] #差を5値入れる。そこからマイナスで最大な値を取り出す
            dic={}
            mi = datetime.datetime.strptime(mi, '%Y-%m-%d')
            for ma in i.date[arg_r_max[0]]:
                ma = datetime.datetime.strptime(ma, '%Y-%m-%d')
                dt=mi-ma
                dic[dt.days]=ma
                arr1.append(dt.days)
                print(dt)
                print(arr1)
            minus_list=[x for x in arr1 if x > 0]
            
            arr.append([mi,dic[min(minus_list)]])
            
    return arr




    
    

    


