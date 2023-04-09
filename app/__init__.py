from flask import Flask
from flask_restx import Api
from .api.admin import admin
from .api.user import user as user_api
from .api.pray import pray
import os

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('APP_CONFIG_FILE')
    CORS(app, resources={r'*': {'origins': ['http://localhost:3000', os.getenv('CORS_ORIGIN')]}})

    # Swagger
    authorizations = {
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        }
    }
    api = Api(
        app,
        version=1.0,
        title='API',
        description='API 명세서 입니다.',
        prefix='/api',
        authorizations=authorizations,
        security='apikey'
    )
 
    api.add_namespace(admin, '')
    api.add_namespace(user_api, '/user')
    api.add_namespace(pray, '/pray')
    app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

    # ORM
    from .models import db
    #from .models import pray
    db.init_app(app)
    migrate = Migrate(app, db)
    # migrate.init_app(app, db)

    # Error Handler
    from .error_handler import CustomUserError, handle_custom_user_error
    app.register_error_handler(CustomUserError, handle_custom_user_error)

    return app
