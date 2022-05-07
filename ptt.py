import requests
from bs4 import BeautifulSoup
import re 
import pandas as pd
import os
import gc
import time
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities




if not os.path.isdir('Datasource'):
    os.mkdir('Datasource')


def links_list(url):
    cookies = {'over18':'1'}
    req = requests.get(url,cookies=cookies).text
    soup = BeautifulSoup(req,'html.parser')

    links = []
    for i in soup.find_all('div' ,class_ = 'title'):
        try:
            links.append('https://www.ptt.cc'+i.find('a' ,href = True).get('href'))
        except:
            pass
    return links

def content_cralwer(links):
    cookies = {'over18':'1'}
    artical_list = []
    final_content_message = []

    for artical in links:
        try:
            # time.sleep(randint(1,3))
            

            req = requests.get(artical,cookies=cookies).text
            soup = BeautifulSoup(req,'html.parser')
            
            
            top_scope = soup.find_all('span' ,class_ = "article-meta-value")
            classfy = top_scope[2].text.split(']')[0].replace('[',"").replace('Re:',"").replace(' ',"")
            author = top_scope[0].text
            board = top_scope[1].text
            tital = top_scope[2].text
            date = top_scope[3].text
            artical_list.append([board,classfy,author,tital,date])
            print(tital)
            

            #爬取內文
            content =str(soup.find('div' ,id = 'main-container')).split('</span></div>\n')[1].split('※ 發信站')[0]
            #爬取留言
            message = soup.find('div' ,id = 'main-container').find_all('div' ,class_="push")
            content_message = message_content(message)
            final_content_message.append([content,content_message])
        except:
            pass

    df1 = pd.DataFrame(artical_list,columns=['版名','分類','作者','標題','日期'])
    df2 = pd.DataFrame(final_content_message,columns=['內容','留言'])
    df3 = pd.concat([df1,df2],axis = 1)

    return df3



def message_content(message):
    
    message_content = []
    for i in message:
        try:
            push_tag = i.find('span' ,class_=re.compile('hl push-tag')).text
            push_userid = i.find('span' ,class_=re.compile('f3 hl push-userid')).text
            push_content = i.find('span' ,class_=re.compile('f3 push-content')).text
            push_ipdatetime = i.find('span' ,class_=re.compile('push-ipdatetime')).text
            message_content.append([push_tag,push_userid,push_content,push_ipdatetime])
            
        except:
            pass
        
    attrs = ['type','user','content','ipdatetime']

    msgs = []
    for msg in message_content:
        msgs.append(dict(zip(attrs,list(msg))))

    return str(msgs) 

def new_page(table_name):
    driver = webdriver.Chrome("chromedriver.exe")
    driver.get("https://www.ptt.cc/ask/over18?from=%2Fbbs%2F"+table_name+"%2Findex.html")
    driver.find_element(By.NAME, "yes").click()
    driver.find_element(By.LINK_TEXT, "‹ 上頁").click()
    new_page = driver.current_url
    driver.quit()
    new_page=int(new_page.split('/')[5].replace('index','').replace('.html',''))
    return new_page
 

def crawler(table_name,page_quantity):
    start_page = new_page(table_name)
    end_page = start_page-page_quantity
    print('start_page : '+str(start_page))
    print('end_page : '+str(end_page))
    for i in range(start_page, end_page, -1):
        print(i)
        try:
            dfs = []
            url = 'https://www.ptt.cc/bbs/'+table_name+'/index'+str(i)+'.html'
            links = links_list(url)
            dfs.append(content_cralwer(links))
            dfs = pd.concat(dfs)
            add_to_pickle(table_name,dfs)  
        except:
            pass



def add_to_pickle(table_name,df):
    fname = os.path.join('Datasource',  table_name + '.pkl')
    newfname = os.path.join('Datasource',  'new' + table_name + '.pkl')
    
    if os.path.isfile(fname):
        
        old_df = pd.read_pickle(fname)
        gc.collect()
                
        old_df = old_df.append(df, sort=False)
        old_df = old_df.drop_duplicates()
        gc.collect()
        
        
        old_df.sort_index(inplace=True)
        gc.collect()
        
        old_df.to_pickle(newfname)
        os.remove(fname)
        os.rename(newfname, fname)
    else:
        df = df[~df.index.duplicated(keep='last')]
        df.to_pickle(fname)
        old_df = df

    del old_df
    gc.collect()