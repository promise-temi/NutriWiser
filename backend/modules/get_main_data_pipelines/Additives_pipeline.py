import requests 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json
from pymongo import MongoClient

class Additive_Pipeline:
    def __init__(self):
        self.mongo_client = MongoClient("mongodb://localhost:27017")
        self.db = self.mongo_client["nutriwiser_db"]

    def get_additives_main_data_scrapping_and_json(self):
        
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)  


        driver.get("https://www.additifs-alimentaires.net/additifs.php")

        time.sleep(10)  

        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")

        table = soup.select_one("table.tpi tbody")
        additives_list = []
        additionnal_additives_data = requests.get('https://static.openfoodfacts.org/data/taxonomies/additives.json')
        data_aditional = additionnal_additives_data.json()

        for row in table.find_all('tr'):
            additive_code_ = row.select_one('td.colCode').get_text(strip=True).lower()
            additive_additional_dict = data_aditional.get(f"en:{additive_code_}")
            try:
                additive_classes = additive_additional_dict.get('additives_classes').get('en').replace('en:', '').replace(' ', '').split(',')
            except AttributeError:
                    additive_classes = []
            additive_dict = {
                'additive_code': row.select_one('td.colCode').get_text(strip=True),
                'names': row.select_one('td.colNom').get_text(strip=True).split(', '),
                'danger': row.select_one('td.colDanger').get_text(strip=True),
                'additive_classes': additive_classes,
            }
            additives_list.append(additive_dict)
        # print(table.get_text(separator="\n", strip=True))
        print(len(additives_list))
        driver.quit()
        return additives_list

    def scrapping_additional_additives_data(self):
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        additives_list = self.get_additives_main_data_scrapping_and_json()
        print(len(additives_list))
        complete_additives_list = []
        for additive in additives_list:
            code = additive['additive_code']
            url = f"https://www.additifs-alimentaires.net/{code}.php#toxic"
            
            try: 
                driver.get(url)
                time.sleep(1)
                html = driver.page_source
                
                soup = BeautifulSoup(html, "html.parser")
                texts = soup.find_all("td", class_="colonne2")

                description = texts[0].get_text(strip=True)
                description_avancee = texts[2].get_text(strip=True)
                remarques = texts[4].get_text(strip=True)
                additive['description'] = description
                additive['description_avancee'] = description_avancee
                additive['remarques'] = remarques
                
                complete_additives_list.append(additive)
            except Exception as e:
                print(f"Erreur lors de la récupération de la page pour {code}: {e}")
                continue


                    

        driver.quit()
        return complete_additives_list

    def save_data_to_json(self):
        complete_additives_list = self.scrapping_additional_additives_data()

        # Sauvegarde du fichier principal enrichi
        with open('../data/additives_complet_data.json', 'w', encoding='utf-8') as file:
            json.dump(complete_additives_list, file, ensure_ascii=False, indent=4)

        print("✅ Fichier JSON principal sauvegardé.")

        # Sauvegarde brute des données additionnelles OpenFoodFacts
        response = requests.get('https://static.openfoodfacts.org/data/taxonomies/additives.json')
        with open('../data/additives_additional_data.json', 'wb') as file:
            file.write(response.content)

        print("✅ Fichier JSON additionnel sauvegardé.")

    def insert_additives_data_to_mongodb(self):
        self.save_data_to_json()

        # Insertion des données scrappées enrichies
        collection_scraped = self.db["additifs_scraped"]
        collection_scraped.delete_many({})

        with open("../data/additives_complet_data.json", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            collection_scraped.insert_many(data)
        else:
            collection_scraped.insert_one(data)

        print("✅ Données insérées dans MongoDB (additifs_scraped).")

        # Insertion des données OpenFoodFacts brutes
        collection_additional = self.db["additifs"]
        collection_additional.delete_many({})  # Optionnel, selon ton besoin

        with open("../data/additives_additional_data.json", encoding="utf-8") as f:
            data = json.load(f)

        collection_additional.insert_one({
            "source": "openfoodfacts",
            "data": data
        })

        print("✅ Données insérées dans MongoDB (additifs).")

    

    def close(self):
        self.mongo_client.close()
    
    def run_pipeline(self):
        self.insert_additives_data_to_mongodb()
        print("✅ Pipeline d'additifs exécuté avec succès.")
        self.close()