from flask import Flask
from flask_restx import Api 
from .views.main import main
from .views.user import user

def create_app():
    app = Flask(__name__)

    # Swagger
    authorizations = {
        'basic': {
            'type': 'basic',
            'in': 'header',
            'name': 'ACCESS-KEY'
        }
    }
    api = Api(
        app, 
        version=1.0, 
        title='API', 
        description='API 명세서 입니다.', 
        prefix='/api', 
        security='basic'
    )
    api.add_namespace(main, '')
    api.add_namespace(user, '/user')
    app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

    return app