import time
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from utils.DataBaseClass import DBMongo
from tqdm import tqdm
import sys

class Divar_home():
    def __init__(self):
        self.url="https://divar.ir/s/tehran/rent-residential"
        self.init_db()
        self.check_urls = list()


    def get_floor(self, row_name):
        floor= row_name.replace("طبقه", "").split("از")[0].replace(" ", "")
        if (floor == "همکف"  ):
            floor = 0
        elif (floor == "زیرهمکف"):
            floor = -1
        else :
            floor = int(unidecode(floor))
        return floor

    def get_place(self):
        rows =  self.home_page_soup.find_all("div", class_ = 'kt-page-title__subtitle kt-page-title__subtitle--responsive-sized')
        text = rows[0].text
        sp = text.split('،')
        city = sp[0].split()[-1]
        region = sp[1].split("|")[0].strip()
        return city, region


    def get_time(self):
        base_decrease_time = -1
        value_decrease_time = -1
        rows =  self.home_page_soup.find_all("div", class_ = 'kt-page-title__subtitle kt-page-title__subtitle--responsive-sized')
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



    def get_deposit(self, row_name):
        deposit= row_name.replace("ودیعه", "").replace("تومان", "").replace(" ", "")
        if deposit == "توافقی":
            deposit = -100
        elif deposit == "مجانی":
            deposit = 0
        else :
            deposit = int(unidecode(deposit).replace(",",""))//1000000
        return deposit


    def get_rent(self, row_name):
        rent= row_name.replace("اجارهٔ ماهانه", "").replace("تومان", "").replace(" ", "")
        if rent == "توافقی":
            rent = -100
        elif rent == "مجانی":
            rent = 0
        else :
            rent = int(unidecode(rent).replace(",",""))/float(1000000)
        return rent

    def get_one_home_info(self, url):
        rent = -100
        deposit = -100
        floor = -100
        self.home_page = requests.get(url)
        if self.home_page.status_code != 200:
            print("Error to get home page")
            return
        self.home_page_soup = BeautifulSoup(self.home_page.content, "html.parser")
        rows =  self.home_page_soup.find_all("div",class_ = 'kt-base-row kt-base-row--large kt-unexpandable-row')
        for row in rows:
            row_name = row.text
            if "طبقه" in row_name:
                floor = self.get_floor(row_name)
            if  "ودیعه" in row_name  and "اجاره" not in row_name:
                deposit = self.get_deposit(row_name)
            if "اجارهٔ ماهانه" in row_name:
                rent = self.get_rent(row_name)
        city, region = self.get_place()
        time = self.get_time()
        column = self.home_page_soup.find_all("span",class_ = 'kt-group-row-item__value')
        property_col = self.home_page_soup.find_all("span",class_ = 'kt-group-row-item__value kt-body kt-body--stable')
        elavator,parking,Warehouse = -1,-1,-1
        for col in property_col:
            if "آسانسور" in col.text:
                elavator = 0 if col.text == "آسانسور ندارد" else 1
            if "پارکینگ" in col.text:
                parking = 0 if col.text == "پارکینگ ندارد" else 1
            if "انباری" in col.text:
                Warehouse = 0 if col.text == "انباری ندارد" else 1
        area = int(unidecode(column[0].text))
        age = int(unidecode(column[1].text.split()[-1]))
        if(column[2].text == "بدون اتاق"):
            rooms = 0
        else:
            rooms = int(unidecode(column[2].text))
        self.save_to_db({'deposit' :deposit, 'rent' : rent, 'floor': floor, 'area': area, 'age' : age, 'rooms' : rooms,'elavator': elavator,'parking': parking,'Warehouse': Warehouse, 'time': time, 'city' :city,  'region' : region, 'url' : url})
        

    def check_duplicate(self,url):
        if url in self.check_urls:
            return True
        self.check_urls.append(url)
        return(False)
    def save_to_db(self,dic):
        self.db.InsertItem(dic)
    def init_db(self):
        self.db = DBMongo("home")
    def run(self):
        base_page = requests.get(self.url)
        if base_page.status_code != 200:
            print("Error to get base page")
            sys.exit()
        base_page_soup = BeautifulSoup(base_page.content, "html.parser")

        all_results1 =base_page_soup.find_all("div",class_ = 'post-card-item kt-col-6 kt-col-xxl-4')
        all_results2 =base_page_soup.find_all("section",class_ = 'post-card-item kt-col-6 kt-col-xxl-4')
        all_results3 =base_page_soup.find_all("div",class_ = 'waf972 wbee95 we9d46')
        all_results = all_results1 if all_results1  else all_results2 if all_results2 else all_results3
        for result in tqdm(all_results):
            if all_results1:
                href_class_2 = result.find_all("a",class_ = 'kt-post-card kt-post-card--outlined kt-post-card--padded kt-post-card--has-action kt-post-card--has-chat')
                href_class_1 = result.find_all("a",class_ = 'kt-post-card kt-post-card--outlined kt-post-card--padded kt-post-card--has-action')
                # href_class_1=all_results[i].find_elements(By.ID,value=all_results[i].id)
                href_class_3=result.find_all("a")
                address = href_class_1 if href_class_1  else href_class_2 if href_class_2 else href_class_3
                one_url = 'https://divar.ir' + address[0]['href']
            elif all_results2 or all_results3 :
                one_url = 'https://divar.ir' + result.contents[0]['href']
            if (not self.check_duplicate(one_url)):
                self.get_one_home_info(one_url)

                

if __name__ == "__main__":
    divar = Divar_home()
    while True:
    #     try:
        divar.run()
        time.sleep(20)
        # except Exception as e:
        #     print(e)
        #     divar = Divar()
    

