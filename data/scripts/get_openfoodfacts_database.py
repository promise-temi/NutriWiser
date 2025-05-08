import requests
import io
import gzip

def get_openfoodfacts_database():

    # Récupération de la base de données Open Food Facts au format JSONL mais compressée en zip
    url = "https://static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz"
    response = requests.get(url)

    # Sauvegarde du zip en mémoire
    response_en_memoire = io.BytesIO(response.content)

    # Décompression du zip avec gzip (reccuperation du contenu du zip)
    with gzip.open(response_en_memoire, "rt", encoding='utf-8') as fichier_decompresse:

        # Creation d'un fichier JSONL pour stocker le contenu décompressé
        with open("../openfoodfacts_database.jsonl", "w", encoding='utf-8') as file:
            
            # Pour chaque lige du fichier décompressé, réecriture dans le fichier JSONL
            for ligne in fichier_decompresse:
                file.write(ligne)