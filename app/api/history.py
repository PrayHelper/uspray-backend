from app.decorators.login_required import login_required
from flask_restx import Namespace, Resource, fields
from flask import request, g
from app.utils.pray import StorageService

history = Namespace('history', description='history test API')

pagination = history.parser()
pagination.add_argument('page', required=False, type=int, default=1)
pagination.add_argument('per_page', required=False, type=int, default=15)
pagination.add_argument('sort_by', required=False, type=str, default='date')

historyModifyModel = history.model('Modify Deadline', {
	'pray_id': fields.Integer(required=False, description='pray id'),
	'deadline': fields.Date(required=False, default='2021-08-01', description='modified deadline')
})

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


@history.route('/modify', methods=['PUT'])
class HistoryUpdate(Resource):
	@history.expect(historyModifyModel)
	@login_required
	def put(self):
		"""
		히스토리의 마감기한을 수정합니다.
		"""
		pray_id = content['pray_id']
		content = request.json
		return StorageService.update_storage(pray_id, content), 200
	
