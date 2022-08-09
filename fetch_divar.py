import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from unidecode import unidecode
from utils.DataBaseClass import DBMongo
from tqdm import tqdm

class Divar():
    def __init__(self):
        self.url="https://divar.ir/s/tehran/rent-residential"
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        s=Service('utils/chromedriver')
        self.driver1 =  webdriver.Chrome(service=s,options=op)
        self.driver1.get(self.url)
        self.driver2 =  webdriver.Chrome(service=s,options=op)


        self.check_urls = list()
        self.init_db()


    def get_floor(self, row):
        floor_all = row.find_elements(By.XPATH,value=".//p[@class = 'kt-unexpandable-row__value']")[0].text
        floor= floor_all.split("از")[0].replace(" ", "")
        if (floor == "همکف"  ):
            floor = 0
        elif (floor == "زیرهمکف"):
            floor = -1
        else :
            floor = int(unidecode(floor))
        return floor

    def get_place(self):
        rows =  self.driver2.find_elements(By.XPATH,value="//div[@class = 'kt-page-title__subtitle kt-page-title__subtitle--responsive-sized']")
        text = rows[0].text
        sp = text.split('،')
        city = sp[0].split()[-1]
        region = sp[1].split("|")[0]
        return city, region


    def get_time(self):
        base_decrease_time = -1
        value_decrease_time = -1
        rows =  self.driver2.find_elements(By.XPATH,value="//div[@class = 'kt-page-title__subtitle kt-page-title__subtitle--responsive-sized']")
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



    def get_deposit(self, row):
        deposit_all = row.find_elements(By.XPATH,value=".//p[@class = 'kt-unexpandable-row__value']")[0].text
        deposit= deposit_all.split(" ")[0]
        if deposit == "توافقی":
            deposit = -100
        elif deposit == "مجانی":
            deposit = 0
        else :
            deposit = int(unidecode(deposit).replace(",",""))//1000000
        return deposit


    def get_rent(self, row):
        rent_all = row.find_elements(By.XPATH,value=".//p[@class = 'kt-unexpandable-row__value']")[0].text
        rent= rent_all.split(" ")[0]
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
        self.driver2.get(url)
        rows =  self.driver2.find_elements(By.XPATH,value="//div[@class = 'kt-base-row kt-base-row--large kt-unexpandable-row']")
        for row in rows:
            row_name = row.find_elements(By.XPATH,value=".//p[@class = 'kt-base-row__title kt-unexpandable-row__title']")[0].text
            if row_name == "طبقه":
                floor = self.get_floor(row)
            if row_name == "ودیعه":
                deposit = self.get_deposit(row)
            if row_name == "اجارهٔ ماهانه":
                rent = self.get_rent(row)
        city, region = self.get_place()
        time = self.get_time()
        column = self.driver2.find_elements(By.XPATH,value="//span[@class = 'kt-group-row-item__value']")
        property_col = self.driver2.find_elements(By.XPATH,value="//span[@class = 'kt-group-row-item__value kt-body kt-body--stable']")
        elavator = 0 if property_col[0].text == "آسانسور ندارد" else 1
        parking = 0 if property_col[1].text == "پارکینگ ندارد" else 1
        Warehouse = 0 if property_col[2].text == "انباری ندارد" else 1
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
        self.db = DBMongo()
    def run(self):
        self.driver1.refresh()
        all_results1 =self.driver1.find_elements(By.XPATH,value="//div[@class = 'post-card-item kt-col-6 kt-col-xxl-4']")
        all_results2 =self.driver1.find_elements(By.XPATH,value="//section[@class = 'post-card-item kt-col-6 kt-col-xxl-4']")
        all_results3 =self.driver1.find_elements(By.XPATH,value="//div[@class = 'waf972 wbee95 we9d46']")
        all_results = all_results1 if all_results1 != [] else all_results2 if all_results2 != [] else all_results3
        for i,result in tqdm(enumerate(all_results)):
            if all_results1 != []:
                href_class_1 = result.find_elements(By.XPATH,value="./a[@class = 'kt-post-card kt-post-card--outlined kt-post-card--padded kt-post-card--has-action']")
                href_class_2 = result.find_elements(By.XPATH,value="./a[@class = 'kt-post-card kt-post-card--outlined kt-post-card--padded kt-post-card--has-action kt-post-card--has-chat']")
                # href_class_1=all_results[i].find_elements(By.ID,value=all_results[i].id)
                href_class_3=result.find_elements(By.XPATH,value=".//a")
                address = href_class_1 if href_class_1 != [] else href_class_2
                address=address if address!=[] else href_class_3
                one_url = address[0].get_attribute('href')
            elif all_results2 != [] or all_results3 != []:
                address = result.find_elements(By.XPATH,value=".//a")
                one_url = address[0].get_attribute('href')
            if (not self.check_duplicate(one_url)):
                self.get_one_home_info(one_url)

                

if __name__ == "__main__":
    divar = Divar()
    while True:
        try:
            divar.run()
            time.sleep(60)
        except Exception as e:
            print(e)
            divar = Divar()
    

