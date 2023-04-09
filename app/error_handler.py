from flask import jsonify

class CustomUserError(Exception):
    def __init__(self, statusCode, devErrorMessage, errorMessage):
        self.statusCode = statusCode
        self.devErrorMessage = devErrorMessage
        self.errorMessage = errorMessage
        self.rv = dict(
            statusCode=self.statusCode,
            devErrorMessage=self.devErrorMessage,
            errorMessage=self.errorMessage
        )
        
    def to_dict(self):
        return self.rv


class SignUpFail(CustomUserError):
    def __init__(self, errorMessage, devErrorMessage=None):
        statusCode = 400
        if not devErrorMessage:
            devErrorMessage = "SignUpFail error"
        super().__init__(statusCode, devErrorMessage, errorMessage)
        
    def to_dict(self):
        return self.rv

def handle_custom_user_error(error):
    response = jsonify(error.to_dict())
    response.statusCode = error.statusCode
    return response
