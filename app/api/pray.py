from app.decorators.login_required import login_required
from flask_restx import Namespace, Resource, fields
from flask import request, g
from app.utils.pray import PrayDAO, PrayDTO, StorageDAO, StorageDTO, StorageService

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
		return StorageDAO.create_storage(storage_dto), 200

@pray.route('/<int:pray_id>', methods=['GET'])
class PrayDetail(Resource):
	def get(self, pray_id):
		"""
		기도제목을 조회합니다.
		"""
		# TODO: @login_required 추가 후 자신의 pray인지 확인하는 로직 추가하기
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

	