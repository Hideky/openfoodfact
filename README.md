# openfoodfact

# Data Collector
- fetch(path) - Retrieve data from the API in Json format
- get_categories() - Get all categories from the database in list of Categorie object
- update_categories() - Get all categories from the API using fetch() then update the database
- get_product(id) - Get a product data using fetch()
- get_categorie_products(categ_url, page_number) - Get page of 20 maximum product from a defined categorie in list of Product object

# Browsing
- categorie_manager() - Allows user to browse categorie available, find then select a categorie
- categorie_product_manager() - Allows user to browse product of a categorie available, find then select a product
- product_manager() - Allows user show a product