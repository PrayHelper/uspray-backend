from flask import Flask
from flask_restx import Api
from app.api.utils import send_push_notification, send
from app.utils.user import UserService
from app.models.user import User
from .api.admin import Scheduler, admin
from .api.user import user
from .api.pray import pray
from .api.share import share
from .api.history import history
import os

from flask_migrate import Migrate
from flask_cors import CORS
# from apscheduler.schedulers.background import BackgroundScheduler


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
    api.add_namespace(user, '/user')
    api.add_namespace(pray, '/pray')
    api.add_namespace(share, '/share')
    api.add_namespace(history, '/history')
    app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

    # ORM
    from .models import db
    db.init_app(app)
    migrate = Migrate(app, db)

    # Error Handler
    from .utils.error_handler import CustomUserError, handle_custom_user_error
    app.register_error_handler(CustomUserError, handle_custom_user_error)


    # def Scheduler():
    #         with app.app_context():
    #             users = User.query.filter(User.device_token != None).all()
    #             user_device_tokens = [user.device_token for user in users]
    #             print(user_device_tokens)
    #             # response = send_push_notification("🌅", "오전 8시 기도할 시간이에요", user_device_token, {})

    # # Scheduler
    # sched = BackgroundScheduler(daemon=True)
    # # sched.add_job(Scheduler, 'cron', day_of_week='0-6', hour=8)
    # sched.add_job(Scheduler, 'interval', seconds=60)
    # sched.start() 

    return app
