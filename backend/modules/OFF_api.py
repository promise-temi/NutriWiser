import requests 

class OpenFoodFactsAPI:
    def __init__(self):
        pass
    def get_product_info_from_off_api(self, item_qr_code):
        # Récupération des informations du produit depuis l'API Open Food Facts
        response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{item_qr_code}.json")
        if response.status_code == 200:
            product_data = response.json()
        # aggrégation des informations du produit dans un dictionnaire
            product_info = {
                "nom": product_data.get("product", {}).get("product_name", "non disponible"),
                "marque": product_data.get("product", {}).get("brands", "Marque non trouvée"),
                "nutriscore": product_data.get("product", {}).get("nutriscore_grade", "Nutri-Score non trouvé"),
                "ingredients": product_data.get("product", {}).get("ingredients_text", "Ingrédients non trouvés"),
                "additifs": product_data.get("product", {}).get("additives_tags", []),
                "allergènes": product_data.get("product", {}).get("allergens", "Allergènes non trouvés"),
                "score_nova": product_data.get("product", {}).get("nova_group", "NOVA non trouvé"),
                "image_url": product_data.get("product", {}).get("image_url", "Image non trouvée"),
                "url": product_data.get("product", {}).get("url", "URL non trouvée"),
                # Macronutriments
                "sucres": product_data.get("product", {}).get("nutriments", {}).get("sugars_100g", "Non renseigné"),
                "glucides": product_data.get("product", {}).get("nutriments", {}).get("carbohydrates_100g", "Non renseigné"),
                "proteines": product_data.get("product", {}).get("nutriments", {}).get("proteins_100g", "Non renseigné"),
                "lipides": product_data.get("product", {}).get("nutriments", {}).get("fat_100g", "Non renseigné"),
                "gras_satures": product_data.get("product", {}).get("nutriments", {}).get("saturated-fat_100g", "Non renseigné"),
                "trans_fats": product_data.get("product", {}).get("nutriments", {}).get("trans-fat_100g", "Non renseigné"),
                "fibres": product_data.get("product", {}).get("nutriments", {}).get("fiber_100g", "Non renseigné"),
                "sodium": product_data.get("product", {}).get("nutriments", {}).get("sodium_100g", "Non renseigné"),
            }
        return product_info