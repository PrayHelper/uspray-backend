from flask import Blueprint
from flask_restx import Namespace, Resource

main = Namespace('main', description='main test API')


@main.route('')
class Main(Resource):
    def get(self):
        return {'message': 'Hello World'}