from bs4 import BeautifulSoup
import requests
class Web_scrap():
    def __init__(self,url):
        self.url =url

    def get_data(self):
        return requests.get(self.url)

    def bs_html(self,response):
        return BeautifulSoup(response.content, 'html.parser')




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Wb = Web_scrap('https://arzdigital.com/')
    response= Wb.get_data()
    bs= Wb.bs_html(response)
    fid_by_id = bs.find_all("a", attrs= {"class" : "arz-last-post arz-row"})
    for item in fid_by_id:
        print(item.get('href'))
