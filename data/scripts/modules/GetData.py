import requests
import gzip
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import polars as pl

class GetCsv:
    def __init__(self, url, filename, decompress=False, to_parket=False, parquet_name=None):
        self.url = url
        self.filename = filename
        self.decompress = decompress
        self.to_parquet = to_parket
        self.parquet_name = parquet_name

    def get_csv_from_url(self):

        
        print("Récupération du dataset...")
        url = self.url
        response = requests.get(url)
        

        if response.status_code == 200:
            print("Enregistrement du dataset...")
            contenu = response.content

            if self.decompress == True:
                # Décompression du contenu gzip avant enregistrement
                contenu_decompresse = gzip.decompress(contenu)
                with open(self.filename, "wb") as fichier_csv:
                    fichier_csv.write(contenu_decompresse)

            else:
                fichier_csv = open(self.filename, "wb")
                fichier_csv.write(contenu)
                fichier_csv.close()

            print("Dataset enregistré avec succès !")
        else:
            print(f"Une erreur s'est produite lors de la récupération du dataset. \nCODE :  {response.status_code}")
        

        if self.to_parquet == True:
            try:
                print("Conversion du fichier CSV en fichier Parquet...")

                df = pl.read_csv(self.filename, separator="\t", ignore_errors=True, infer_schema_length=10_000, quote_char=None)
                df.write_parquet(self.parquet_name, compression="gzip")

                print("Conversion terminée !")
            except Exception as e:
                print(f"Une erreur s'est produite lors de la conversion du fichier CSV en fichier parquet. \nERREUR : {e}")


# from pymongo import MongoClient
# class MongoDB:
#     def __init__(self):
#         pass

#     def get_mongo_urls(self):
#         client = MongoClient('mongodb://localhost:27017/')
#         filter={}
#         project={
#             '_id': False, 
#             'url': True
#         }
#         result = client['nutriwiser']['products'].find(
#         filter=filter,
#         projection=project
#         )