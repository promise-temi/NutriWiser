from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from modules.get_main_data_pipelines.Produits_rappels_pipeline import RappelsPipeline

app = Flask(__name__)

def scheduled_rappel_update():
    print("Lancement de la mise à jour automatique des rappels")
    process = RappelsPipeline()
    process.get_rappels_data()

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_rappel_update, 'cron', hour=8, minute=0)  # tous les jours à 8h
scheduler.start()

@app.route('/')
def home():
    return "API NutriWiser est en ligne via http://localhost:5000"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

