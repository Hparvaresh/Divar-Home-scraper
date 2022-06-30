from instabot import Bot
from PIL import Image

class insta():
    def __init__(self):
        
        self.bot = Bot()
        self.bot.login(username = "khane_rozane",
                password = "4717Hamed")
        self.send_post()
        self.logout()
    
    def send_post(self):
        self.bot.upload_photo("/home/hamed/project/learn/home_predict/resized.jpeg",
                caption = " دومین تست")
    def logout(self):
        self.bot.logout()
if __name__ == "__main__":
    insta_obj = insta()