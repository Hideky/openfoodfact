import requests
import MySQLdb
import os
import Color
from Categorie import Categorie
from Product import Product

API_URL = "https://fr.openfoodfacts.org/"
db = MySQLdb.connect(user='root', passwd='root', host='127.0.0.1', db='openfoodfacts')
db.set_character_set('utf8')

def fetch(path):
	"""Get dynamically data from the REST API of OpenFoodFacts"""
	path = "%s%s.json" % (API_URL, path)
	response = requests.get(path)
	return response.json()

def get_categories():
	"""Get all categorie in the database"""
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SET NAMES utf8;')
	cursor.execute('SET CHARACTER SET utf8;')
	cursor.execute('SET character_set_connection=utf8;')
	cursor.execute("SELECT categories_id, id, name, products, url FROM categories")
	result = cursor.fetchall()
	cursor.close()
	categories = list()
	for element in result:
		categories.append(Categorie(element['categories_id'], element['name'], element['products'], element['url']))
	return categories

def update_categories():
	"""Download all categorie then update the database"""
	categories = fetch("categories")
	cursor = db.cursor()
	cursor.execute('SET NAMES utf8;')
	cursor.execute('SET CHARACTER SET utf8;')
	cursor.execute('SET character_set_connection=utf8;')
	cursor.execute('TRUNCATE categories')

	# clear result from useless data
	cleared_categories = list()
	for element in categories['tags']:
		if element['products'] < 10:
			continue
		if element['name'][:3] in ['en:', 'ru:', 'de:', 'es:']:
			continue
		cleared_categories.append(element)
	for element in cleared_categories:
		cursor.execute("""INSERT INTO categories(id, name, products, url) VALUES (%s, %s, %s, %s)""", 
			(element['id'], element['name'], element['products'], element['url']))
	cursor.close()
	db.commit()

def get_product(id):
	"""Get data of a product"""
	return fetch("api/v0/product/{}".format(id))

def get_categorie_products(url, page_number):
	"""Get data of all product of a categorie"""
	result = requests.get("{}/{}.json".format(url, page_number)).json()
	products = list()
	for element in result['products']:
		if not all(k in element for k in ("product_name","brands", "id", "nutrition_grade_fr")):
			continue
		if not all(k in element['nutriments'] for k in ("fat_100g","saturated-fat_100g", "sugars_100g", "salt_100g")):
			continue
		products.append(Product(element['id'], element['product_name'], element['brands'], element['nutrition_grade_fr'],
			element['nutriments']['fat_100g'], element['nutriments']['saturated-fat_100g'], 
			element['nutriments']['sugars_100g'], element['nutriments']['salt_100g']))
	return products

def categorie_product_manager(categorie_id):
	categorie_page = 1
	categorie_products = get_categorie_products(categories[categorie_id].url, categorie_page)
	while "User don't use 0 to exit":
		# Clear then show products
		os.system('cls' if os.name=='nt' else 'clear')
		print(Color.cyan("Categorie \"{}").format(Color.yellow(categories[categorie_id].name)) + Color.cyan("\" Page {}").format(categorie_page))
		for i in range(min(20,len(categorie_products))):
			print("{} - {} {}".format(Color.green(i+1), categorie_products[i].name, categorie_products[i].brands))
		uinput = input(Color.cyan("(Entrez: Un numéro pour selectionner un produit | S pour page suivante | P pour page précedente | 0 pour revenir au catégorie)\n"))

		# Exit catagorie product manager
		if uinput is '0':
			break

		# Select product
		if uinput.isdigit():
			product_manager(categorie_products[int(uinput)-1], categories[categorie_id].name)
			continue

		# Change page
		if uinput.isalpha():
			if uinput.lower() == 's':
				categorie_page += 1
			if uinput.lower() == 'p':
				categorie_page -= 1
			categorie_products = get_categorie_products(categories[categorie_id].url, categorie_page)

def product_manager(product, from_categorie):
	while "User don't use 0 to exit":
		# Clear then show product
		os.system('cls' if os.name=='nt' else 'clear')
		print("Nom du produit: {}".format(product.name))
		print("Marque: {}".format(product.brands))
		print("Nutri-score: {}".format(product.nutrition_grade))
		print("Repères nutritionnels pour 100g:")
		print("\tLipides: {}".format(product.fat))
		print("\tAcides gras saturés: {}".format(product.saturated_fat))
		print("\tSucres: {}".format(product.sugars))
		print("\tSel: {}".format(product.salt))

		uinput = input(Color.cyan("(Entrez: S pour trouver un produit de substitution | 0 pour revenir au produit de {}\n").format(from_categorie))

		# Exit product manager
		if uinput is '0':
			break

def categorie_manager():
	filter_categories = list()

	while "User don't use 0 to exit":
		# Clear then show catagorie
		os.system('cls' if os.name=='nt' else 'clear')
		if len(filter_categories):
			print(Color.cyan("Sélectionnez une catégorie (filté par \"{}\"):").format(uinput))
			for i in range(min(20,len(filter_categories))):
				print("{} - {} ({} produits)".format(Color.green(filter_categories[i].id), filter_categories[i].name, filter_categories[i].products))
		else:
			print(Color.cyan("Sélectionnez une catégorie:"))
			for i in range(min(20,len(categories))):
				print("{} - {} ({} produits)".format(Color.green(categories[i].id), categories[i].name, categories[i].products))

		# User input
		uinput = input(Color.cyan("(Entrez: Un numéro pour selectionner la catégorie | Une lettre pour filtrer | 0 pour fermer)\n"))

		# Exit		
		if uinput is '0':
			break
	
		# Select Categorie
		if uinput.isdigit():
			categorie_product_manager(int(uinput)-1)
			continue
	
		# Filter Categorie
		if uinput.isalpha():
			if len(uinput) == 1:
				filter_categories = [elem for elem in categories if elem.name[:1] == uinput[:1].upper()]
			else:
				filter_categories = [elem for elem in categories if uinput.lower() in elem.name.lower() ]
			continue

		# Reset Filter
		if not uinput:
			filter_categories.clear()
			continue

print("Bienvenue")

#update_categories()
categories = get_categories()

print("{} categories loaded".format(len(categories)))
categorie_manager()
	
# Nutrition_grade_fr

db.close()
print("Au revoir !")