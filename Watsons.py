from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import os 
import time
from random import randint
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
    }

driver = webdriver.Chrome("chromedriver.exe")

promotion_type_list = ["2件88折","2件9折","2件享優惠","2件享折扣","3件享優惠","VIP點金價","不限金額結帳享85折","任選兩件享買一送一","任選買2送1","刷國泰卡滿$888現折$100","加贈寵i點數","售價再5折","售價再7折","售價再85折","售價再88折","售價再9折","售價再享折扣","寵i會員9折","寵i會員加贈3000點","寵i會員加贈6000點","寵i會員加贈9000點","寵i會員獨享價","專櫃指定品牌滿2000送$200","清貨3折","清貨7折","清貨8折","滿$888折$100","第2件3折","結帳再79折","結帳再9折","醫美滿$1500送$200","醫美滿$2800送$400","開架彩妝85折","點數狂飆10倍","點數狂飆6倍"]


df = pd.DataFrame()
df['品項'] = ""
df['促銷標籤'] = ""
df['售價']=""
df['折扣前金額'] = ""
df['主要促銷'] = ""
df.to_csv('promotion_type.csv',encoding ='utf_8_sig',index = False ,header=True)


for promotion_type in promotion_type_list:
    for page in range(0,370):
        try:
            time.sleep(randint(3,5))
            url = 'https://www.watsons.com.tw/%E5%85%A8%E9%83%A8%E5%95%86%E5%93%81/c/1?pageSize=64&currentPage='+str(page)+'&text=:bestSeller:category:1:allPromotions:' + promotion_type
            driver.get(url)
            time.sleep(randint(3,5))
            try:
                driver.find_element(By.LINK_TEXT, "我已滿十八歲").click()
            except:
                pass

            soup = BeautifulSoup(driver.page_source ,'html.parser')
            img_alt = []
            for img in soup.find_all('e2-product-thumbnail'):
                img = img.find('img',alt=True)
                img_alt.append(img['alt'].replace(" ",""))



            promotions = []
            for promotion in soup.find_all('div' ,class_ = 'productHighlight'):
                promotions.append(promotion.text.replace(" ",""))

            pre_prices = []
            for prices in soup.find_all('div' ,class_ = 'productPrice'):
                pre_prices.append(prices.text.replace(" ","").split("$")[1])


            discont = []
            for prices in soup.find_all('div' ,class_ = 'productPrice'):
                try:
                    discont.append(prices.text.replace(" ","").split("$")[2])  
                except:
                    discont.append(" ")





            if len(img_alt) <64:
                break
            
            df = pd.DataFrame({"品項":img_alt,
                                "促銷標籤":promotions,
                                "售價":pre_prices,
                                "折扣後金額":discont
                                })

            df['主要促銷'] = promotion_type
            df.to_csv('promotion_type.csv',encoding ='utf_8_sig',index = False ,mode = 'a+',header=False)
            print(url)
        except Exception as e:
            print(e)

