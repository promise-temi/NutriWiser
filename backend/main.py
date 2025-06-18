






from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
import mysql.connector
from modules.Products_health_details import ProductHealthDetails
from modules.OFF_api import OpenFoodFactsAPI
from modules.Health_F import Health_Form

import requests
from fastapi import FastAPI




app = FastAPI()




@app.get("/")
def read_root():
    return {"Hello": "World"}


client = MongoClient("mongodb://localhost:27017")
conn = mysql.connector.connect(
    host="localhost",
    user="nutriwiser",
    password="nutriwiser",
    database="nutriwiser_db"
)
cursor = conn.cursor()

@app.get("/product_additives_details/{item_qr_code}")
def get_product_health_details(item_qr_code):
    # Récupération des informations du produit à partir de l'API Open Food 
    
    Product_Health_date = ProductHealthDetails()
    OFFAPI = OpenFoodFactsAPI()

    product_info = OFFAPI.get_product_info_from_off_api(item_qr_code)
    # Enrichissement des informations du produit avec les détails des additifs graces au base de données MySQL
    complete_product_info = Product_Health_date.get_additives_details(product_info["additifs"])
    return complete_product_info

@app.get("/user_product_macronutrients/details/{item_qr_code}/{user_profile}")
def get_user_product_macronutrients_details(item_qr_code, user_profile):
    OFFAPI = OpenFoodFactsAPI()
    product_info = OFFAPI.get_product_info_from_off_api(item_qr_code)

    Product_Health_data = ProductHealthDetails()
    user_macronutrients = Product_Health_data.get_user_macronutrients_details(product_info)
    

