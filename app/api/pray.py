from app.decorators.login_required import login_required
from flask_restx import Namespace, Resource, fields
from flask import request, g
import jwt
import os

from app.models import db
from app.models.pray import Pray
from app.utils.pray import PrayDAO, PrayDTO, StorageDAO, StorageDTO

pray = Namespace('pray', description='pray test API')

prayListModel = pray.model('Pray', {
    'target': fields.String(required=True, default='이수빈', description='pray target'),
    'title': fields.String(required=True, default='기도합니다', description='pray title'),
    'deadline': fields.Date(required=True, description='pray deadline'),
})

@pray.route('', methods=['POST'])
class Pray(Resource):
	@pray.expect(prayListModel)
	@login_required
	def post(self):
		"""
		Pray Post
		"""
		user_id = g.user_id
		content = request.json

		pray_dto = PrayDTO(
			user_id=user_id,
			target=content['target'],
			title=content['title']
		)
		pray_dao = PrayDAO.create_pray(pray_dto)
		storage_dto = StorageDTO(
			user_id=user_id,
			pray_id=pray_dao.id,
			deadline=content['deadline']
		)
		storage_dao = StorageDAO.create_storage(storage_dto)
		return { 'message': 'success' }, 200

		
# @pray.route('/teest', methods=['GET'])
# class Pray(Resource):
#     def get(self):
#         a = Pray.query.filter_by(id=1).first()
#         return a

# @pray.route('/list', methods=['GET'])
# class Pray(Resource):
#     @pray.response(200, 'Success', prayListModel)
#     def get(self):
#         """
#         Get Pray List
#         """
#         user = User.query.filter_by(id=uid).first()
#         if not user:
#             return { 'message': '사용자가 존재하지 않습니다.' }, 400
#         prayList = user.pray_set
#         prayList = [
#           { 'id': 1, 
# 						'user_id': 'uuid',
# 						'deadline': '2023-01-02',
# 						'target': '이수빈',
# 						'title': '기도합시다'
# 					},
# 					{ 'id': 2, 
# 						'user_id': 'uuid',
# 						'deadline': '2023-01-03',
# 						'target': '배서현',
# 						'title': '파이팅'
# 					},
# 					{ 'id': 3, 
# 						'user_id': 'uuid',
# 						'deadline': '2023-01-04',
# 						'target': '김하람',
# 						'title': '안뇽'
# 					},
# 					{ 'id': 4, 
# 						'user_id': 'uuid',
# 						'deadline': '2023-01-05',
# 						'target': '권은혜',
# 						'title': '메렁'
# 					},
# 					{ 'id': 5, 
# 						'user_id': 'uuid',
# 						'deadline': '2023-01-06',
# 						'target': '이수빈',
# 						'title': '기도합시다'
# 					}
# 				]
#         return { 'res': prayList }, 200
