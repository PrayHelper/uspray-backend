from flask import Flask
from flask_restx import Api
from .views.main import main

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('APP_CONFIG_FILE')

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
    from .views.user import user
    from .views.pray import pray
    api.add_namespace(main, '')
    api.add_namespace(user, '/user')
    api.add_namespace(pray, '/pray')
    app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

    # ORM
    from .models import user
    #from .models import pray
    db.init_app(app)
    migrate.init_app(app, db)

    return app
