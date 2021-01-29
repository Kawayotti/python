# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 00:49:40 2019

@author: 川南慶喜
"""

import pandas as pd
import os
import numpy as np
import urllib.request,urllib.error #install require
from bs4 import BeautifulSoup #install require
from datetime import datetime
import csv
import time
import schedule #install require
from selenium import webdriver#install require
from selenium.webdriver.support.ui import WebDriverWait#install require
from selenium.webdriver.support import expected_conditions as EC#install require
from selenium.webdriver.common.by import By#install require
from operator import itemgetter


def job():#日経平均を毎日持ってくる

    
    
    f = open('nikkei_ave2.csv','a')
    writer =csv.writer(f,lineterminator='\n')
    
    #取る合図
    print("日時,終値を取得")
    csv_list=[]
    
    time_ = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    #時間を加える
    csv_list.append(time_)
    


    #アクセスするURL
    url = "http://www.nikkei.com/markets/kabu/"


    html = urllib.request.urlopen(url=url)


    soup = BeautifulSoup(html, "html.parser")

    span = soup.find_all("span")


    for tag in span:
        try:
            string_ = tag.get("class").pop(0)
        
            if string_ in "mkc-stock_prices":
                nikkei_heikin = tag.string
                break
        except:
            pass
    
    
    print (time_,nikkei_heikin)
    #日経平均を加える
    csv_list.append(nikkei_heikin)
    
    writer.writerow(csv_list)
    
    f.close()
    
    
#ここからCSVのダウンロード
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : "E:\Stock_Price"} #ダウンロードするディレクトリ
    chromeOptions.add_experimental_option("prefs",prefs)
    #Chrome diriverのパス
    chromedriver = "C:/Program Files (x86)/Chrome/chromedriver.exe" #クロームWEBドライバのディレクトリ
    extension_path = "C:/Program Files (x86)/Chrome/0.0.3_0.crx"
    chromeOptions.add_extension(extension_path)
    driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)
    
    
    
    #code = 1031
    for code in range(1301,9999): #株価コード
        url = 'https://kabuoji3.com/stock/' + str(code) + "/" + str(nen) + "/"
        driver.get(url)
        try:
            WebDriverWait(driver,4).until(EC.element_to_be_clickable((By.NAME,"csv")))
            driver.find_element_by_name('csv').click()
            WebDriverWait(driver,4).until(EC.element_to_be_clickable((By.NAME,"csv")))
            driver.find_element_by_name('csv').click()
            time.sleep(2)
            continue
        except:
            break
    driver.quit()


s1 = []
s2 = []

Fdir = "E:\Stock_price" #自分のパソコンのCSVのはいってるところ
os.chdir(Fdir)

ave = pd.read_csv("nikkei_ave.csv",header=0,usecols=[1])
mm = np.array(ave)
m = mm.flatten()#日経平均

dt_now= datetime.datetime.now()
nen = dt_now.year


c = 100000
Fdir = "E:\Stock_price" #自分のパソコンのCSVのはいってるところ
os.chdir(Fdir)
dfnp2 = np.array([])
stock = []


def keisan(s1,s2,m,c):
    def calcReturn(s_):#収益率の計算
        try:
            s0 = s_[:len(s_)-1]
            s1 = s_[1:len(s_)]
            output = (s1-s0)/s0
            return(output)
        except:
            pass
    
    
    def calcProb(r_):#確率測度の計算
        try:
            with np.errstate(invalid = 'ignore'):
                
                countUp = np.sum(calcReturn(r_)>0) #収益率が上昇した数
                probUp = countUp/len(r_) #収益率が上昇した割合
                return(np.array([probUp,1-probUp])) #上昇、下降確率を返す
        except:
            pass
    
    
    def calcEstReturn(s1_,m_):
            r1 = calcReturn(s1_)
            rm = calcReturn(m_)
            prob = calcProb(rm)
            mu = np.mean(r1)
            sigma = np.sqrt(np.var(r1,ddof=1))
            rm = np.array(rm[-len(r1):])
            XY = np.concatenate(([[r1,rm]]),axis =1)
            cor = np.corrcoef(XY)[0,1]
            re,rec = 0.0,0.0
            if(cor>0):
                re = mu + np.sqrt(prob[1]/prob[0])*sigma
                rec = mu - np.sqrt(prob[0]/prob[1])*sigma
            else:
                re = mu - np.sqrt(prob[1]/prob[0])*sigma
                rec = mu +np.sqrt(prob[0]/prob[1])*sigma
            return(np.array([re,rec]))
    
    
    
    
    
    def calcRNProb(r1_):
        qe = -r1_[1]/(r1_[0] - r1_[1])
        qec = r1_[0]/(r1_[0] - r1_[1])
        return(np.array([qe,qec]))
    
    
    
    
    def calcNAP(m_,s1_,s2_):
        est_r1 = calcEstReturn(s1_,m_) #s1の将来収益率
        est_r2 = calcEstReturn(s2_,m_) #s2の将来収益率
        RNProb = calcRNProb(est_r1)
        est_s2 = (1+est_r2)*s2_[0]
        nap = sum(RNProb*est_s2)
        return(nap)
        
    def calcAS(m_,c_,s1_,s2_):
        try:
            est_s1 = (1+est_r1)*s1_[0]
            est_s2 = (1+est_r2)*s2_[0]
            b = np.matrix([[s1[0],s2[0]],[est_s1[1],est_s2[1]]])
            gyaku = np.linalg.inv(b)
            theta1 = gyaku[0,0]*c+gyaku[0,1]*c
            theta2 = gyaku[1,0]*c+gyaku[1,1]*c
            if theta1 > 0 and theta2 > 0:#どっちもプラスのときに出力
                return(theta1,theta2,theta1*est_s1[0]+theta2*est_s2[0]>c)
            else:
                pass
        except:
            return(0,0,"none")
    
    
    
    print("ファイルのディレクトリを入力 E:\Stock_price")
    #Fdir = input()
    print("手持ちの現金を入力")
    #c = input()
    
    for code in range(1301,9997):
        s1 = []
        for year in range(2015,nen+1):
            try:
                Fname = str(code) + "_" + str(year) + ".csv"
                df = pd.read_csv(Fname,encoding = "shift_jis",skiprows = 1)
                dff = df["終値調整値"]
                df2 = pd.DataFrame(df,index = [len(dff)])
                dfnp = np.array(dff)
                s1 = np.append(s1,dfnp) #終値調整値が日付で降順にnumpy配列で入ってると思います多分
                if year != nen-1:
                    continue
                else:
                    for i in range(code+1,9998):
                        for toshi in range(2015,nen+1):
                            try:
                                Fname2 = str(i) + "_" + str(toshi) + ".csv"
                                data = pd.read_csv(Fname2,encoding = "shift_jis",skiprows = 1)
                                data2 = data["終値調整値"]
                                data3 = pd.DataFrame(df,index = [len(data2)])
                                data4 = np.array(data2)
                                s2 = np.append(s2,data4)
                                
                                r1 = calcReturn(s1)
                                r2 = calcReturn(s2)
                                rm = calcReturn(m)
                                
                                
                                est_r1 = calcEstReturn(s1,m)
                                est_r2 = calcEstReturn(s2,m)
                                pri = calcAS(m,c,s1,s2)
                                    
                                if toshi == nen and pri == None:
                                    s2 = []
                                elif toshi == nen:
                                    sep =(calcNAP(m,s1,s2) -s2[0])+(calcNAP(m,s2,s1) - s1[0])
                                    
                                    tot = (code,i,pri,sep)
                                    stock.append(tot)
                                    s2=[]
                                #s1は固定してs2をループで変えて行きｓ２が最後まで行ったら、s1を変えてまたループと言うふうに
                                #やっていくので、一つ計算が終わるときにコード名でリストを作って最後に比較できるようにすると良いかも
                                
                                else:
                                    continue
                                
                            except:
                                break
            except:
                break
    
    
    stock2 = sorted(stock,key = itemgetter(3),reverse = True)
    print(stock2)
    
schedule.every().day.at("23:00").do(keisan,s1='s1',s2='s2',m='m',c='c')
schedule.every().day.at("21:00").do(job)

while True:
 schedule.run_pending()
 time.sleep(30)

