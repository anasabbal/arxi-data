import os
import ijson
import time
from flask import current_app





# function to extract ID from a list field
def extract_id(id_field):  
    # docstring explaining the function's purpose
    """Extracts the ID from a field that may be a list."""  
    
    # check if the field is a list and has elements
    if isinstance(id_field, list) and len(id_field) > 0:  
        return id_field[0]  # return the first element if valid
    return None  # return None if not a valid list

# function to validate and convert a value to a non-negative float
def validate_numeric(value, default=0.0):  
    # docstring explaining the function's purpose
    """Validates and converts a numeric value, ensuring it's non-negative."""  
    
    try:
        # try converting the value to float and return the max with 0.0 to ensure non-negative
        return max(float(value), 0.0)  
    except (TypeError, ValueError):  
        # log a warning if value is not numeric or invalid
        current_app.logger.warning(f"Invalid numeric value encountered: {value}")  
        return default  # return the default value if invalid

# function to log a summary of the loaded data
def log_data_summary(data_loader):  
    # docstring explaining the function's purpose
    """Logs a summary of the loaded data."""  
    
    # create a summary string with the counts of categories, products, contacts, and sales
    summary = (  
        f"Data initialization completed\n"  
        f"- Categories: {len(data_loader.categories)}\n"  
        f"- Products: {len(data_loader.products)}\n"  
        f"- Contacts: {len(data_loader.contacts)}\n"  
        f"- Sales: {sum(len(v) for v in data_loader.country_product_sales.values())}"  
    )  
    
    # log the summary to the application logger
    current_app.logger.info(summary)  