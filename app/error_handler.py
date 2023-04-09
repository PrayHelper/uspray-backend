from flask import jsonify

class CustomUserError(Exception):
    def __init__(self, status_code, dev_error_message, error_message):
        self.status_code = status_code
        self.dev_error_message = dev_error_message
        self.error_message = error_message
        self.rv = dict(
            status_code=self.status_code,
            dev_error_message=self.dev_error_message,
            error_message=self.error_message
        )
        
    def to_dict(self):
        return self.rv


class SignUpFail(CustomUserError):
    def __init__(self, error_message, dev_error_message=None):
        status_code = 400
        if not dev_error_message:
            dev_error_message = "SignUpFail error"
        super().__init__(status_code, dev_error_message, error_message)
        
    def to_dict(self):
        return self.rv

def handle_custom_user_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
