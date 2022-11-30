from os import PRIO_PGRP
import time
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from utils.DataBaseClass import DBMongo
from tqdm import tqdm
import sys

class Divar_car():
    def __init__(self):
        self.url="https://divar.ir/s/tehran/vehicles"
        self.init_db()
        self.check_urls = list()




    def get_place(self):
        rows =  self.car_page_soup.find_all("div", class_ = 'kt-page-title__subtitle kt-page-title__subtitle--responsive-sized')
        text = rows[0].text
        sp = text.split('،')
        city = sp[0].split()[-1]
        region = sp[1].split("|")[0].strip()
        return city, region


    def get_time(self):
        base_decrease_time = -1
        value_decrease_time = -1
        rows =  self.car_page_soup.find_all("div", class_ = 'kt-page-title__subtitle kt-page-title__subtitle--responsive-sized')
        text = rows[0].text
        sp = text.split('پیش')
        time_text = sp[0].split()
        if len(time_text) == 1:
            if time_text[0] == "دقایقی" or time_text[0] == "لحظاتی":
                base_decrease_time = 0
        else:
            if time_text[0] == "نیم":
                value_decrease_time = 0.5
            if time_text[0] == "یک" or time_text[0] == "۱":
                value_decrease_time = 1
            if time_text[0] == "۲":
                value_decrease_time = 2
            if time_text[0] == "۳":
                value_decrease_time = 3
            if time_text[0] == "۴":
                value_decrease_time = 4
            if time_text[0] == "۵":
                value_decrease_time = 5
            if time_text[0] == "۶":
                value_decrease_time = 6
            if time_text[1] == "ربع":
                base_decrease_time = 15*60
            if time_text[1] == "ساعت":
                base_decrease_time = 60*60
            if time_text[1] == "روز":
                base_decrease_time = 24*60*60
            if time_text[1] == "هفته":
                base_decrease_time = 7*24*60*60
        return time.time() - value_decrease_time*base_decrease_time

    def get_price(self, row_name):
        price= row_name.replace("قیمت", "").replace("تومان", "").replace(" ", "").replace("فروشنقدی","")
        if price in ['توافقی' , 'برای معاوضه', 'برایمعاوضه', 'غیرقابلنمایش']:
            price = -100
        else :
            price2 =    price.replace("٬","")
            price2 = int(unidecode(price2))/float(1000000)
        return price

    def get_one_car_info(self, url):
        price = -100
        production_year = -100
        distance = -100
        insurance_deadline = -100
        brand = ""
        engine = ""
        front_chassis =""
        back_chassis =""
        body =""
        gearbox = ""
        color = ""
        self.car_page = requests.get(url)
        if self.car_page.status_code != 200:
            print("Error to get car page")
            return
        self.car_page_soup = BeautifulSoup(self.car_page.content, "html.parser")
        type = self.car_page_soup.find_all("div",class_ = 'kt-page-title__subtitle kt-page-title__subtitle--responsive-sized')
        if type[0].text.split("|")[1].strip() != 'سواری و وانت':
            return
        rows =  self.car_page_soup.find_all("div",class_ = 'kt-base-row kt-base-row--large kt-unexpandable-row')
        for row in rows:
            row_name = row.text
            if "برند و تیپ" in row_name:
                brand = row_name.replace("برند و تیپ", "").strip()
            if "وضعیت موتور" in row_name:
                engine = row_name.replace("وضعیت موتور", "").strip()
            if "شاسی جلو" in row_name:
                front_chassis = row_name.replace("شاسی جلو", "").strip()
            if "شاسی عقب" in row_name:
                back_chassis = row_name.replace("شاسی عقب", "").strip()
            if "وضعیت شاسی‌ها" in row_name:
                front_chassis = back_chassis = row_name.replace("وضعیت شاسی‌ها", "").strip()
            if "وضعیت بدنه" in row_name:
                body = row_name.replace("وضعیت بدنه", "").strip()
            if  "مهلت بیمهٔ شخص ثالث" in row_name :
                insurance_deadline = int(unidecode(row_name.replace("مهلت بیمهٔ شخص ثالث", "").replace("ماه", "").strip()))
                
            if "گیربکس" in row_name:
                gearbox = row_name.replace("گیربکس", "").strip()
            if "قیمت" in row_name:
                price = self.get_price(row_name)
        city, region = self.get_place()
        time = self.get_time()
        column = self.car_page_soup.find_all("span",class_ = 'kt-group-row-item__value')
        for col in column:
            if "کارکرد" in col.previous:
                distance = int(unidecode(col.text.replace("٬","")))
            if "مدل (سال تولید)" in col.previous:
                production_year = int(unidecode(col.text.replace("قبل از", "").strip()))
            if "رنگ" in col.previous:
                color =col.text
       
        self.save_to_db({'brand' :brand , 'engine' : engine, 'front_chassis': front_chassis, 'back_chassis': back_chassis, 'body' : body, 'insurance_deadline' : insurance_deadline,'gearbox': gearbox,'price': price,'city': city, 'region': region, 'time' :time,  'distance' : distance, 'production_year' : production_year, 'color': color})
        

    def check_duplicate(self,url):
        if url in self.check_urls:
            return True
        self.check_urls.append(url)
        return(False)
    def save_to_db(self,dic):
        self.db.InsertItem(dic)
    def init_db(self):
        self.db = DBMongo("car")
    def run(self):
        base_page = requests.get(self.url)
        if base_page.status_code != 200:
            print("Error to get base page")
            sys.exit()
        base_page_soup = BeautifulSoup(base_page.content, "html.parser")

        all_results1 =base_page_soup.find_all("div",class_ = 'post-card-item kt-col-6 kt-col-xxl-4')
        all_results2 =base_page_soup.find_all("section",class_ = 'post-card-item kt-col-6 kt-col-xxl-4')
        all_results3 =base_page_soup.find_all("div",class_ = 'waf972 wbee95 we9d46')
        all_results4 =base_page_soup.find_all("div",class_ = 'post-card-item-_-af972 kt-col-6-_-bee95 kt-col-xxl-4-_-e9d46')
        all_results = all_results1 if all_results1  else all_results2 if all_results2 else all_results3 if all_results3 else all_results4
        for result in tqdm(all_results):
            if all_results1 or all_results4:
                href_class_2 = result.find_all("a",class_ = 'kt-post-card kt-post-card--outlined kt-post-card--padded kt-post-card--has-action kt-post-card--has-chat')
                href_class_1 = result.find_all("a",class_ = 'kt-post-card kt-post-card--outlined kt-post-card--padded kt-post-card--has-action')
                # href_class_1=all_results[i].find_elements(By.ID,value=all_results[i].id)
                href_class_3=result.find_all("a")
                address = href_class_1 if href_class_1  else href_class_2 if href_class_2 else href_class_3
                one_url = 'https://divar.ir' + address[0]['href']
            elif all_results2 or all_results3 :
                one_url = 'https://divar.ir' + result.contents[0]['href']
            if (not self.check_duplicate(one_url)):
                self.get_one_car_info(one_url)

                

if __name__ == "__main__":
    divar = Divar_car()
    while True:
        try:
            divar.run()
            time.sleep(20)
        except Exception as e:
            print(e)
    

