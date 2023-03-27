from flask_restx import Namespace, Resource
from flask_restx import Namespace, Resource, fields
from flask import request, g, jsonify

from app import db
from app.models.user import User
#from app.models.pray import Pray
#from app.dto.pray import PrayDTO 

pray = Namespace('pray', description='pray test API')

prayListModel = pray.model('Pray', {
    'id': fields.Integer(required=True, description='pray id'),
    'uuid': fields.String(required=True, description='user uuid'),
    'deadline': fields.Date(required=True, description='pray deadline'),
    'target': fields.String(required=True, description='pray target'),
    'title': fields.String(required=True, description='pray title'),
})

@pray.route('/list/<string:uid>', methods=['GET'])
class Pray(Resource):
    @pray.doc(params={'uid': 'uuid'})
    @pray.response(200, 'Success', prayListModel)
    def get(self, uid):
        """
        Get Pray List
        """
        # user = User.query.filter_by(uid=uid).first()
        # if not user:
        #     return { 'message': '사용자가 존재하지 않습니다.' }, 400
        # prayList = user.pray_set
        prayList = [
          { 'id': 1, 
						'uuid': 'uuid',
						'deadline': '2023-01-02',
						'target': '이수빈',
						'title': '기도합시다'
					},
					{ 'id': 2, 
						'uuid': 'uuid',
						'deadline': '2023-01-03',
						'target': '배서현',
						'title': '파이팅'
					},
					{ 'id': 3, 
						'uuid': 'uuid',
						'deadline': '2023-01-04',
						'target': '김하람',
						'title': '안뇽'
					},
					{ 'id': 4, 
						'uuid': 'uuid',
						'deadline': '2023-01-05',
						'target': '권은혜',
						'title': '메렁'
					},
					{ 'id': 5, 
						'uuid': 'uuid',
						'deadline': '2023-01-06',
						'target': '이수빈',
						'title': '기도합시다'
					}
				]
        return prayList, 200
