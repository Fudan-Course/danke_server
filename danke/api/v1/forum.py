from flask_restplus import Namespace, Resource, fields, reqparse
from danke.core.render import Render
from danke.core.tool import *
from danke.database.user import User as UserModel
from danke.database.operations import get_home_page, create_forum, get_forum_page

api = Namespace('forums', description='板块相关操作')


# XXXData是要下发的数据
# NewXXXData是上传的数据

SimpleUserData = api.model('SimpleUserData', {
    'id': fields.Integer(),
    'nickname': fields.String(),
    'avatar': fields.String()
})

ForumNavData = api.model('ForumNavData', {
    'id': fields.Integer(),
    'title': fields.String()
})

ForumTopicData = api.model('ForumTopicData', {
    'id': fields.Integer(),
    'title': fields.String(),
    'preview': fields.String(),
    'user': fields.Nested(SimpleUserData),
    'topic_time': fields.String(),
    'is_deleted': fields.Boolean(),
    'last_reply_post_id': fields.Integer(),
    'last_reply_post_preview': fields.String(),
    'last_reply_user_id': fields.Integer(),
    'last_reply_user_nickname': fields.String(),
    'last_reply_time': fields.String(),
    'count_posts': fields.Integer(),
    'count_views': fields.Integer()
})


ForumForumData = api.model('ForumForumData', {
    'id': fields.Integer(),
    'title': fields.String(),
    'subtitle': fields.String(),
    'last_reply_topic_id': fields.Integer(),
    'last_reply_topic_title': fields.String(),
    'last_reply_topic_preview': fields.String(),
    'last_reply_user_id': fields.Integer(),
    'last_reply_user_nickname': fields.String(),
    'last_reply_time': fields.String(),
    'count_topics': fields.Integer()
})

ForumData = api.model('ForumData', {
    'id': fields.Integer(),
    'title': fields.String(),
    'subtitle': fields.String(),
    'is_locked': fields.Boolean(),
    'only_admin': fields.Boolean(),
    'cover': fields.String(),
    'supforums': fields.List(fields.Nested(ForumNavData)),
    'subforum_list': fields.List(fields.Nested(ForumForumData)),
    'top_topic_list': fields.List(fields.Nested(ForumTopicData)),
    'other_topic_list': fields.List(fields.Nested(ForumTopicData)),
    'count_topics': fields.Integer()
})


@api.route('/')
class Forums(Resource):
    # 主页
    ForumsRsp = api.model('ForumsRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String(),
        'data': fields.List(fields.Nested(ForumData))
    })
    @api.doc('get_homepage')
    @api.marshal_with(ForumsRsp)
    def get(self):
        '''获取主页的板块列表'''
        err_code, message, data = self.do_get_homepage()
        return Render.common_response(err_code, message, data), 200

    def do_get_homepage(self):
        try:
            forums = get_home_page()
        except Exception as e:
            return 1, str(e), None
        return 0, '成功', forums

    NewForumReq = api.model('NewForumReq', {
        'session_id': fields.String(required=True),
        'title': fields.String(),
        'subtitle': fields.String(),
        'is_locked': fields.Boolean(),
        'only_admin': fields.Boolean(),
        'supforum_id': fields.Integer()
    })
    NewForumRsp = api.model('NewForumRsp', {
        'err_code': fields.String(),
        'message': fields.String()
    })
    parser = reqparse.RequestParser()
    parser.add_argument('session_id', type=str)
    parser.add_argument('title', type=str)
    parser.add_argument('subtitle', type=str)
    parser.add_argument('is_locked', type=bool)
    parser.add_argument('only_admin', type=bool)
    parser.add_argument('supforum_id', type=int)

    @api.doc('create_forum')
    @api.expect(NewForumReq)
    @api.marshal_with(NewForumRsp)
    def post(self):
        '''新建板块'''
        kwargs = self.parser.parse_args()
        err_code, message = self.do_create_forum(**kwargs)
        return Render.common_response(err_code, message), 200

    def do_create_forum(self, session_id, **kwargs):
        now_user = get_login_user(session_id)
        if not now_user:
            return 1, '请登录'
        kwargs['user_id'] = now_user.id
        try:
            create_forum(kwargs)
        except Exception as e:
            return 1, str(e)
        return 0, '成功'

@api.route('/<forum_id>/page')
@api.param('forum_id', '板块id')
class ForumPage(Resource):
    ForumPageRsp = api.model('ForumPageRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String(),
        'data': fields.Nested(ForumData)
    })
    @api.doc('get_forum_page')
    @api.marshal_with(ForumPageRsp)
    def get(self, forum_id):
        '''获取板块页的数据'''
        forum_id = int(forum_id)
        err_code, message, data = self.do_get_forum_page(forum_id)
        return Render.common_response(err_code, message, data), 200
    
    def do_get_forum_page(self, forum_id):
        try:
            forum = get_forum_page(forum_id)
        except Exception as e:
            return 1, str(e), None
        return 0, '成功', forum

# @api.route('/<forum_id>/page')
# @api.param('forum_id', '板块id')
# class UserProfile(Resource):
#     '''
#     用户资料
#     get: 获取
#     put: 更新
#     '''
#     # get
#     UserProfileData = api.model('UserProfileData', {
#         'user_id': fields.Integer(required=True),
#         'username': fields.String(),
#         'email': fields.String(),
#         'description': fields.String(),
#         'nickname': fields.String()
#     })
#     UserProfileRsp = api.model('UserProfileRsp', {
#         'err_code': fields.Integer(required=True),
#         'message': fields.String(),
#         'data': fields.Nested(UserProfileData)
#     })
#     @api.doc('get_user_profile')
#     @api.marshal_with(UserProfileRsp)
#     def get(self, user_id):
#         '''通过user_id获取用户数据'''
#         err_code, message, data = self.do_get_user_profile(int(user_id))
#         return Render.common_response(err_code, message, data), 200

#     def do_get_user_profile(self, user_id):
#         user = UserModel.find(user_id=user_id)
#         if not user:
#             return 1, '用戶不存在', None
#         data = {
#             'user_id': user.id,
#             'username': user.name,
#             'email': user.email,
#             'description': user.description,
#             'nickname': user.nickname
#         }
#         return 0, '成功', data

#     # put
#     UserProfilePutReq = api.model('UserProfilePutReq', {
#         'session_id': fields.String(required=True),
#         'description': fields.String(),
#         'nickname': fields.String()
#     })
#     UserProfilePutRsp = api.model('UserProfilePutRsp', {
#         'err_code': fields.Integer(required=True),
#         'message': fields.String()
#     })
#     parser = reqparse.RequestParser()
#     parser.add_argument('session_id', required=True, type=str)
#     parser.add_argument('description', type=str)
#     parser.add_argument('nickname', type=str)

#     @api.doc('update_user_profile')
#     @api.expect(UserProfilePutReq)
#     @api.marshal_with(UserProfilePutRsp)
#     def put(self, user_id):
#         '''通过user_id更新用户数据'''
#         # get data from post
#         kwargs = self.parser.parse_args()
#         err_code, message = self.do_update_user_profile(int(user_id), kwargs)
#         return Render.common_response(err_code, message), 200

#     def do_update_user_profile(self, user_id, data):
#         now_user = get_login_user(data.session_id)
#         if not now_user:
#             return 1, '请登录'
#         if now_user.id != user_id and not now_user.have_permission(2):
#             return 1, '没有权限'
#         user = UserModel.find(user_id=user_id)
#         if not user:
#             return 2, '被修改资料用户不存在'
#         # update user by data
#         if data.description:
#             user.description = data.description  # TODO: 防止攻击
#         if data.nickname:
#             user.nickname = data.nickname  # TODO: 防止攻击
#         try:
#             user.save()
#             return 0, '成功'
#         except Exception as e:
#             print(e)
#             return 3, '保存用户信息失败'
