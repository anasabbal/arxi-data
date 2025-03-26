import logging
from flask import Flask
from config import Config
from api import api_bp
from services.data_loader import data_loader_instance






def create_app():
    # create a new Flask application instance
    app = Flask(__name__)  
    # load configuration from the Config class
    app.config.from_object(Config)  

    # configure logging based on the environment (development/production)
    log_level = logging.DEBUG if app.config["DEBUG"] else logging.INFO  # set log level based on debug mode
    logging.basicConfig(
        # set the logging level
        level=log_level,  
        # log format with timestamp and function name
        format="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",  
        handlers=[  # specify the logging handlers
            # log to console for development
            logging.StreamHandler(),  
            # log to file in production
            logging.FileHandler("app.log", encoding="utf-8")  
        ]
    )
    # log a message indicating logging configuration
    app.logger.info("Logging is configured.")  
    # log the initialization of Flask with the config
    app.logger.info(f"Flask app initialized with config: {Config}")  

    # register the API blueprint with a URL prefix "/api"
    app.register_blueprint(api_bp, url_prefix="/api")  
    # log a message after registering the blueprint
    app.logger.info("API blueprint registered.")  

    with app.app_context():  # create an app context to initialize data
        # log that data initialization is starting
        app.logger.info("Initializing data...")  
        # initialize data using the data loader
        data_loader_instance.initialize_data()  
        # log after data initialization is complete
        app.logger.info("Data initialization complete.")  

    # return the Flask app instance
    return app  

# check if the script is run directly
if __name__ == '__main__':
    # create the app instance
    app = create_app()  
    # log that the server is starting
    app.logger.info("Starting Flask server.")  
    # start the Flask server on host 0.0.0.0 and port 5000
    app.run(host='0.0.0.0', port=5000)  
