from modules.GetData import GetCsv


csv_url = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"
csv_filename = "../openfoodfacts_products.csv"
parket_filename = "../openfoodfacts_products.parquet"

products = GetCsv(csv_url, csv_filename, True, True, parket_filename)
products.get_csv_from_url()