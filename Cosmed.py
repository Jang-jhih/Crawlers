driver = webdriver.Chrome("chromedriver.exe")
driver.get("https://shop.cosmed.com.tw/v2/official/SalePageCategory/216486?sortMode=Sales")
driver.find_element(By.CSS_SELECTOR, ".fkeTIp").click()

js="var action=document.documentElement.scrollTop=10000"
driver.execute_script(js)
soup = BeautifulSoup(driver.page_source ,'html.parser')


items = []
for item in soup.find_all('div', class_ ='sc-fzXfOY jHoCXN'):
    items.append(item.text)
split_NT = []
for i in items:
    split_NT.append(i.split("NT"))
df = pd.DataFrame(split_NT ,columns=['品項','未折扣金額','折扣後金額'] )
df.to_csv('Cosmed.csv',index = False ,encoding='utf_8_sig')
