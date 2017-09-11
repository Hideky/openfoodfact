# openfoodfact

# Data Collector
- fetch(path) - Retrieve data from the API in Json format
- fetch_m(path) - Retrieve data from the API
- get_categories() - Get all categories from the database in list of Categorie object
- update_categories() - Get all categories from the API using fetch() then update the database
- get_product(id) - Get a product data using fetch()
- get_categorie_products(categ_url, page_number) - Get page of 20 maximum product from a defined categorie in list of Product object
- get_substitutes(product) - Get all products with the categorie of the selected product then return a list of the healthier products
- get_db_product() - Return all products in the database

# Utils
- save_product(product) - Save this product in database

# Browsing
- categorie_manager() - Allows user to browse categorie available, find then select a categorie
- categorie_product_manager() - Allows user to browse product of a categorie available, find then select a product
- product_manager() - Allows user show a product
- substitute_manager() - Allows user to browse all healthier product of a selected product
- db_substitute_manager() - Allows user to browse all products save in database
- main_manager() - Allows user to browse all options available then select a menu