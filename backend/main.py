# from NutriWiser.backend.modules.get_main_data_pipelines.Additives_pipeline import Additive_Pipeline
# from NutriWiser.backend.modules.get_main_data_pipelines.Mysql_pipeline import Mysql_Pipeline
# from NutriWiser.backend.modules.get_main_data_pipelines.Produits_rappels_pipeline import RappelsPipeline

# # Pipleline pour la réccupération de plusieurs source, le traitement et le stockage des données d'additifs alimentaires dans mongoDB
# additives_data_process = Additive_Pipeline()
# additives_data_process.run_pipeline()

# # Pipeline pour la création de la base de données MySQL et l'insertion des données d'additifs
# mysql_insersion_additives_process = Mysql_Pipeline()
# mysql_insersion_additives_process.run_pipeline()

# # Script pour réccuperer de l'api data.gouv les données des produits rappelés, faire le tri et les insérer dans MongoDB
# products_rappels_process = RappelsPipeline()
# products_rappels_process.get_rappels_data()






from pymongo import MongoClient
import mysql.connector


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

@app.get("/product_health_details/{item_qr_code}")
def get_product_health_details(item_qr_code):
    response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{item_qr_code}.json")
    if response.status_code == 200:
        product_data = response.json()
        product_info = {
            "nom": product_data.get("product", {}).get("product_name", "non disponible"),
            "marque": product_data.get("product", {}).get("brands", "Marque non trouvée"),
            "nutriscore": product_data.get("product", {}).get("nutriscore_grade", "Nutri-Score non trouvé"),
            "ingredients": product_data.get("product", {}).get("ingredients_text", "Ingrédients non trouvés"),
            "additifs": product_data.get("product", {}).get("additives_tags", []),
            "allergènes": product_data.get("product", {}).get("allergens", "Allergènes non trouvés"),
            "score_nova": product_data.get("product", {}).get("nova_group", "NOVA non trouvé"),
        }
        def getadditives_infos(additives):
            product_all_additives_info = []
            for additive in additives:
                additive = additive.replace("en:", "").strip()
                query = "SELECT additif.code, toxicite.label,  FROM additifs INNER JOIN toxicite ON additifs.toxicite_id = toxicite.id WHERE additifs.code = %s"
                cursor.execute(query, (additive,))
                result = cursor.fetchone()

                product_all_additives_info.append(result)

            return product_all_additives_info
        return getadditives_infos(product_info["additifs"])

    else:
        return {"erreur": "Produit non trouvé essayé une autre methode..."}


