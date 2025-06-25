from pymongo import MongoClient
import mysql.connector

class Mysql_Pipeline:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017")
        self.conn = mysql.connector.connect(
            host="localhost",
            user="nutriwiser",
            password="nutriwiser",
            database="nutriwiser_db"
        )
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()
        self.client.close()

    def create_database(self):
        """
        Cette methode créé les tables nécessaires dans la base de données MySQL pour stocker les données des additifs alimentaires.
        Elle lit les instructions SQL depuis un fichier externe et les exécute pour créer les tables.
        """

        try:
            with open("modules/mysql_creation.sql", "r", encoding="utf-8") as f:
                sql = f.read()
            for statement in sql.split(';'):
                stmt = statement.strip()
                if stmt:
                    self.cursor.execute(stmt)
            self.conn.commit()
            print(" Tables créées avec succès.")
        except Exception as e:
            print("Erreur création DB :", e)

    def insert_distinct_classes(self):
        """
        Cette méthode insère les classes d'additifs distinctes dans la table 'classes'.
        Elle récupère les classes depuis la collection 'additifs_scraped' de MongoDB.
        """

        db = self.client["nutriwiser_db"]
        collection = db["additifs_scraped"]
        distinct_classes = collection.distinct("additive_classes")
        query = "INSERT IGNORE INTO classes (label) VALUES (%s)"
        for classe in distinct_classes:
            if classe:
                self.cursor.execute(query, (classe.lower().strip(),))
        self.conn.commit()

    def insert_additives_names(self):
        """
        Cette méthode insère les noms distincts des additifs dans la table 'toxicite'.
        Elle récupère les noms depuis la collection 'additifs_scraped' de MongoDB.
        """

        db = self.client["nutriwiser_db"]
        collection = db["additifs_scraped"]
        distinct_names = collection.distinct("danger")
        query = "INSERT IGNORE INTO toxicite (label) VALUES (%s)"
        for name in distinct_names:
            if name:
                self.cursor.execute(query, (name.lower().strip(),))
        self.conn.commit()

    def insert_all_additives_data(self):
        """
        Cette méthode insère toutes les données des additifs dans les tables MySQL.
        Elle récupère les données depuis la collection 'additifs_scraped' de MongoDB.
        Elle insère les additifs, leurs noms alternatifs, classes et toxicité dans les tables appropriées.
        """
        #Récupération des données depuis MongoDB
        db = self.client["nutriwiser_db"]
        collection = db["additifs_scraped"]
        results = collection.find({})

        # Pour chaque document, on insère les données dans MySQL
        for doc in results:
            try:
                code = doc.get('additive_code')
                if not code:
                    continue
                # Récupération des champs nécessaires
                names = doc.get('names') or []
                label_toxicite = (doc.get('danger') or '').strip()
                classes = doc.get('additive_classes', [])
                description = doc.get('description')
                description_avancee = doc.get('description_avancee')
                remarques = doc.get('remarques')

                # Toxicité
                self.cursor.execute("SELECT id FROM toxicite WHERE label = %s", (label_toxicite,))
                row = self.cursor.fetchone()
                if not row:
                    self.cursor.execute("INSERT INTO toxicite (label) VALUES (%s)", (label_toxicite,))
                    self.conn.commit()
                    toxicite_id = self.cursor.lastrowid
                else:
                    toxicite_id = row[0]

                # Additif principal
                self.cursor.execute("""
                    INSERT IGNORE INTO additifs (code, toxicite_id, description, description_avancee, remarques)
                    VALUES (%s, %s, %s, %s, %s)
                """, (code, toxicite_id, description, description_avancee, remarques))

                # Noms alternatifs
                for name in names:
                    self.cursor.execute("""
                        INSERT IGNORE INTO additifs_noms (code_additif, nom)
                        VALUES (%s, %s)
                    """, (code, name))

                # Classes
                for label in classes:
                    label = label.strip()
                    self.cursor.execute("SELECT id FROM classes WHERE label = %s", (label,))
                    row = self.cursor.fetchone()
                    # Si la classe n'existe pas, on l'insère
                    if not row:
                        self.cursor.execute("INSERT INTO classes (label) VALUES (%s)", (label,))
                        self.conn.commit()
                        class_id = self.cursor.lastrowid
                    else:
                        class_id = row[0]
                    self.cursor.execute("""
                        INSERT IGNORE INTO additifs_classes (code_additif, class_id)
                        VALUES (%s, %s)
                    """, (code, class_id))

                self.conn.commit()
                print(f"[OK] Additif inséré : {code}")

            except mysql.connector.Error as err:
                print(f"[ERREUR MySQL] sur {code} :", err)
                self.conn.rollback()


    def run_pipeline(self):
        # Exécution du pipeline complet
        pipeline = Mysql_Pipeline()
        pipeline.create_database()
        pipeline.insert_additives_names()
        pipeline.insert_distinct_classes()
        pipeline.insert_all_additives_data()
        pipeline.close()
