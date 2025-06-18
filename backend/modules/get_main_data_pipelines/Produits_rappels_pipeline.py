from pymongo import MongoClient
import requests

class RappelsPipeline:
    def __init__(self):
        pass
    def get_rappels_data(self):
        
        # URL de l’API RappelConso (données GTIN)
        URL = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/rappelconso-v2-gtin-espaces/exports/json"

        print("[+] Téléchargement des rappels...")
        response = requests.get(URL)
        if response.status_code != 200:
            print(f"[-] Erreur HTTP {response.status_code}")
        else: 
            data = response.json()
            print(f"[+] {len(data)} fiches récupérées")
            print(data[0:5], "\n...")  # Afficher les 5 premières fiches pour vérification

            rappels_produits_alimentaires_d_actualite = []
            for fiche in data:
                if fiche.get("categorie_produit") == "alimentation":
                    if fiche.get("date_de_fin_de_la_procedure_de_rappel") is None or fiche.get("date_de_fin_de_la_procedure_de_rappel") == "":
                        
                        rappels_produits_alimentaires_d_actualite.append(fiche)

            print(f"[+] {len(rappels_produits_alimentaires_d_actualite)} fiches alimentaires")
            print(rappels_produits_alimentaires_d_actualite[0:5]) 
            
            list_rappels_mongo = []
            for fiche in rappels_produits_alimentaires_d_actualite:
                fiche_rappel = {
                "nom" :  fiche.get("libelle"),
                "marque" :  fiche.get("marque_produit"),
                "motif_rappel"  : fiche.get("motif_rappel"),
                "conseils" : fiche.get("conduites_a_tenir_par_le_consommateur"),
                "images" : fiche.get("liens_vers_les_images"),
                "affichette_pdf" : fiche.get("lien_vers_affichette_pdf"),
                "fiche_rappel_lien" : fiche.get("lien_vers_la_fiche_rappel"),
                "Preconisation_sanitaire" : fiche.get("preconisations_sanitaires"),
                }

                list_rappels_mongo.append(fiche_rappel)

            
            client = MongoClient("mongodb://localhost:27017")
            db = client["nutriwiser_db"]
            collection = db["rappels_produits_alimentaires"]
            collection.insert_many(list_rappels_mongo)
            print(f"[+] {collection.count_documents({})} fiches insérées dans la base de données MongoDB")
            
