from app.decorators.login_required import login_required
from app.dto.pray import PrayDTO
from flask_restx import Namespace, Resource
from flask_restx import Namespace, Resource, fields
from flask import request, g, jsonify
import jwt
import os

from app.models import db
from app.models.user import User
from app.models.pray import Pray
from app.dto.pray import PrayDTO 

pray = Namespace('pray', description='pray test API')

prayListModel = pray.model('Pray', {
    'target': fields.String(required=True, default='이수빈', description='pray target'),
    'title': fields.String(required=True, default='기도합니다', description='pray title'),
    'deadline': fields.Date(required=True, description='pray deadline'),
})

@pray.route('', methods=['POST'])
@login_required
class Pray(Resource):
	@pray.expect(prayListModel)
	def post(self):
		"""
		Pray Post
		"""
		access_token = request.headers.get("Authorization")
		payload = jwt.decode(access_token, os.getenv('SECRET_KEY'), algorithm="HS256")
		user_uuid = payload.id

		content = request.json
		u = PrayDTO.create_pray(
			id=user_uuid,
			target=content['target'],
			title=content['title']
		)
		# if u가 잘 생성됐을때 보관함 DTO 생성?
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
