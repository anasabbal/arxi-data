from flask import Blueprint, jsonify, current_app
from services.data_loader import data_loader_instance
from services.exceptions import DataLoaderException
from flask_caching import Cache
from config import Config



# create blueprint for the api
api_bp = Blueprint("api", __name__)

# initialize cache
cache = Cache()

# configure cache settings
@api_bp.record_once
def configure_cache(state):
    """
    Initializes the cache with specific settings when the app is first recorded.
    Sets the cache type to SimpleCache and the default timeout to 300 seconds.
    """
    cache.init_app(state.app, config={
        'CACHE_TYPE': Config.CACHE_TYPE,
        'CACHE_DEFAULT_TIMEOUT': Config.CACHE_DEFAULT_TIMEOUT
    })

# validate if essential data is loaded
def validate_data_loaded():
    """
    Validates if the essential data structures are initialized.
    Raises a DataLoaderException if sales data is not loaded.
    """
    if not data_loader_instance.category_sales:
        raise DataLoaderException("Sales data not loaded", status_code=503)

# endpoint to get most sold products by category
@api_bp.route('/most_sold_by_category', methods=['GET'])
@cache.cached(query_string=True)
def get_most_sold_by_category():
    """
    Get top-selling products by category.
    ---
    responses:
      200:
        description: List of categories with top products.
      503:
        description: Data not loaded or unavailable.
    """
    try:
        # validate if data is loaded
        validate_data_loaded()
        
        results = []
        
        # iterate through categories and their corresponding products
        for cat_id, products in data_loader_instance.category_product_sales.items():
            if not products:
                continue
            
            # find the top-selling product in each category
            top_product_id, quantity = max(products.items(), key=lambda x: x[1])
            product_info = data_loader_instance.products.get(top_product_id, {})
            category_info = data_loader_instance.category_index.get(cat_id, {})
            
            results.append({
                "category_id": cat_id,
                "category_name": category_info.get('name', 'Unknown Category'),
                "top_product": product_info.get('name', 'Unknown Product'),
                "total_quantity": round(quantity, 2),
                "category_total": round(data_loader_instance.category_sales[cat_id], 2)
            })

        # return the sorted results by category total in descending order
        return jsonify(sorted(results, key=lambda x: x['category_total'], reverse=True))

    except DataLoaderException as e:
        # log data-related error and return the exception details
        current_app.logger.error(f"Data error: {str(e)}", exc_info=True)
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        # log unexpected error and return a generic error message
        current_app.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# endpoint to get most sold products by country
@api_bp.route('/most_sold_by_country', methods=['GET'])
@cache.cached(timeout=300)
def get_most_sold_by_country():
    """
    Get most sold products by country.
    ---
    responses:
      200:
        description: List of products most sold by country.
    """
    try:
        result = [
            {
                "country": country,
                "product_id": max_product[0],
                "product_name": data_loader_instance.products.get(max_product[0], {}).get("name", "unknown"),
                "total_quantity": round(max_product[1], 2),
                "country_code": data_loader_instance.country_code_map.get(country, "XX")
            }
            for country, country_products in data_loader_instance.country_product_sales.items()
            if country_products
            for max_product in [max(country_products.items(), key=lambda x: x[1])]
        ]
        
        return jsonify(result)
    
    except Exception as e:
        # log error and return it as a response
        current_app.logger.error(f"Error in /most_sold_by_country: {str(e)}")
        return jsonify({"error": str(e)}), 500

# endpoint to get the top client who bought the most unique products
@api_bp.route('/top_client', methods=['GET'])
@cache.cached()
def get_top_client():
    """
    Get the client who bought the most unique products.
    ---
    responses:
      200:
        description: Client with the most unique products bought.
      404:
        description: No client data available.
    """
    try:
        # check if client data is available
        if not data_loader_instance.client_products:
            current_app.logger.info("No client data available.")
            return jsonify({"message": "No client data available"}), 404

        # find the client who bought the most unique products
        client_id, products = max(
            data_loader_instance.client_products.items(),
            key=lambda x: len(x[1])
        )
        
        current_app.logger.info(f"Top client determined: {client_id}")
        
        # return client details with the number of unique products they bought
        return jsonify({
            "client_id": client_id,
            "client_name": data_loader_instance.contacts.get(client_id, {}).get("name", "unknown"),
            "unique_products": len(data_loader_instance.client_products[client_id])
        })
    
    except DataLoaderException as e:
        # log data-related error and return the exception details
        current_app.logger.error(f"Error: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        # log unexpected error and return a generic error message
        current_app.logger.error(f"Unexpected error in /top_client: {e}")
        return jsonify({"error": str(e)}), 500
