class Product:
    """OpenFoodFacts Categorie"""
    def __init__(self, id, name, brands, nutrition_grade, fat, saturated_fat, sugars, salt):
        self.id = id
        self.name = name
        self.brands = brands
        self.nutrition_grade = nutrition_grade
        self.fat = fat
        self.saturated_fat = saturated_fat
        self.sugars = sugars
        self.salt = salt
#data['products'][1]['nutriments']['saturated-fat_100g']