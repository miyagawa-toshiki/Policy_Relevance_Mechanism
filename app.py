from flask import Flask, render_template, request
import pandas as pd
import base64
from io import BytesIO
from covid_func import news_scraper, news_df, important_word, data_cre,main, main2, extremum
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

def fig_to_base64(fig):
    # Bytes IO に対して、エンコード結果を書き込む。
    ofs = BytesIO()
    fig.savefig(ofs, format="png")
    png_data = ofs.getvalue()

    # バイト列を base64 文字列に変換する。
    base64_data = base64.b64encode(png_data).decode()

    return base64_data

@app.route("/",methods=['GET','POST'])
def index():
    if request.method == 'POST':
        print('データが送られました')
        d=pd.read_csv('owid-covid-data.csv')
        country=request.form.get('countries')
        countries=[]
        countries.append(country)
        #country=None
        print(countries)
        days=data_cre(d,countries)
        fig=main2(days,countries)
        img = fig_to_base64(fig)
        fig=None
        
        arr=extremum(countries)
        
        dates_url_arr=[]
        dates_title_arr=[]
        dates_diff=[]
        title_url_diclist=[]
        for i,dates in enumerate(arr):
            print(dates[0].day)
            url_list=news_scraper(country,dates[1].day,dates[1].month,dates[1].year,dates[0].day,dates[0].month,dates[0].year)
            df=news_df(url_list)
            dates_diff.append(dates)
            dates_url_arr.append(df['url'])
            dates_title_arr.append(df['title'])
            dic={}
            dic['title']=df['title']
            dic['url']=df['url']
            title_url_diclist.append(dic)
        #print(dic)
        #print(dates_diff)
        #rint(dates_title_arr)
        #print(dates_url_arr)
        return render_template('index.html',img=img, urls=zip(dates_diff,dates_title_arr,dates_url_arr))
    return render_template('index.html') 

@app.route("/Initialization", methods=['GET','POST'])
def ini():
    img=None
    return render_template('index.html',img=img)
    
    
@app.route("/extremum",methods=['GET','POST'])
def ex_search():
    d=pd.read_csv('owid-covid-data.csv')
    if request.method == 'POST':
        country=request.form.get('countries')
        extremum=request.form.get('extremum')
        extremum=int(extremum)
        countries=[]
        countries.append(country)
        days=data_cre(d,countries)
        fig=main2(days,countries,extremum)
        img1 = fig_to_base64(fig)
        
        return render_template('extremum.html',img1=img1)

    return render_template('extremum.html')
    
    