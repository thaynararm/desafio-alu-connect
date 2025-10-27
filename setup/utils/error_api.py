DEFAULT_ERROR_STATUS_CODE = 400

class ErrorAPI(Exception):
    def __init__(self, status_code=DEFAULT_ERROR_STATUS_CODE,message=None, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.details = details
