# from config.default import *
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    user='postgres',
    pw='postgres',
    url='localhost',
    db='postgres')
SQLALCHEMY_TRACK_MODIFICATIONS = False