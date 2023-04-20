from app.decorators.login_required import login_required
from flask_restx import Namespace, Resource, fields
from flask import request, g
from app.utils.pray import PrayDAO, PrayDTO, StorageDAO, StorageDTO, StorageService
from app.models.pray import Pray

pray = Namespace('pray', description='pray test API')

prayListModel = pray.model('Pray', {
    'target': fields.String(required=True, default='이수빈', description='pray target'),
    'title': fields.String(required=True, default='기도합니다', description='pray title'),
    'deadline': fields.Date(required=True, description='pray deadline'),
})

@pray.route('', methods=['POST'])
class PrayPost(Resource):
	@pray.expect(prayListModel)
	@login_required
	def post(self):
		"""
		기도제목을 입력합니다.
		"""
		user_id = g.user_id
		user = g.user
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
		storages = StorageService.get_storages(user_id)
		return { 'res': storages }, 200

@pray.route('/<int:pray_id>', methods=['GET'])
class PrayDetail(Resource):
	@login_required
	def get(self, pray_id):
		"""
		기도제목을 조회합니다.
		"""
		# TODO: @login_required 추가 후 자신의 pray인지 확인하는 로직 추가하기
		user_id = g.user_id
		pray = Pray.query.filter_by(id=pray_id).first()
		if pray is None:
			return { 'message': '기도제목이 존재하지 않습니다.' }, 400
		else:
			if str(pray.user_id) != str(user_id):
				return { 'message': '기도제목 아이디가 올바르지 않습니다.' }, 400
			return StorageService.get_storage(pray_id), 200
		
			
	
	def delete(self, pray_id):
		"""
		기도제목을 삭제합니다.
		"""
		# TODO: StorageService.delete_storage(pray_id) + @login_required 추가하기

	def put(self, pray_id):
		"""
		기도제목을 수정합니다.
		"""
		# TODO: StorageService.update_storage(pray_id) + @login_required 추가하기

	