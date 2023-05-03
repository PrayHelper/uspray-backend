from app.decorators.login_required import login_required
from flask_restx import Namespace, Resource, fields
from flask import request, g
from app.utils.pray import StorageService

history = Namespace('history', description='history test API')

pagination = history.parser()
pagination.add_argument('page', required=False, type=int, default=1)
pagination.add_argument('per_page', required=False, type=int, default=15)

@history.route('', methods=['GET'])
class History(Resource):
	@history.expect(pagination)
	@login_required
	def get(self):
		"""
		히스토리 목록을 조회합니다.
		"""
		content = pagination.parse_args()
		return StorageService.get_history(content), 200
	
