import csv
from pymongo import MongoClient

import json


with open('./Config/Creds.json') as f:
    config = json.load(f)
    mongoURI = config['uri']
    databse = config['database']
client = MongoClient(mongoURI)
db = client.get_database(databse)

collection = db['CategoryMaster'] 

csv_file_path = 'districtList.csv'  

with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file) 
    data_list = list(csv_reader)  

result = collection.insert_many(data_list)

print(f"Inserted {len(result.inserted_ids)} records.")
