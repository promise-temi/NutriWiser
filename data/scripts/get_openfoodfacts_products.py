import requests
import io
import gzip
import pandas as pd

def get_openfoodfacts_database():

    # Récupération de la base de données Open Food Facts au format csv mais compressée en zip
    print("Récupération du dataset de produits Open Food Facts...")
    url = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"
    response = requests.get(url, stream=True)

    # Vérification du statut de la requête
    if response.status_code == 200:
        with open("../openfoodfacts_products.csv.gz", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Téléchargement terminé avec succès.")
    else:
        print(f"Erreur : {response.status_code}")

get_openfoodfacts_database()