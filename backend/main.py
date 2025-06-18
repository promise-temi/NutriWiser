from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
import mysql.connector
from modules.Products_health_details import ProductHealthDetails
from modules.OFF_api import OpenFoodFactsAPI
from modules.Health_F import Health_Form

import requests
from fastapi import FastAPI , Request , HTTPException


client = MongoClient("mongodb://localhost:27017")
conn = mysql.connector.connect(
    host="localhost",
    user="nutriwiser",
    password="nutriwiser",
    database="nutriwiser_db"
)
cursor = conn.cursor()


app = FastAPI()

@app.middleware("http")
async def verify_token(request: Request, call_next):
    token = request.query_params.get("token")
    expected_token = "1234"

    if token != expected_token:
        raise HTTPException(status_code=403, detail="Accès interdit : token manquant ou invalide")
    return await call_next(request)



@app.get("/product_full_health_details")
def get_product_health_details(item_qr_code):
    # Récupération des informations du produit à partir de l'API Open Food 
    Product_Health_data = ProductHealthDetails()
    OFFAPI = OpenFoodFactsAPI()

    product_info = OFFAPI.get_product_info_from_off_api(item_qr_code)
    # Enrichissement des informations du produit avec les détails des additifs graces au base de données MySQL
    complete_product_info = Product_Health_data.get_additives_details(product_info["additifs"])

    recalls_collection = Product_Health_data.verify_product_is_recalled(product_info['marque'])
    if recalls_collection:
        recall_final_data =  {
            'message': 'attention des produits de cette marque sont rappelés vous pouver consulter les produits concernées en cliquant sur le lien des fiches de rappel',
            'recalls_data': recalls_collection
        } 
    else:
        recall_final_data = 'Aucun rappel de produit pour cette marque',
            
    

    
    return complete_product_info, recall_final_data



