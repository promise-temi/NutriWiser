import requests
import mysql.connector
from pymongo import MongoClient
import re

class ProductHealthDetails:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="nutriwiser",
            password="nutriwiser",
            database="nutriwiser_db"
        )
        self.cursor = self.conn.cursor()
        self.client = MongoClient("mongodb://localhost:27017")

    
    def get_additives_details(self, additives):
        product_all_additives_info = []
        if not additives:
            return {"erreur": "Aucun additif trouvé pour ce produit."}
        for additive in additives:
            additive = additive.replace("en:", "").strip()
            print(f"Traitement de l'additif: {additive}")
            # Verification de la presence de l'additif dans la base de données, si non présent, on verifie mongoDB si il est present on ajoutes les données du document tels quelles sinon on passe à l'additif suivant en l'ignorant
            non_present_additive = self.verify_additive_exist_in_database(additive)
            product_all_additives_info.append(non_present_additive)
            if non_present_additive:
                continue

            cursor = self.cursor
            # Premiere requete pour reccuper les information de l'additif de la table principale
            query = "SELECT additifs.code, toxicite.label, additifs.description, additifs.description_avancee, additifs.remarques FROM additifs INNER JOIN toxicite on additifs.toxicite_id = toxicite.id WHERE additifs.code = %s"
            cursor.execute(query, (additive,))
            result1 = cursor.fetchone()

            #deuxieme reqquete pour reccuperer les information de l'additif de la table additive classes
            query = "SELECT classes.label FROM additifs_classes INNER JOIN classes on additifs_classes.class_id = classes.id WHERE additifs_classes.code_additif = %s"
            cursor.execute(query, (additive,))
            result2 = cursor.fetchall()

            #troisieme requette pour reccuperer les information de la table 
            query = "SELECT nom FROM additifs_noms WHERE additifs_noms.code_additif = %s" 
            cursor.execute(query, (additive,))
            result3 = cursor.fetchall()

            # Aggregation des resultat pour faire un objet complet sur l'additif
            complete_result = {
                "code" : result1[0],
                "toxicite_level": result1[1] if result1[1] else "Toxicité non renseignée",
                "categories": result2 if result2 else "Catégories non renseignées",
                "noms": result3 if result3 else "Noms alternatifs non renseignés",
                "description": result1[2] if result1[2] else "Aucune description disponible",
                "description_avancee": result1[3] if result1[3] else "Aucune description avancée disponible",
                "remarques": result1[4] if result1[4] else "Aucune remarque disponible"
            }

            product_all_additives_info.append(complete_result)

        return product_all_additives_info
            
    def verify_additive_exist_in_database(self, additive):
        #requete pour verifier que l'additif dans la base mySQL
        cursor = self.cursor
        query = "SELECT * FROM additifs WHERE code = %s"
        cursor.execute(query, (additive,))
        cursor.fetchone()
        if cursor.rowcount == 0:
            print(f"L'additif {additive} n'existe pas dans la base de données MySQL.")
            # Si l'additif n'existe pas dans la base de données MySQL, on le récupère depuis MongoDB
            try:
                additive_mongo = f'en:{additive}'
                filter={}
                project={
                    f'data.{additive_mongo}': 1
                }
            
                result = self.client['nutriwiser_db']['additifs'].find(
                filter=filter,
                projection=project
                )
        
                result = list(result)[0]['data'][additive_mongo]
                return result
            except Exception as e:
                print(f"L'additif {additive} n'existe pas dans la base de données MongoDB")
                return None

    def verify_product_is_recalled(self, brand):
        # Nettoyage pour la regex : enlever les articles comme "la", "le", etc.
        cleaned = re.sub(r"\b(la|le|l'|les|des|de|du|d')\b", "", brand, flags=re.IGNORECASE).strip()

        # Crée une regex insensible à la casse
        brand_regex = re.compile(cleaned, re.IGNORECASE)
        filter={'marque': brand_regex}
        project={
            'conseils': 1,
            'Preconisation_sanitaire': 1,
            'fiche_rappel_lien': 1,
            'marque': 1,
            '_id': 0
        }
   
        result = self.client['nutriwiser_db']['rappels_produits_alimentaires'].find(
        filter=filter,
        projection=project
        )
        result = list(result)
        return result



   