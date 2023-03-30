from flask import Flask
from flask_restx import Api
from .api.admin import admin
from .api.user import user as user_api
from .api.pray import pray

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('APP_CONFIG_FILE')

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
    migrate.init_app(app, db)

    return app
