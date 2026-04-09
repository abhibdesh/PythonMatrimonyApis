import csv
from pymongo import MongoClient
import json
import os
import pandas as pd





mongoURI = os.getenv('MONGO_URL','')
databse = os.getenv('DATABSE',"")
client = MongoClient(mongoURI)
db = client.get_database(databse)

collection = db['DistrictMaster'] 

csv_file_path = 'districtList.csv'  

data = pd.read_csv(csv_file_path).dropna(how='all')  # Drop empty rows
print(data)
data_list = data.to_dict(orient='records')


result = collection.insert_many(data_list)

print(f"Inserted {len(result.inserted_ids)} records.")
