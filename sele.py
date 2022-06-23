from selenium import webdriver
from selenium.webdriver.common.by import By
import sys
from selenium.webdriver.chrome.service import Service
from unidecode import unidecode

class Divar():
    def __init__(self):
        self.url="https://divar.ir/s/tehran/rent-residential"
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        s=Service('/home/hamed/project/learn/home_predict/chromedriver')
        self.driver1 =  webdriver.Chrome(service=s,options=op)
        self.driver1.get(self.url)
        self.driver2 =  webdriver.Chrome(service=s,options=op)
        self.run()


    def get_floor(self, row):
        floor_all = row.find_elements(By.XPATH,value=".//p[@class = 'kt-unexpandable-row__value']")[0].text
        floor= floor_all.split("از")[0]
        print(floor)
        if (floor == "همکف"):
            floor = 0
        elif (floor == "زیرهمکف"):
            floor = -1
        else :
            floor = int(unidecode(floor))
        return floor


    def get_vadie(self, row):
        vadie_all = row.find_elements(By.XPATH,value=".//p[@class = 'kt-unexpandable-row__value']")[0].text
        vadie= vadie_all.split(" ")[0]
        if vadie == "توافقی":
            vadie = -100
        else :
            vadie = int(unidecode(vadie).replace(",",""))
        return vadie


    def get_ejare(self, row):
        ejare_all = row.find_elements(By.XPATH,value=".//p[@class = 'kt-unexpandable-row__value']")[0].text
        ejare= ejare_all.split(" ")[0]
        if ejare == "توافقی":
            ejare = -100
        elif ejare == "مجانی":
            ejare = 0
        else :
            ejare = int(unidecode(ejare).replace(",",""))
        return ejare


    def get_one_home_info(self, url):
        ejare = -100
        vadie = -100
        floor = -100
        self.driver2.get(url)
        rows =  self.driver2.find_elements(By.XPATH,value="//div[@class = 'kt-base-row kt-base-row--large kt-unexpandable-row']")
        for row in rows:
            row_name = row.find_elements(By.XPATH,value=".//p[@class = 'kt-base-row__title kt-unexpandable-row__title']")[0].text
            if row_name == "طبقه":
                floor = self.get_floor(row)
            if row_name == "ودیعه":
                vadie = self.get_vadie(row)
            if row_name == "اجارهٔ ماهانه":
                ejare = self.get_ejare(row)
        print(f"vadie : {vadie}  , ejare : {ejare}  , floor : {floor}")

    def run(self):
        all_results =self.driver1.find_elements(By.XPATH,value="//section[@class = 'post-card-item kt-col-6 kt-col-xxl-4']")
        for result in all_results:
            href_class_1 = result.find_elements(By.XPATH,value="./a[@class = 'kt-post-card kt-post-card--outlined']")
            href_class_2 = result.find_elements(By.XPATH,value="./a[@class = 'kt-post-card kt-post-card--outlined kt-post-card--has-chat']")

            address = href_class_1 if href_class_1 != [] else href_class_2
            self.get_one_home_info(address[0].get_attribute('href'))
    

if __name__ == "__main__":
    Divar()