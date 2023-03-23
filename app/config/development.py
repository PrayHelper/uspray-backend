# from config.default import *
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#postgresql://postgres:postgres@db:5432/prayhelper
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    user='postgres',
    pw='postgres',
    url='db:5432',
    db='prayhelper') 
SQLALCHEMY_TRACK_MODIFICATIONS = False