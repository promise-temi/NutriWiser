import bcrypt
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
import mysql.connector

SECRET_KEY = "ton_secret_ultra_sécurisé"
ALGORITHM = "HS256"

class User_Auth:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="nutriwiser",
            password="nutriwiser",
            database="nutriwiser_db"
        )
        self.cursor = self.conn.cursor()

    def create_user(this, username, password):
        """
        Cette méthode crée un nouvel utilisateur dans la base de données MySQL.
        Elle prend en paramètre le nom d'utilisateur et le mot de passe,
        hache le mot de passe avec bcrypt, et insère l'utilisateur dans la table 'utilisateurs'.
        Elle retourne True si l'utilisateur est créé avec succès, sinon False.
        """
        print("Creating user:", username)
        print("Password:", password)
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        print("Hashed Password:", hashed_pw)
        try:
            # Vérification de l'existence de l'utilisateur
            this.cursor.execute("SELECT username FROM utilisateurs WHERE username = %s", (username,))
            user = this.cursor.fetchone()
            # Si l'utilisateur existe déjà, on affiche un message d'erreur
            if user:
                print("User already exists.")
                return False
            # Si l'utilisateur n'existe pas, on insère le nouvel utilisateur dans la base de données
            this.cursor.execute("INSERT INTO utilisateurs (username, password_hash) VALUES (%s, %s)", (username, hashed_pw))
            this.conn.commit()
            print("User created successfully.")
        except mysql.connector.Error as err:
            print("Error creating user:", err)
        finally:
            this.cursor.close()
            this.conn.close()
        return True

    def verify_user(this, username, password):
        """
        Cette méthode vérifie si un utilisateur existe dans la base de données MySQL
        et si le mot de passe fourni correspond au mot de passe haché stocké.
        Elle prend en paramètre le nom d'utilisateur et le mot de passe.
        Elle retourne True si l'utilisateur est vérifié avec succès, sinon False.
        """

        print("Verifying user:", username)
        # vérification de l'existence de l'utilisateur
        this.cursor.execute("SELECT username FROM utilisateurs WHERE username = %s", (username,))
        user = this.cursor.fetchone()
        # si l'utilisateur n'existe pas, on affiche un message d'erreur
        if not user:
            print("User not found.")
            return False 
        # si l'utilisateur existe, on récupère le mot de passe haché associé à ce nom d'utilisateur
        this.cursor.execute("SELECT password_hash FROM utilisateurs WHERE username = %s", (username,))
        hashed_password = this.cursor.fetchone()
        hashed_password = hashed_password[0]
        # On vérifie si le mot de passe fourni correspond au mot de passe haché stocké dans la base de données
        if bcrypt.checkpw(password.encode(), hashed_password.encode()):
            print("User verified successfully.")
            return True
        else:
            print("User verification failed.")
            return False
        
    def delete_user(this, username, password):
        """
        Cette méthode supprime un utilisateur de la base de données MySQL.
        Elle prend en paramètre le nom d'utilisateur et le mot de passe.
        Elle vérifie d'abord si l'utilisateur existe, puis si le mot de passe correspond,
        et enfin supprime l'utilisateur de la table 'utilisateurs'.
        Elle retourne True si l'utilisateur est supprimé avec succès, sinon False.
        """
        try: 
            this.cursor.execute("SELECT username FROM utilisateurs WHERE username = %s", (username,))
            user = this.cursor.fetchone()
            if not user:
                print("User not found.")
                return False
            # Vérification du mot de passe
            this.cursor.execute("SELECT password_hash FROM utilisateurs WHERE username = %s", (username,))
            hashed_password = this.cursor.fetchone()
            hashed_password = hashed_password[0]    
            if not bcrypt.checkpw(password.encode(), hashed_password.encode()):
                print("Password does not match.")
                return False
            # Suppression de l'utilisateur
            this.cursor.execute("DELETE FROM utilisateurs WHERE username = %s", (username,))
            this.conn.commit()
            print("User deleted successfully.")
            return True
        except mysql.connector.Error as err:
            print("Error deleting user:", err)
            return False
    
    def create_token(self, username):
        """
        Cette méthode crée un token JWT pour l'utilisateur authentifié.
        Elle prend en paramètre le nom d'utilisateur et génère un token qui expire dans 1 heure.
        Elle retourne le token JWT.
        """
        payload = {
            "sub": username,  # subject = l'utilisateur
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)  # expire dans 1 heure
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    

    def verify_token(self, token):
        """
        Cette méthode vérifie la validité d'un token JWT.
        Elle prend en paramètre le token JWT et tente de le décoder.
        Si le token est valide, elle retourne True, sinon elle gère les exceptions
        pour les tokens expirés ou invalides et retourne False.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # Si tu veux, tu peux retourner aussi le payload
            return True
        except ExpiredSignatureError:
            print("Token expiré")
            return False
        except InvalidTokenError:
            print("Token invalide")
            return False