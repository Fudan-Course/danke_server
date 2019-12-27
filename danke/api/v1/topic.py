from flask_restplus import Namespace, Resource, fields, reqparse
from danke.core.render import Render
from danke.core.tool import *
from danke.database.topic import Topic as TopicModel
from danke.database.operations import create_topic, get_topic_page, create_post, create_comment

api = Namespace('topics', description='帖子相关操作')

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

TopicPostCommentData = api.model('TopicPostCommentData', {
    'id': fields.Integer(),
    'raw_content': fields.String(),
    'content': fields.String(),
    'user': fields.Nested(SimpleUserData),
    'is_deleted': fields.Boolean(),
    'comment_time': fields.String()
})

TopicPostData = api.model('TopicPostData', {
    'id': fields.Integer(),
    'raw_content': fields.String(),
    'content': fields.String(),
    'user': fields.Nested(SimpleUserData),
    'data_type': fields.Integer(),
    'is_deleted': fields.Boolean(),
    'post_time': fields.String(),
    'count_comments': fields.Integer(),
    'extend': fields.Raw(),
    'comment_list': fields.List(fields.Nested(TopicPostCommentData))
})

TopicData = api.model('TopicData', {
    'id': fields.Integer(),
    'title': fields.String(),
    'raw_content': fields.String(),
    'content': fields.String(),
    'user': fields.Nested(SimpleUserData),
    'topic_time': fields.String(),
    'data_type': fields.Integer(),
    'is_deleted': fields.Boolean(),
    'is_locked': fields.Boolean(),
    'supforums': fields.List(fields.Nested(ForumNavData)),
    'count_post': fields.Integer(),
    'count_views': fields.Integer(),
    'extend': fields.Raw(),
    'post_list': fields.List(fields.Nested(TopicPostData))
})


@api.route('/')
class Topics(Resource):
    NewTopicReq = api.model('NewTopicReq', {
        'session_id': fields.String(required=True),
        'title': fields.String(),
        'raw_content': fields.String(),
        'data_type': fields.Integer(),
        'is_locked': fields.Boolean(),
        'forum_id': fields.Integer()
    })
    NewTopicRsp = api.model('NewTopicRsp', {
        'err_code': fields.String(),
        'message': fields.String()
    })
    parser = reqparse.RequestParser()
    parser.add_argument('session_id', type=str)
    parser.add_argument('title', type=str)
    parser.add_argument('raw_content', type=str)
    parser.add_argument('data_type', type=int)
    parser.add_argument('is_locked', type=bool)
    parser.add_argument('forum_id', type=int)

    @api.doc('create_topic')
    @api.expect(NewTopicReq)
    @api.marshal_with(NewTopicRsp)
    def post(self):
        '''新建帖子'''
        kwargs = self.parser.parse_args()
        err_code, message = self.do_create_topic(**kwargs)
        return Render.common_response(err_code, message), 200

    def do_create_topic(self, session_id, **kwargs):
        now_user = get_login_user(session_id)
        if not now_user:
            return 1, '请登录'
        kwargs['user_id'] = now_user.id
        try:
            create_topic(kwargs)
        except Exception as e:
            return 1, str(e)
        return 0, '成功'


@api.route('/posts/')
class Posts(Resource):
    NewPostReq = api.model('NewPostReq', {
        'session_id': fields.String(required=True),
        'raw_content': fields.String(),
        'data_type': fields.Integer(),
        'topic_id': fields.Integer()
    })
    NewPostRsp = api.model('NewPostRsp', {
        'err_code': fields.String(),
        'message': fields.String()
    })
    parser = reqparse.RequestParser()
    parser.add_argument('session_id', type=str)
    parser.add_argument('raw_content', type=str)
    parser.add_argument('data_type', type=int)
    parser.add_argument('topic_id', type=int)

    @api.doc('create_post')
    @api.expect(NewPostReq)
    @api.marshal_with(NewPostRsp)
    def post(self):
        '''新建回帖'''
        kwargs = self.parser.parse_args()
        err_code, message = self.do_create_post(**kwargs)
        return Render.common_response(err_code, message), 200

    def do_create_post(self, session_id, **kwargs):
        now_user = get_login_user(session_id)
        if not now_user:
            return 1, '请登录'
        kwargs['user_id'] = now_user.id
        try:
            create_post(kwargs)
        except Exception as e:
            return 1, str(e)
        return 0, '成功'


@api.route('/posts/comments')
class Comments(Resource):
    NewCommentReq = api.model('NewCommentReq', {
        'session_id': fields.String(required=True),
        'raw_content': fields.String(),
        'post_id': fields.Integer()
    })
    NewCommentRsp = api.model('NewCommentRsp', {
        'err_code': fields.String(),
        'message': fields.String()
    })
    parser = reqparse.RequestParser()
    parser.add_argument('session_id', type=str)
    parser.add_argument('raw_content', type=str)
    parser.add_argument('post_id', type=int)

    @api.doc('create_comment')
    @api.expect(NewCommentReq)
    @api.marshal_with(NewCommentRsp)
    def post(self):
        '''新建评论'''
        kwargs = self.parser.parse_args()
        err_code, message = self.do_create_comment(**kwargs)
        return Render.common_response(err_code, message), 200

    def do_create_comment(self, session_id, **kwargs):
        now_user = get_login_user(session_id)
        if not now_user:
            return 1, '请登录'
        kwargs['user_id'] = now_user.id
        try:
            create_comment(kwargs)
        except Exception as e:
            return 1, str(e)
        return 0, '成功'


@api.route('/<topic_id>/page')
@api.param('topic_id', '帖子id')
class TopicPage(Resource):
    TopicPageRsp = api.model('TopicPageRsp', {
        'err_code': fields.Integer(required=True),
        'message': fields.String(),
        'data': fields.Nested(TopicData)
    })
    @api.doc('get_topic_page')
    @api.marshal_with(TopicPageRsp)
    def get(self, topic_id):
        '''获取板块页的数据'''
        topic_id = int(topic_id)
        err_code, message, data = self.do_get_topic_page(topic_id)
        return Render.common_response(err_code, message, data), 200

    def do_get_topic_page(self, topic_id):
        try:
            topic = get_topic_page(topic_id)
        except Exception as e:
            return 1, str(e), None
        return 0, '成功', topic
