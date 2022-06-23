from selenium import webdriver
from selenium.webdriver.common.by import By
import sys
from selenium.webdriver.chrome.service import Service
from unidecode import unidecode

# driver=webdriver.Chrome('/home/hamed/project/learn/data_science/chromedriver')

url="https://divar.ir/s/tehran/rent-residential"

op = webdriver.ChromeOptions()
# op.add_argument('headless')


s=Service('/home/hamed/project/learn/data_science/chromedriver')
driver1 =  webdriver.Chrome(service=s,options=op)
driver2 =  webdriver.Chrome(service=s,options=op)
driver1.get(url)
floor = -100
all_results =driver1.find_elements(By.XPATH,value="//section[@class = 'post-card-item kt-col-6 kt-col-xxl-4']")
for result in all_results:
    href_class_1 = result.find_elements(By.XPATH,value="./a[@class = 'kt-post-card kt-post-card--outlined']")
    href_class_2 = result.find_elements(By.XPATH,value="./a[@class = 'kt-post-card kt-post-card--outlined kt-post-card--has-chat']")

    address = href_class_1 if href_class_1 != [] else href_class_2
    specific_result = driver2.get(address[0].get_attribute('href'))
    rows = driver2.find_elements(By.XPATH,value="//div[@class = 'kt-base-row kt-base-row--large kt-unexpandable-row']")
    for row in rows:
        row_name = row.find_elements(By.XPATH,value=".//p[@class = 'kt-base-row__title kt-unexpandable-row__title']")[0].text
        if row_name == "طبقه":
            floor_all = row.find_elements(By.XPATH,value=".//p[@class = 'kt-unexpandable-row__value']")[0].text
            floor= floor_all.split("از")[0]
            floor = int(unidecode(floor))
        if row_name == "ودیعه":
            vadie_all = row.find_elements(By.XPATH,value=".//p[@class = 'kt-unexpandable-row__value']")[0].text
            vadie= vadie_all.split(" ")[0]
            if vadie == "توافقی":
                vadie = -100
            else :
                vadie = int(unidecode(vadie).replace(",",""))
                print(vadie)
        # if row_name == "اجارهٔ ماهانه":
        #     floor_all = row.find_elements(By.XPATH,value=".//p[@class = 'kt-unexpandable-row__value']")[0].text
        #     floor= floor_all.split("از")[0]
    # print(len(floor))
    # if len(floor) == 5:
    #     input('w')
    # print(floor[-1].text)
