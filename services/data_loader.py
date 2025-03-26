import os
import ijson
import time
from collections import defaultdict
from flask import current_app
from services.exceptions import DataLoaderException
from utils.data_utils import extract_id, validate_numeric, log_data_summary




# base class for data load strategy
class DataLoadStrategy:
    # abstract method to load data
    def load(self, data_loader: 'DataLoader'):  
        # raises an error if method is not implemented in child class
        raise NotImplementedError  


# category data loading strategy
class CategoryLoadStrategy(DataLoadStrategy):
    # method to load category data
    def load(self, data_loader: 'DataLoader'):  
        # get the folder path from Flask config
        data_folder = current_app.config["DATA_FOLDER"]  
        # construct the full file path
        file_path = os.path.join(data_folder, "categories.json")  
        
        try:
            # open categories JSON file for reading
            with open(file_path, "r") as f:  
                # parse JSON items one by one
                for category in ijson.items(f, "item"):  
                    # process each category
                    self._process_category(category, data_loader)  
            current_app.logger.info(f"Loaded {len(data_loader.categories)} categories")  
        except Exception as e:  
            current_app.logger.error(f"Category load error: {str(e)}")  
            raise DataLoaderException(f"Category loading failed: {str(e)}", 500)  

    # process individual category data
    def _process_category(self, category, data_loader):  
        # get parent ID for the category
        parent_info = category.get("parent_id")  
        # set parent name if available
        parent_name = "No Parent" if isinstance(parent_info, bool) and parent_info else None  
        
        # add category data to the data loader
        data_loader.categories[category["id"]] = category  
        data_loader.category_index[category["id"]] = {
            'name': category["name"],
            'parent': parent_name
        }


# product data loading strategy
class ProductLoadStrategy(DataLoadStrategy):
    # method to load product data
    def load(self, data_loader: 'DataLoader'):  
        # get the folder path from Flask config
        data_folder = current_app.config["DATA_FOLDER"]  
        # construct the full file path
        file_path = os.path.join(data_folder, "products.json")  
        
        try:
            # open products JSON file for reading
            with open(file_path, "r") as f:  
                # parse JSON items one by one
                for product in ijson.items(f, "item"):  
                    # process each product
                    self._process_product(product, data_loader)  
            current_app.logger.info(f"Loaded {len(data_loader.products)} products")  
        except Exception as e:  
            current_app.logger.error(f"Product load error: {str(e)}")  
            raise DataLoaderException(f"Product loading failed: {str(e)}", 500)  

    # process individual product data
    def _process_product(self, product, data_loader):  
        # add product data to the data loader
        data_loader.products[product["id"]] = product  
        # get category info for the product
        categ_info = product.get("categ_id")  
        if isinstance(categ_info, list):  
            # map product to category
            data_loader.product_category_map[product["id"]] = {
                'id': categ_info[0] if len(categ_info) > 0 else None,
                'name': categ_info[1] if len(categ_info) > 1 else "Unnamed Category"
            }


# contact data loading strategy
class ContactLoadStrategy(DataLoadStrategy):
    # method to load contact data
    def load(self, data_loader: 'DataLoader'):  
        # get the folder path from Flask config
        data_folder = current_app.config["DATA_FOLDER"]  
        # construct the full file path
        file_path = os.path.join(data_folder, "contacts.json")  
        
        try:
            # open contacts JSON file for reading
            with open(file_path, "r") as f:  
                # parse JSON items one by one
                for contact in ijson.items(f, "item"):  
                    # process each contact
                    self._process_contact(contact, data_loader)  
            current_app.logger.info(f"Loaded {len(data_loader.contacts)} contacts")  
        except Exception as e:  
            current_app.logger.error(f"Contact load error: {str(e)}")  
            raise DataLoaderException(f"Contact loading failed: {str(e)}", 500)  

    # process individual contact data
    def _process_contact(self, contact, data_loader):  
        # get contact ID
        contact_id = contact["id"]  
        # add contact to data loader
        data_loader.contacts[contact_id] = contact  
        # get country info for the contact
        country_info = contact.get("country_id")  
        
        if isinstance(country_info, list) and len(country_info) > 1:  
            # extract country details
            country_name = country_info[1]  
            country_code = country_info[0]  
            
            # map contact to country
            data_loader.contact_country_map[contact_id] = {
                'code': country_code,
                'name': country_name
            }
            
            # check for any country code conflicts
            if country_name in data_loader.country_code_map:  
                if data_loader.country_code_map[country_name] != country_code:  
                    # log warning if there is a conflict
                    current_app.logger.warning(
                        f"Country code conflict for {country_name}: "
                        f"Existing {data_loader.country_code_map[country_name]} vs new {country_code}"
                    )
            else:
                # map country to code
                data_loader.country_code_map[country_name] = country_code


# sales data loading strategy
class SalesLoadStrategy(DataLoadStrategy):
    # method to load sales data
    def load(self, data_loader: 'DataLoader'):  
        # start the time tracking for performance
        start_time = time.time()  
        processed = 0  # counter for processed records
        # get the folder path from Flask config
        data_folder = current_app.config["DATA_FOLDER"]  
        # construct the full file path
        file_path = os.path.join(data_folder, "sale_order_lines.json")  
        
        try:
            # open sales JSON file for reading
            with open(file_path, "r") as f:  
                # parse JSON items one by one
                for sale in ijson.items(f, "item"):  
                    # process each sale if it meets the conditions
                    if self._process_sale(sale, data_loader):  
                        processed += 1  
            # log summary of the data loaded
            log_data_summary(data_loader)  
        except Exception as e:  
            current_app.logger.error(f"Sales processing failed: {str(e)}")  
            raise DataLoaderException(f"Sales processing error: {str(e)}", 500)  

    # process individual sale data
    def _process_sale(self, sale, data_loader):  
        # skip sales not created in 2024
        if not sale.get("create_date", "").startswith("2024"):  
            return False  

        # extract product and customer ID
        product_id = extract_id(sale.get("product_id"))  
        customer_id = extract_id(sale.get("order_partner_id"))  
        
        if not product_id:  
            return False  

        # validate quantity value
        quantity = validate_numeric(sale.get("product_uom_qty", 0))  
        # get country data for the customer
        country_data = data_loader.contact_country_map.get(customer_id, {})  
        country_name = country_data.get('name', 'Unknown')  
        
        # get category info for the product
        category = data_loader.product_category_map.get(product_id, {})  
        category_id = category.get('id')  

        if category_id:  
            # update sales data by category
            data_loader.category_sales[category_id] += quantity  
            data_loader.category_product_sales[category_id][product_id] += quantity  

        # update sales data by country
        data_loader.country_product_sales[country_name][product_id] += quantity  

        if customer_id:  
            # add product to the customer's list
            data_loader.client_products[customer_id].add(product_id)  

        return True


# main data loader class
class DataLoader:
    # initialize data loader
    def __init__(self):  
        # initialize dictionaries to store loaded data
        self.categories = {}  
        self.products = {}  
        self.contacts = {}  
        self.category_index = {}  
        self.product_category_map = {}  
        self.category_sales = defaultdict(float)  
        self.category_product_sales = defaultdict(lambda: defaultdict(float))  
        self.country_product_sales = defaultdict(lambda: defaultdict(float))  
        self.client_products = defaultdict(set)  
        self.contact_country_map = {}  
        self.country_code_map = {}  
        self.factory = DataLoadFactory()  # create a factory for loading strategies

    # method to load data based on data type
    def load_data(self, data_type: str):  
        # use the factory to get the appropriate loader and load data
        self.factory.get_loader(data_type).load(self)  

    # method to initialize all data
    def initialize_data(self):  
        # log the start of data initialization
        current_app.logger.info("Starting data initialization")  
        # load data for each type (categories, products, contacts, sales)
        for data_type in ["categories", "products", "contacts", "sales"]:  
            try:
                # load the data for the specified type
                self.load_data(data_type)  
            except DataLoaderException as e:  
                # log error if loading fails
                current_app.logger.error(f"Failed to load {data_type}: {str(e)}")  
                raise  
        # log data summary after loading all data
        log_data_summary(self)  


# factory class to get the appropriate loader strategy
class DataLoadFactory:
    # method to get the correct loader based on data type
    def get_loader(self, data_type: str) -> DataLoadStrategy:  
        loaders = {
            "categories": CategoryLoadStrategy(),  
            "products": ProductLoadStrategy(),  
            "contacts": ContactLoadStrategy(),  
            "sales": SalesLoadStrategy()  
        }  
        # return the loader for the specified data type
        return loaders.get(data_type, ValueError(f"Unknown data type: {data_type}"))  


# create an instance of the data loader
data_loader_instance = DataLoader()  