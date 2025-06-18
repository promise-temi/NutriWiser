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
        try:
            with open("modules/mysql_creation.sql", "r", encoding="utf-8") as f:
                sql = f.read()
            for statement in sql.split(';'):
                stmt = statement.strip()
                if stmt:
                    self.cursor.execute(stmt)
            self.conn.commit()
            print("✅ Tables créées avec succès.")
        except Exception as e:
            print("Erreur création DB :", e)

    def insert_distinct_classes(self):
        db = self.client["nutriwiser_db"]
        collection = db["additifs_scraped"]
        distinct_classes = collection.distinct("additive_classes")
        query = "INSERT IGNORE INTO classes (label) VALUES (%s)"
        for classe in distinct_classes:
            if classe:
                self.cursor.execute(query, (classe.lower().strip(),))
        self.conn.commit()

    def insert_additives_names(self):
        db = self.client["nutriwiser_db"]
        collection = db["additifs_scraped"]
        distinct_names = collection.distinct("danger")
        query = "INSERT IGNORE INTO toxicite (label) VALUES (%s)"
        for name in distinct_names:
            if name:
                self.cursor.execute(query, (name.lower().strip(),))
        self.conn.commit()

    def insert_all_additives_data(self):
        db = self.client["nutriwiser_db"]
        collection = db["additifs_scraped"]
        results = collection.find({})

        for doc in results:
            try:
                code = doc.get('additive_code')
                if not code:
                    continue

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
        pipeline = Mysql_Pipeline()
        pipeline.create_database()
        pipeline.insert_additives_names()
        pipeline.insert_distinct_classes()
        pipeline.insert_all_additives_data()
        pipeline.close()
