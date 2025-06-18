import requests
import pandas as pd


from nbformat import v4 as nbf
from nbclient import NotebookClient
from nbformat import write, read
import textwrap
import shutil


class Nutriscore:
    def __init__ (self):
        pass

    def get_openfoodfacts_raw_dataset(self):
        
        """
        Cette fonction télécharge le fichier CSV brut des produits Open Food Facts.
        Elle enregistre ensuite le fichier.
        Elle est optimiser pour éviter de saturer la mémoire car c'est un très gros dataset.
        """

        csv_url = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"
        response = requests.get(csv_url, stream=True)
        if response.status_code == 200:
            with open("../data/openfoodfacts_products.csv.gz", "wb") as file:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    file.write(chunk)
            print("Télechargement du fichier réussi.")
        else:
            print(f"Erreur lors du télechargement du fichier : {response.status_code}")





    def clean_openfoodfacts_raw_dataset_for_nutriscore(self):
        """
        Cette methode permet de nettoyer le gros dataset d'Open Food Facts
        pour ne garder que les colonnes utiles pour le calcul du Nutri-Score.
        Toutes les lignes possède un nutriscore valide.
        Elle crée un notebook Jupyter avec le code de nettoyage.
        Elle exécute le notebook dans un conteneur Docker et sauvegarde le fichier nettoyé dans un volume partagé.
        Elle copie le fichier nettoyé dans un dossier local.
        Elle est optimisée pour éviter de saturer la mémoire car c'est un très gros dataset.
        Elle utilise PySpark pour le traitement des données.
        Elle utilise nbformat pour créer et exécuter le notebook.
        Elle utilise nbclient pour exécuter le notebook.
        Elle utilise shutil pour copier les fichiers.
        Elle utilise textwrap pour formater le code du notebook.
        """
        # 1. Copier le fichier brut dans le volume Docker
        fichier_source = "../data/openfoodfacts_products.csv.gz"
        fichier_destination = "./notebooks/openfoodfacts_products.csv.gz"
        shutil.copyfile(fichier_source, fichier_destination)
        print("Fichier copié vers le volume partagé.")

        # 2. Créer un notebook avec du code PySpark
        notebook_path = "notebooks/nettoyage_auto.ipynb"
        nb = nbf.v4.new_notebook()

        code = textwrap.dedent("""
            import pyspark.pandas as ps

            # Lecture du dataset
            df = ps.read_csv("openfoodfacts_products.csv.gz", sep="\\t", mode="PERMISSIVE")

            # Nettoyage
            seuil = 95
            colonnes_vides = df.isna().sum() / len(df) * 100 > seuil
            df_sans_colonnes_vides = df.drop(columns=colonnes_vides[colonnes_vides].index.tolist())

            columns_to_drop = [
                'created_t', 'last_modified_t', 'labels_tags', 'brand_owner',
                'image_url', 'image_small_url', 'image_ingredients_url',
                'image_nutrition_url', 'states', 'states_en', 'states_tags'
            ]
            df_clean = df_sans_colonnes_vides.drop(columns=columns_to_drop, errors="ignore")

            # Filtrage sur les NutriScores valides
            df_clean = df_clean[df_clean['nutriscore_grade'].isin(['a','b','c','d','e'])]

            # Sauvegarde dans le volume partagé
            df_clean.to_csv("df_avec_nutriscore_clean.csv", index=False)
            print("Fichier nettoyé sauvegardé avec succès.")
        """)

        nb.cells.append(nbf.v4.new_code_cell(code))

        # Écrire le notebook dans le volume
        with open(notebook_path, "w") as f:
            nbf.write(nb, f)
        print("Notebook généré.")

        # 3. Exécuter le notebook dans le conteneur (via le volume)
        print("Exécution du notebook...")
        with open(notebook_path) as f:
            nb = nbf.read(f, as_version=4)

        client = NotebookClient(nb, timeout=600, kernel_name="python3")
        client.execute()

        with open(notebook_path, "w") as f:
            nbf.write(nb, f)
        print("Notebook exécuté avec succès.")

        # 4. Copier le CSV nettoyé depuis le volume vers un dossier local
        source_csv = "./notebooks/df_avec_nutriscore_clean.csv"
        destination_csv = "../data/df_avec_nutriscore_clean.csv"
        shutil.copyfile(source_csv, destination_csv)
        print("CSV final copié vers le dossier local.")
        
