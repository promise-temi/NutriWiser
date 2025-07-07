# NutriWiser API

NutriWiser est une application qui fournit des informations nutritionnelles  et sanitaires sur les produits alimentaires.
Elle interagit avec l’API OpenFoodFacts, enrichit les données à l’aide de bases internes (MySQL et MongoDB), et expose une API REST sécurisée et documentée via Swagger.

## Fonctionnalités principales :

Recherche de produits alimentaires par code-barres (QR)

Vérification des additifs présents

Alertes sur les rappels sanitaires selon les marques

Authentification des utilisateurs avec token

Documentation interactive via Swagger UI

## Structure du projet :

main.py → Lance l’API FastAPI

get_data.py → Pipeline pour récupérer et stocker toutes les données (OpenFoodFacts, etc.)

refresh_data.py → (optionnel) serveur flask pour mettre a jours les données de rappels alimentaires automatiquement tout les jours


docker-compose.yml → Lance les bases MySQL + MongoDB + volumes

requirements.txt → Liste des dépendances Python

## Installation et Lancement :

### Cloner le projet :

git clone https://github.com/ton_repo/nutriwiser.git
cd nutriwiser

### Créer un environnement virtuel :

python -m venv venv
source venv/bin/activate
(Windows : venv\Scripts\activate)

### Installer les dépendances :

pip install -r requirements.txt

### Lancer les bases de données :

docker-compose up -d

### Récupérer les données (pipeline) :

python get_data.py

### Lancer l'API :

uvicorn main:app --reload

## Documentation API :

Swagger UI : http://localhost:8000/docs

ReDoc : http://localhost:8000/redoc

Authentification :

Certaines routes sont protégées par un token.

### Routes disponibles :

/register?username=...&password=...
→ Inscription d’un utilisateur

/login?username=...&password=...
→ Authentifie un utilisateur et retourne un token

### Exemple d’appel à une route protégée :

- Creer votre compte afin de pouvoir vous connecter. lors d'une connection réussie vous serez attribué un tocken. Entrez ce tocken dans l'onglet autorize du swagger fast api. Une fois connecter vous pourrez interroger les routes protégées pendant 1h.



