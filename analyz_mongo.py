from torch import group_norm
from utils.DataBaseClass import DBMongo
import pandas as pd
import numpy as np
class Analyzor():
	def __init__(self):
		self.init_db()
		# column_names = ["_id", "deposit", "rent","floor","area","age","rooms","time","city","region","url"]
		# self.df = pd.DataFrame(columns = column_names)
		self.df = pd.DataFrame()
		self.fech_all_data()
		self.run()

	def init_db(self):
		self.db = DBMongo()

	def fech_all_data(self):
		data = self.db.FetchAllItem()
		for item in data:
			# print(type(item))
			self.df = self.df.append(item, ignore_index=True)
		# self.all_data= pd.DataFrame.from_dict(self.db.FetchAllItem(),  orient="index")
	def run(self):
		# self.df = self.df[self.df != -100]
		self.df = self.df.replace(-100,np.NaN)
		self.df = self.df.dropna()
		print(len(self.df))
		self.df["all_to_deposit"] = self.df.deposit + (self.df.rent//0.03) 
		self.df["deposit_per_area"] = self.df.all_to_deposit // self.df.area 
		self.df["region"] = self.df.region.apply(lambda x: x.strip())
		self.df.to_excel("output.xlsx")  


		group_df = self.df.groupby("region")
		# region_names = list()
		# print(group_df.count().index)
		# for row in group_df.count():
		# 	print(row)
			# region_names.append(row)
		# print(self.df[self.df.region == "سعادت‌آباد"])
		print(group_df.count().sort_values(by=['_id']))
		# print(region_names)
		
		# print(self.df.head())


if __name__ == "__main__":
	Analyzor()