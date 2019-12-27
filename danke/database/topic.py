from danke.database import db
from danke.core.transaction import Transaction

import time

'''
Topic定制化设计
Topic存储一楼信息，并拥有一堆Post
Post表示回帖，并拥有一堆Comment
Comment即为评论
Topic 包含data_type和data_id
data_type表示Topic扩展的数据是什么类型的
data_id表示Topic扩展的数据在对应表中的id
Post 只包含data_id
Post的扩展数据的类型继承于Topic的data_type
data_id表示Post扩展的数据在对应表中的id
例如
Topic data_type=1 data_id=1
表示扩展的数据存放在表CourseTopic的第一条
Post data_id=1
表示扩展的数据存放在表CoursePost的第一条
他们扩展的数据应该是对应一个data_type的

为此应该根据data_type提供三个函数
CourseTopicCreate 创建一个Course类型的帖子
CourseTopicUpdate 更新一个Course类型的帖子
CoursePostCreate 创建一个Course类型的回帖，并更新对应的Topic，Forum（更新摘要）
CoursePostUpdate 更新一个Course类型的回帖，并更新对应的Topic，Forum（更新摘要）

Topic
创建：给定一系列参数，CourseTopic的参数放在extend字段中，是一个字典。
     先创建Topic和CourseTopic，再将Topic传给CourseTopic用于初始化
     因为必须得到id，所以id的赋值放在Topic里，最终一起commit

create_topic():
    new topic
    new course_topic(topic) # course_topic在init中更新了topic的信息
    topic.data_id = course_topic.id
    topic_update_forum()


修改：取出Topic和CourseTopic的实例，先更新Topic，再将Topic和CourseTopic一起传给CourseTopic
     用extend数据进行更新

create_topic():
    get topic
    get course_topic(topic.id)
    topic.update()
    course_topic.update(topic.id)
    topic_update_forum()

Post
创建：给定一些列参数，CoursePost的参数放在extend字段中，是一个字典。
     先创建Post和CoursePost，再将Post传给CoursePost用于初始化
     因为必须得到id，所以id赋值放在Post中，一起commit
     创建好之后，需要更新Topic的一些字段
再之后只会用Topic本身的字段更新板块信息

为了不循环依赖，topic不应该依赖于topic_extend
'''


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, default='新主题')
    preview = db.Column(db.String(120))
    raw_content = db.Column(db.Text)  # markdown
    content = db.Column(db.Text)  # rendered markdown
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', backref=db.backref('topics', lazy='dynamic'))
    topic_time = db.Column(db.Integer)
    # 类型，0代表基础帖子，Topic本身的字段即可表示完全
    # 后续可以添加，如1代表一个课程的帖子，存储在 CourseTopic 表里，它有多个评分字段
    # data_id 存储表中的id，则
    # 增：新建Topic，根据data_type将参数表传给XXXTopic的构造函数，新建XXXTopic
    # 删：不支持真正的删除，只允许隐藏，因为XXXTopic不会直接被下发展示，所以不用再XXXTopic打标记
    # 查：查询到Topic时，顺带将对应的XXXTopic对象返回
    # 改：更新时，不同的Topic会有自己的更新过程，如课程会对评分重新计算
    data_type = db.Column(db.Integer, nullable=False, default=0)
    data_id = db.Column(db.Integer, nullable=False, default=0)
    # 是否已经删除，删除后不下发，但下发给管理员，待后续设计支持
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    # 是否锁定，锁定后不允许回复
    is_locked = db.Column(db.Boolean, nullable=False, default=False)
    # 所属板块
    forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'))
    forum = db.relationship(
        'Forum', backref=db.backref('topics', lazy='dynamic'))
    # 当前话题在板块中的置顶的排序关键字，越大越靠前，0为不置顶
    # 相同排序关键字应该按照最新动态排序
    cmp_key = db.Column(db.Integer, nullable=False, default=0)

    # 为了减少数据库查询，在这里直接记录最新动态的信息
    # 最新回复的话题id
    last_reply_post_id = db.Column(db.Integer)
    # 最新回复的回帖预览
    last_reply_post_preview = db.Column(db.String(120))
    # 最新回复的用户id
    last_reply_user_id = db.Column(db.Integer)
    # 最新回复的昵称
    last_reply_user_nickname = db.Column(db.String(120))
    # 最新回复的时间
    last_reply_time = db.Column(db.Integer)
    # 回帖数
    count_posts = db.Column(db.Integer, nullable=False, default=0)
    # 阅读数
    count_views = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, title, raw_content, user_id, data_type, data_id, is_locked, forum_id, **kwargs):
        # TODO
        self.title = title
        self.preview = raw_content[:15]
        self.raw_content = raw_content
        self.content = raw_content
        self.user_id = user_id
        self.data_type = data_type
        self.data_id = data_id
        self.is_locked = is_locked
        self.forum_id = forum_id
        self.topic_time = int(time.time())
        self.last_reply_time = int(time.time())

    def __repr__(self):
        print('<Topic %r Title  %r type %r id %r>' %
              (self.id, self.title, self.data_type, self.data_id))

    def db_save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def find(id):
        return Topic.query.filter_by(id=id).first()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    preview = db.Column(db.String(120))
    raw_content = db.Column(db.Text)  # markdown
    content = db.Column(db.Text)  # rendered markdown
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', backref=db.backref('posts', lazy='dynamic'))
    data_type = db.Column(db.Integer, nullable=False, default=0)
    data_id = db.Column(db.Integer, nullable=False, default=0)
    # 是否已经删除，删除后不下发，但下发给管理员，待后续设计支持
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    # 所属topic
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    topic = db.relationship(
        'Topic', backref=db.backref('posts', lazy='dynamic'))
    post_time = db.Column(db.Integer)
    # 回帖数
    count_comments = db.Column(db.Integer, nullable=False, default=0)
    # TODO 点赞数

    def __init__(self, raw_content, user_id, data_type, data_id, topic_id, **kwargs):
        self.preview = raw_content[:15]
        self.raw_content = raw_content
        self.content = raw_content
        self.user_id = user_id
        self.data_type = data_type
        self.data_id = data_id
        self.topic_id = topic_id
        self.post_time = int(time.time())

    def __repr__(self):
        print('<Post %r type %r user_id %r>' %
              (self.id, self.data_type, self.user_id))

    def db_save(self):
        db.session.add(self)
        db.session.commit()

    def db_update_topic(self, topic, is_new):
        '''
        当前post更新topic，需要给出当前post是否为真的
        '''
        if is_new:
            topic.last_reply_post_id = self.id
            topic.last_reply_post_preview = self.preview
            topic.last_reply_user_id = self.user_id
            topic.last_reply_user_nickname = self.user.nickname
            topic.last_reply_time = self.post_time
            topic.count_posts += 1
            topic.db_save()

    @staticmethod
    def find(id):
        return Post.query.filter_by(id=id).first()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raw_content = db.Column(db.Text)  # markdown
    content = db.Column(db.Text)  # rendered markdown
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', backref=db.backref('comments', lazy='dynamic'))
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    # 所属post
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship(
        'Post', backref=db.backref('comments', lazy='dynamic'))
    comment_time = db.Column(db.Integer)
    # TODO 点赞数

    def __init__(self, raw_content, user_id, post_id, **kwargs):
        self.raw_content = raw_content
        self.content = raw_content
        self.user_id = user_id
        self.post_id = post_id
        self.comment_time = int(time.time())

    def __repr__(self):
        print('<Comment %r user_id %r>' %
              (self.id, self.user_id))

    def db_save(self):
        db.session.add(self)
        db.session.commit()

    def db_update_post(self, post, is_new):
        '''
        当前comment更新post，需要给出是否为新的
        '''
        if is_new:
            post.count_comments += 1
            post.db_save()

    @staticmethod
    def find(id):
        return Comment.query.filter_by(id=id).first()