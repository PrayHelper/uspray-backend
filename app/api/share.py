from flask_restx import Namespace, Resource, fields
from app.decorators.login_required import login_required
from flask import request, g
import urllib.parse
from app.utils.share import ShareService
from urllib.parse import parse_qsl, urlparse, urlunparse, unquote

share = Namespace('share', description='Share related operations')

shareModel = share.model('Share', {
    'target': fields.String(required=True, default='이수빈', description='pray target'),
    'title': fields.String(required=True, default='기도합니다', description='pray title'),
    'deadline': fields.Date(required=True, default='2024-08-01', description='pray deadline')
})    

prayListModel = share.model('PrayList', {
    'pray_id_list': fields.List(fields.Integer, required=True, description='pray id list')
})

pray_list_encoding = share.parser()
pray_list_encoding.add_argument('pray_list', type=str, required=True, help='pray list', location='args')

@share.route('', methods=['GET', 'POST', 'DELETE'])
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
      기도제목 리스트를 공유하고 공유 url을 반환합니다.
      """
      content = request.json
      pray_list = ",".join(str(pray_id) for pray_id in content['pray_id_list'])
      return "https://api.uspray.krapi/share/social?pray_list=" + urllib.parse.quote(pray_list)
    

    @login_required
    @share.expect(prayListModel)
    def delete(self):
      """
      공유받은 기도제목을 삭제합니다.
      """
      content = request.json
      return ShareService.delete_share_list(content['pray_id_list'])

    
    
@share.route('/storage/save', methods=['POST'])
class ShareStorage(Resource):
    @login_required
    @share.expect(prayListModel)
    def post(self):
      """
      공유 받은 기도제목을 저장합니다.
      """
      content = request.json
      return ShareService.save_storage(content['pray_id_list'])

    

@share.route('/social/<string:user_id>', methods=['GET'])
class SharePrayByLink(Resource):
    # @login_required
    @share.expect(pray_list_encoding)
    def get(self, user_id):
      """
      기도제목을 공유합니다. 
      """
      parsed_url = urlparse(request.url)
      query_params = parse_qsl(parsed_url.query)
      g.user_id = user_id

      pray_list_encoding_str = next((val for key, val in query_params if key == 'pray_list'), None)
      if pray_list_encoding_str:
          prays_decoded = [int(todo) for todo in unquote(pray_list_encoding_str).split(',')]
          return ShareService.share_pray(prays_decoded)
    

