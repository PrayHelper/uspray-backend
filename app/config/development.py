# from config.default import *
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{host}/{db}'.format(
    user='postgres',
    pw='postgres',
    host='localhost:5432',
    db='prayhelper') 
SQLALCHEMY_TRACK_MODIFICATIONS = False