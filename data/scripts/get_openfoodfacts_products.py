import requests
import polars as pl

csv_url = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"
response = requests.get(csv_url, stream=True)

if response.status_code == 200:
    with open("../openfoodfacts_products.csv.gz", "wb") as file:
        for chunk in response.iter_content(chunk_size=8000):
            file.write(chunk)
    print("Télechargement du fichier réussi.")
else:
    print(f"Erreur lors du télechargement du fichier : {response.status_code}")



df = pl.read_csv("../openfoodfacts_products.csv.gz", 
                 separator="\t", 
                 infer_schema_length=10_000, 
                 quote_char=None,  
                 ignore_errors=True)
df.write_parquet("../openfoodfacts_products.parquet", compression="gzip")
print("Conversion terminée !")