import csv
from pymongo import MongoClient
import json
import os


mongoURI = os.getenv('MONGO_URL','mongodb+srv://abhibdesh:k6fEWav4Dkc1rQzn@mat.podj9wc.mongodb.net/?retryWrites=true&w=majority&appName=Mat')
databse = os.getenv('DATABSE',"Matrimony")
client = MongoClient(mongoURI)
db = client.get_database(databse)

collection = db['CategoryMaster'] 

csv_file_path = 'districtList.csv'  

with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file) 
    data_list = list(csv_reader)  

result = collection.insert_many(data_list)

print(f"Inserted {len(result.inserted_ids)} records.")
