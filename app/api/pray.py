from app.decorators.login_required import login_required
from flask_restx import Namespace, Resource, fields
from flask import request, g
from app.utils.pray import PrayService, StorageService
from app.models.pray import Storage
import datetime

pray = Namespace('pray', description='pray test API')

prayModel = pray.model('Pray', {
    'target': fields.String(required=True, default='이수빈', description='pray target'),
    'title': fields.String(required=True, default='기도합니다', description='pray title'),
    'deadline': fields.Date(required=True, default='2021-08-01', description='pray deadline')
})

prayUpdateModel = pray.model('Pray Update', {
	'pray_cnt': fields.Integer(required=False, default=0, description='pray count'),
	'deadline': fields.Date(required=False, default='2021-08-01', description='pray deadline')
})

@pray.route('', methods=['POST', 'GET'])
class Pray(Resource):
	@pray.expect(prayModel)
	@login_required
	def post(self):
		"""
		기도제목을 입력합니다.
		"""
		content = request.json
		return PrayService.create_pray(content['target'], content['title'], content['deadline']), 200
	
	@login_required
	def get(self):
		"""
		기도제목 목록을 조회합니다.
		"""
		return StorageService.get_storages(), 200


@pray.route('/<int:pray_id>', methods=['GET', 'DELETE', 'PUT'])
class PrayDetail(Resource):
	@login_required
	def get(self, pray_id):
		"""
		기도제목을 조회합니다.
		"""
		return StorageService.get_storage(pray_id), 200
		

	@login_required
	def delete(self, pray_id):
		"""
		기도제목을 삭제합니다.
		"""
		StorageService.delete_storage(pray_id)
		return { 'message': '기도제목이 삭제되었습니다.' }, 204

	@pray.expect(prayUpdateModel)
	@login_required
	def put(self, pray_id):
		"""
		기도제목을 수정합니다.
		"""
		content = request.json
		return StorageService.update_storage(pray_id, content), 200
	
@pray.route('/increase-count/<int:pray_id>', methods=['PUT'])
class PrayDetail(Resource):
		@login_required
		def put(self, pray_id):
			"""
			기도를 완료합니다.
			"""
			StorageService.increase_cnt(pray_id)
			return StorageService.get_storages(), 200