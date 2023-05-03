from flask_restx import Namespace, Resource, fields
from app.decorators.login_required import login_required
from app.models.pray import Pray, Share
from flask import g
from flask import request
from app.models import db
import datetime

from app.utils.share import ShareService

share = Namespace('share', description='Share related operations')

shareModel = share.model('Share', {
    'target': fields.String(required=True, default='이수빈', description='pray target'),
    'title': fields.String(required=True, default='기도합니다', description='pray title'),
    'deadline': fields.Date(required=True, default='2024-08-01', description='pray deadline')
})    

# 공유제목 아이디 리스트를 받아옵니다.
prayListModel = share.model('PrayList', {
    'pray_id_list': fields.List(fields.Integer, required=True, description='pray id list')
})


@share.route('', methods=['GET', 'POST'])
class Share(Resource):
    @login_required
    def get(self):
      """
      공유받은 기도제목 목록을 조회합니다. (보관함)
      """
      share_list = ShareService.get_share_list()
      return share_list
    
    @login_required
    @share.expect(prayListModel)
    def post(self):
      """
      기도제목을 공유받습니다. 
      """
      content = request.json
      return ShareService.share_pray(content['pray_id_list'])
    
@share.route('/storage/<int:pray_id>', methods=['POST'])
class ShareStorage(Resource):
    @login_required
    def post(self, pray_id):
      """
      공유 받은 기도제목을 저장합니다.
      """
      return ShareService.save_storage(pray_id)
    