from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
import mysql.connector
from modules.Products_health_details import ProductHealthDetails
from modules.OFF_api import OpenFoodFactsAPI
from modules.Health_F import Health_Form
from modules.User_auth import User_Auth
from get_data import get_data

import requests
from fastapi import FastAPI , Request , HTTPException

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security = HTTPBearer()


client = MongoClient("mongodb://localhost:27017")
conn = mysql.connector.connect(
    host="localhost",
    user="nutriwiser",
    password="nutriwiser",
    database="nutriwiser_db"
)
cursor = conn.cursor()

app = FastAPI(
    title="NutriWiser API",
    description="API pour l'application NutriWiser, fournissant des informations nutritive et sanitaires sur les produits alimentaires.",
    version="1.0.0",
)

user_auth = User_Auth()

# @app.middleware("http")
# async def verify_token(request: Request, call_next):
#     if request.url.path in ["/login", "/docs", "/register", "/openapi.json", "/redoc" , "/"]:
#         return await call_next(request)
#     else:
#         # Vérification du token dans les paramètres de la requête
#         token = request.query_params.get("token")
        
#         if user_auth.verify_token(token):
#             return await call_next(request)
#         else:
#             raise HTTPException(status_code=403, detail="Accès interdit : token manquant ou invalide")
            
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not user_auth.verify_token(token):
        raise HTTPException(status_code=403, detail="Token invalide ou expiré")
    return user_auth.verify_token(token)
        
@app.get("/", description="Page d'accueil de l'API NutriWiser", tags=["Home"], response_model=dict)
def home():
    return {"message": "Bienvenue sur l'API NutriWiser. Rendez-vous sur la documentation pour découvrir les fonctionnalités disponibles."}


@app.get("/product_full_health_details", description="Prend en entrée le code QR d'un produit et renvoie des informations sur les additifs présents et les rappels sanitaire. Route protégée, nécessite un token d'authentification.", response_model= list, tags=["Product Health Details"])
def get_product_health_details(item_qr_code : str, user=Depends(get_current_user)):
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
            
    

    
    return [complete_product_info, recall_final_data]



@app.get("/register" , description="Enregistre un nouvel utilisateur avec un nom d'utilisateur et un mot de passe.", tags=["Registration"], response_model=dict)
async def regiter_user(username: str, password: str):
    username = username.lower().strip()
    password = password
    user_auth = User_Auth()
    if user_auth.create_user(username, password):
        return {"message": "utilisateur créé avec succès."}
    else:
        return {"message": "Échec de la création de l'utilisateur. Veuillez réessayer."}



@app.get("/login" , description="Connecte un utilisateur avec un nom d'utilisateur et un mot de passe. Renvoie un token d'authentification en cas de succès.", tags=["Authentication"], response_model=dict)
async def login_user(username: str, password: str):
    username = username.lower().strip()
    password = password
    user_auth = User_Auth()
    print("Attempting login for user:", username)
    if user_auth.verify_user(username, password):
        token = user_auth.create_token(username)
        return {"message": "User verified successfully.", "token": token}
    else:
        return {"message": "Invalid credentials."}


@app.get("/delete_user" , description="Supprime un utilisateur de la base de données avec un nom d'utilisateur et un mot de passe.", tags=["User Management"], response_model=dict)
async def delete_user(username: str, password: str, user=Depends(get_current_user)):
    username = username.lower().strip()
    password = password
    user_auth = User_Auth()
    if user_auth.delete_user(username, password):
        return {"message": "User deleted successfully."}
    else:
        return {"message": "Failed to delete user. Please check your credentials."}


