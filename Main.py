import requests
import webbrowser
import MySQLdb
import os
import Color
from Categorie import Categorie
from Product import Product

API_URL = "https://fr.openfoodfacts.org/"
db = MySQLdb.connect(user='root', passwd='root', host='127.0.0.1', db='openfoodfacts')
db.set_character_set('utf8')
categories = list()

def fetch(path):
	"""Get dynamically data from the REST API of OpenFoodFacts"""
	path = "%s%s.json" % (API_URL, path)
	response = requests.get(path)
	return response.json()

def fetch_m(path):
	"""Get dynamically data from the REST API of OpenFoodFacts"""
	path = "%s%s" % (API_URL, path)
	response = requests.get(path)
	return response.json()

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

def get_categorie_products(url, page_number):
	"""Get data of all product of a categorie"""
	result = requests.get("{}/{}.json".format(url, page_number)).json()
	products = list()
	for element in result['products']:
		if not all(k in element for k in ("product_name","brands", "id", "nutrition_grade_fr", "url", "categories_prev_tags")):
			continue
		if not all(k in element['nutriments'] for k in ("fat_100g","saturated-fat_100g", "sugars_100g", "salt_100g")):
			continue
		products.append(Product(element['id'], element['product_name'], element['brands'], element['nutrition_grade_fr'],
			element['nutriments']['fat_100g'], element['nutriments']['saturated-fat_100g'], 
			element['nutriments']['sugars_100g'], element['nutriments']['salt_100g'],
			element['url'], element['categories_prev_tags'][-1] ))
	return products

def get_product(id):
	"""Get data of a product"""
	return fetch("api/v0/product/{}".format(id))

def get_substitutes(product):
	"""Get healthier products from a selected product"""
	url = "cgi/search.pl?tagtype_0=categories&tag_contains_0=contains&tag_0={}&page_size=500&page=1&action=process&json=1"
	result = fetch_m(url.format(product.categorie))
	products = list()
	for element in result['products']:
		healthy_test = 0
		if not all(k in element for k in ("product_name","brands", "id", "nutrition_grade_fr", "url", "categories_prev_tags")):
			continue
		if not all(k in element['nutriments'] for k in ("fat_100g","saturated-fat_100g", "sugars_100g", "salt_100g")):
			continue
		if float(element['nutriments']['fat_100g']) < float(product.fat):
			healthy_test += 1
		if float(element['nutriments']['saturated-fat_100g']) < float(product.saturated_fat):
			healthy_test += 1
		if float(element['nutriments']['sugars_100g']) < float(product.sugars):
			healthy_test += 1
		if float(element['nutriments']['salt_100g']) < float(product.salt):
			healthy_test += 1
		if healthy_test < 3:
			continue
		products.append(Product(element['id'], element['product_name'], element['brands'], element['nutrition_grade_fr'],
			element['nutriments']['fat_100g'], element['nutriments']['saturated-fat_100g'], 
			element['nutriments']['sugars_100g'], element['nutriments']['salt_100g'],
			element['url'], element['categories_prev_tags'][-1] ))
	return products

def save_product(product):
	"""Save product in the database"""
	categories = fetch("categories")
	cursor = db.cursor()
	cursor.execute('SET NAMES utf8;')
	cursor.execute('SET CHARACTER SET utf8;')
	cursor.execute('SET character_set_connection=utf8;')

	cursor.execute("""INSERT INTO product VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
		(product.id, product.name, product.brands, product.nutrition_grade, product.fat, 
			product.saturated_fat, product.sugars, product.salt, product.url, product.categorie))
	cursor.close()
	db.commit()

def get_db_products():
	"""Get products from the database"""
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SET NAMES utf8;')
	cursor.execute('SET CHARACTER SET utf8;')
	cursor.execute('SET character_set_connection=utf8;')

	cursor.execute("SELECT * FROM product")
	result = cursor.fetchall()
	cursor.close()
	products = list()
	for element in result:
		products.append(Product(element['id'], element['name'], element['brands'], element['nutrition_grade'],
			element['fat'], element['saturated_fat'], 
			element['sugars'], element['salt'],
			element['url'], element['categorie']))
	return products

def categorie_manager():
	"""Show and interact with categorie"""
	global categories
	categories = get_categories()
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
		uinput = input(Color.cyan("(Entrez: Numéro - selectionner la catégorie | Lettre(s) - filtrer | 0 - revenir au menu principal)\n"))

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

def categorie_product_manager(categorie_id):
	"""Show and interact with categorie's product"""
	categorie_page = 1
	categorie_products = get_categorie_products(categories[categorie_id].url, categorie_page)
	while "User don't use 0 to exit":
		# Clear then show products
		os.system('cls' if os.name=='nt' else 'clear')
		print(Color.cyan("Categorie \"{}").format(Color.yellow(categories[categorie_id].name)) + Color.cyan("\" Page {}").format(categorie_page))
		for i in range(min(20,len(categorie_products))):
			print("{} - {} {}".format(Color.green(i+1), categorie_products[i].name, categorie_products[i].brands))
		uinput = input(Color.cyan("(Entrez: Numéro - selectionner un produit | S - page suivante | P - page précedente | 0 - revenir aux catégories)\n"))

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
	"""Show and interact with a product"""
	while "User don't use 0 to exit":
		# Clear then show product
		os.system('cls' if os.name=='nt' else 'clear')
		print(Color.cyan("\t<<< Fiche Produit >>>\n"))
		print(Color.yellow("Nom du produit: ") + product.name)
		print(Color.yellow("Marque: ") + product.brands)
		print(Color.yellow("Nutri-score: ") + product.nutrition_grade.upper())
		print(Color.green("Repères nutritionnels pour 100g:"))
		print(Color.yellow("\tLipides: ") + str(product.fat))
		print(Color.yellow("\tAcides gras saturés: ") + str(product.saturated_fat))
		print(Color.yellow("\tSucres: ") + str(product.sugars))
		print(Color.yellow("\tSel: ") + str(product.salt))
		print(Color.magenta("URL: ") + product.url)

		uinput = input(Color.cyan("(Entrez: S - Substituer | E - Enregistrer | N - Ouvrir | 0 - Revenir aux produits de {})\n").format(from_categorie))

		# Exit product manager
		if uinput is '0':
			break

		# Faire Save

		# Substitute this product
		if uinput.lower() == 's':
			substitute_manager(product)

		# Save this product in DB
		if uinput.lower() == 'e':
			save_product(product)

		# Open url in web browser
		if uinput.lower() == 'n':
			webbrowser.open(product.url, new=0, autoraise=True)

def substitute_manager(product):
	"""Show and interact with selected product's list"""
	substitutes = get_substitutes(product)

	while "User don't use 0 to exit":

		# Clear then show products
		os.system('cls' if os.name=='nt' else 'clear')
		print(Color.cyan("Substitue du produit \"{}").format(Color.yellow(product.name)) + Color.cyan("\""))
		for i in range(min(20,len(substitutes))):
			print("{} - {} {}".format(Color.green(i+1), substitutes[i].name, substitutes[i].brands))
		uinput = input(Color.cyan("(Entrez: Numéro - selectionner un produit | S - page suivante | P - page précedente | 0 - revenir au produit {})\n").format(product.name))

		# Exit substitute manager
		if uinput is '0':
			break

		# Select product
		if uinput.isdigit():
			product_manager(substitutes[int(uinput)-1], "Substitution de {}".format(product.name))
			continue

def db_substitute_manager():
	"""Show and interact with selected product's list"""
	products = get_db_products()
	while "User don't use 0 to exit":

		# Clear then show products
		os.system('cls' if os.name=='nt' else 'clear')
		print(Color.cyan("Produit enregistré:"))
		for i in range(min(20,len(products))):
			print("{} - {} {}".format(Color.green(i+1), products[i].name, products[i].brands))
		uinput = input(Color.cyan("(Entrez: Numéro - selectionner un produit | S - page suivante | P - page précedente | 0 - revenir au menu principal)\n"))

		# Exit substitute manager
		if uinput is '0':
			break

		# Select product
		if uinput.isdigit():
			product_manager(products[int(uinput)-1], "menu principal")
			continue

def main_manager():
	"""Show and start availables options"""
	while "User don't use 0 to exit":

		# Clear then show main application options
		os.system('cls' if os.name=='nt' else 'clear')
		print(Color.cyan("\t<<< Menu Principal >>>"))
		print("{} - {}".format(Color.green("1"), "Trouver un produit (Catégorie > Produit)"))
		print("{} - {}".format(Color.green("2"), "Afficher les produits substitué"))
		uinput = input(Color.cyan("(Entrez: Un numéro pour choisir un menu | 0 pour quitter)\n"))

		# Exit substitute manager
		if uinput is '0':
			break

		# Open categorie manager
		if uinput is '1':
			categorie_manager()
			continue

		# Open db substitute manager
		if uinput is '2':
			db_substitute_manager()
			continue

#update_categories()

main_manager()

db.close()
print("Au revoir !")