class Health_Form:
    def __init__(self, sexe, age, weight, height, activity_level):
        self.sexe = sexe
        self.age = age
        self.weight = weight
        self.height = height
        self.activity_level = activity_level
        
        
        self.TDEE = {
            1:{
                "name": "sédentaire",
                "multiplier": 1.2,
                "description": "peu ou pas d'exercice"
            },
            2:{
                "name": "légèrement actif",
                "multiplier": 1.375,
                "description": "exercice léger/sport 1-3 jours/semaine"
            },
            3:{
                "name": "modérément actif",
                "multiplier": 1.55,
                "description": "exercice modéré/sport 3-5 jours/semaine"
            },
            4:{
                "name": "très actif",
                "multiplier": 1.725,
                "description": "exercice intense/sport 6-7 jours/semaine"
            },
            5:{
                "name": "extrêmement actif",
                "multiplier": 1.9,
                "description": "exercice très intense/sport 2x par jour"
            }
        }


    def calculate_bmi(self):
        if self.sexe == 0:
            BMR = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5

        elif self.sexe == 1:
            BMR = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161
        else:
            print("Erreur, sexe non reconnu")
        return BMR
    
    def calculate_daily_caloric_needs(self):
        multiplier = self.TDEE[self.activity_level]['multiplier']
        BMR = self.calculate_bmi()
        calories_needed = BMR * multiplier
        return calories_needed
    
    def calculate_BMI(self):
        height_m = self.height / 100
        bmi = self.weight / (height_m ** 2)

        if bmi < 16.5:
            category = "Dénutrition "

        elif bmi > 16.5 and bmi < 18.5:
            category = "maigreur"

        elif bmi > 18.5 and bmi < 25:
            category = "poids normal"

        elif bmi > 25 and bmi < 30:
            category = "surpoids"

        elif bmi > 30 and bmi < 35:
            category = "obésité modérée"

        elif bmi > 35 and bmi < 40:
            category = "obésité sévère"

        elif bmi > 40:
            category = "morbide ou massive"

        return [bmi, category]
    
    def  calculate_macronutrients(self):
        calories = self.calculate_daily_caloric_needs()
        macronutrients = {
            'sugar' : calories * 0.05 / 4,
            'glucides' : calories * 0.50 / 4,
            'proteines' : self.weight * 0.80,
            'lipides' : calories * 0.30 / 9,
            'gras_satures_max' : calories * 0.10 / 9,
            'trans_fats_max' : calories * 0.01 / 9,
            'fibres_min' : 25,
            'sodium_max' : 2 
        }
        return macronutrients