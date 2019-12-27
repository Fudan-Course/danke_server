from danke.database import db


import time

# 设置板块1为root


class Forum(db.Model):
    # __tablename__ = 'forum'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, default='新版块')
    subtitle = db.Column(db.String(120))
    # ? 是否增加隐藏功能
    # 是否锁定，锁定后不允许发帖
    is_locked = db.Column(db.Boolean, nullable=False, default=False)
    # 如果允许发帖，是否只允许管理员发帖
    only_admin = db.Column(db.Boolean, nullable=False, default=False)
    # 封面
    cover = db.Column(db.String(120))
    # 父板块
    supforum_id = db.Column(db.Integer, db.ForeignKey('forum.id'))
    supforum = db.relationship(
        'Forum', backref=db.backref('subforums', lazy='dynamic'), remote_side=[id])
    # 当前板块在父板块中的排序关键字，越大越靠前，默认为0
    # 相同排序关键字应该按照最新动态排序
    cmp_key = db.Column(db.Integer, nullable=False, default=0)

    # 为了减少数据库查询，在这里直接记录最新动态的信息
    # 最新回复的帖子id
    last_reply_topic_id = db.Column(db.Integer)
    # 最新回复的帖子标题
    last_reply_topic_title = db.Column(db.String(120))
    # 最新回复的帖子预览
    last_reply_topic_preview = db.Column(db.String(120))
    # 最新回复的用户id
    last_reply_user_id = db.Column(db.Integer)
    # 最新回复的昵称
    last_reply_user_nickname = db.Column(db.String(120))
    # 最新回复的时间
    last_reply_time = db.Column(db.Integer)  # ? Integer
    # 发帖数(包括子版块)
    count_topics = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, title, subtitle, is_locked, only_admin, supforum_id, **kwargs):
        self.title = title
        self.subtitle = subtitle
        self.is_locked = is_locked
        self.only_admin = only_admin
        self.supforum_id = supforum_id
        self.last_reply_time = int(time.time())

    def __repr__(self):
        print('<Forum %r Title  %r>' % (self.id, self.title))

    def db_save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def find(id):
        return Forum.query.filter_by(id=id).first()
