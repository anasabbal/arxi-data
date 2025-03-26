import os






class Config:
    # get the secret key from the environment variable or use a default value "mysecret"
    SECRET_KEY = os.environ.get("ARXI_TEST", "mysecret")  
    # get the debug mode setting from the environment variable or default to True
    DEBUG = os.environ.get("DEBUG", True)  
    # set the cache type to SimpleCache
    CACHE_TYPE = "SimpleCache"  
    # set the default cache timeout to 300 seconds
    CACHE_DEFAULT_TIMEOUT = 300  
    # define the path to the "data" folder in the current directory
    DATA_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data")  
