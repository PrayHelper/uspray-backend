import base64
from app.decorators.login_required import login_required
from flask_restx import Namespace, Resource, fields
from flask import request
from app.utils.pray import PrayService, StorageService
from app.models import db
from app.models.pray import Pray as P
pray = Namespace('pray', description='pray test API')

prayModel = pray.model('Pray', {
    'target': fields.String(required=True, default='이수빈', description='pray target'),
    'title': fields.String(required=True, default='기도합니다', description='pray title'),
    'deadline': fields.Date(required=True, default='2024-08-01', description='pray deadline')
})

prayUpdateModel = pray.model('Pray Update', {
	'pray_cnt': fields.Integer(required=False, default=0, description='pray count'),
	'deadline': fields.Date(required=False, default='2024-08-01', description='pray deadline')
})

prayListSortBy = pray.parser()
prayListSortBy.add_argument('sort_by', type=str, required=False, help='date or cnt', location='args', default='date')

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
	@pray.expect(prayListSortBy)
	def get(self):
		"""
		기도제목 목록을 조회합니다.
		"""
		args = prayListSortBy.parse_args()
		return StorageService.get_storages(args['sort_by']), 200


@pray.route('/<int:pray_id>', methods=['GET', 'DELETE', 'PUT'])
class PrayDetail(Resource):
	@login_required
	def get(self, pray_id):
		"""
		기도제목을 조회합니다. (마감일이 지나지 않은 기도제목만 반환)
		"""
		return StorageService.get_storage(pray_id), 200
		

	@login_required
	def delete(self, pray_id):
		"""
		기도제목을 삭제합니다.
		"""
		StorageService.delete_storage(pray_id)
		return StorageService.get_storages(), 200


	@pray.expect(prayUpdateModel)
	@login_required
	def put(self, pray_id):
		"""
		기도제목을 수정합니다. *공유 받은 기도제목, deadline만 수정 가능*
		"""
		content = request.json
		return StorageService.update_storage(pray_id, content), 200
	

@pray.route('/my/<int:pray_id>', methods=['PUT'])
class MyPrayEdit(Resource):
	@login_required
	@pray.expect(prayModel)
	def put(self, pray_id):
		"""
		나의 기도제목을 수정합니다. *공유 전 나의 기도제목만 수정 가능*
		"""
		content = request.json
		return PrayService.update_pray(content, pray_id), 200
	

@pray.route('/complete/<int:pray_id>', methods=['PUT'])
class PrayComplete(Resource):
		@login_required
		def put(self, pray_id):
			"""
			기도를 완료합니다. 오늘의 기도를 완료한 경우, 기도횟수를 증가시킵니다.
			"""
			StorageService.increase_cnt(pray_id)
			return StorageService.get_storages(), 200
		

@pray.route('/finish/<int:pray_id>', methods=['PUT'])
class PrayFinish(Resource):
		@login_required
		def put(self, pray_id):
			"""
			기도제목을 마감합니다. 마감일을 오늘로 수정합니다. 
			"""
			StorageService.finish_storage(pray_id)
			return StorageService.get_storages(), 200