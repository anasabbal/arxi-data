class DataLoaderException(Exception):
    """custom exception for handling data loader errors."""
    
    def __init__(self, message: str, status_code: int = 400):
        # call the parent exception class constructor
        super().__init__(message)
        self.message = message  # store the error message
        self.status_code = status_code  # store the HTTP status code (default is 400)

    def to_dict(self):
        """convert the exception to a dictionary for json response."""
        # return a dictionary with the error message and status code
        return {'error': self.message, 'status_code': self.status_code}
