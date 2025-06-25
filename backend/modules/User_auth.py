import bcrypt
import jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
import mysql.connector

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
        