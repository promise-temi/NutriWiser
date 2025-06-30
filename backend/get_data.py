from modules.get_main_data_pipelines.Additives_pipeline import Additive_Pipeline
from modules.get_main_data_pipelines.Mysql_pipeline import Mysql_Pipeline
from modules.get_main_data_pipelines.Produits_rappels_pipeline import RappelsPipeline

# Pipleline pour la réccupération de plusieurs source, le traitement et le stockage des données d'additifs alimentaires dans mongoDB
# additives_data_process = Additive_Pipeline()
# additives_data_process.run_pipeline()

# Pipeline pour la création de la base de données MySQL et l'insertion des données d'additifs
mysql_insersion_additives_process = Mysql_Pipeline()
mysql_insersion_additives_process.run_pipeline()

# # Script pour réccuperer de l'api data.gouv les données des produits rappelés, faire le tri et les insérer dans MongoDB
# products_rappels_process = RappelsPipeline()
# products_rappels_process.get_rappels_data()