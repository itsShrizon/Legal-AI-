class BanglaLegalAIException(Exception):
    """Base exception for Bangla Legal AI"""
    pass

class ResourceNotFoundException(BanglaLegalAIException):
    def __init__(self, resource: str, id: str):
        self.message = f"{resource} with id {id} not found"
        super().__init__(self.message)

class AuthenticationException(BanglaLegalAIException):
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)
