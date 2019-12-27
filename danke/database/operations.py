from danke.database import db
from danke.core.transaction import Transaction

from .forum import Forum
from .topic import Topic, Post, Comment
from .topic_course import TopicCourse, PostCourse
from .user import User

from datetime import datetime
import time


# * topic and post Models

__topic_type_to_model = [None, TopicCourse]
__post_type_to_model = [None, PostCourse]


def __create_topic_extend(data_type, **extend):
    '''
    实例化TopicExtend
    '''
    Model = __topic_type_to_model[data_type]
    if Model:
        return Model(**extend)
    else:
        return None


def __get_topic_extend_of_topic(topic):
    '''
    得到属于topic的topic_extend
    如果没有对应的Model直接返回None
    '''
    Model = __topic_type_to_model[topic.data_type]
    if Model:
        return Model.find(topic.data_id)
    else:
        return None


def __get_post_extend_of_post(post):
    '''
    得到属于post的post_extend
    如果没有对应的Model直接返回None
    '''
    Model = __post_type_to_model[post.data_type]
    if Model:
        return Model.find(post.data_id)
    else:
        return None


def __create_post_extend(data_type, **extend):
    '''
    实例化PostExtend
    '''
    Model = __post_type_to_model[data_type]
    if Model:
        return Model(**extend)
    else:
        return None

# * topic and forum


def __new_topic_init(topic):
    '''
    初始化新的topic
    Topic被实例化时，有些额外的工作需要做，如求得preview等
    '''
    # new Topic后, 初始化一些变量
    # TODO: make preview
    topic.last_reply_post_id = 0  # 表示新帖
    topic.last_reply_post_preview = topic.preview
    topic.last_reply_user_id = topic.user_id
    topic.last_reply_user_nickname = User.find(user_id=topic.user_id).nickname
    topic.last_reply_time = int(time.time())


def __forum_update_by_topic(forum, topic):
    '''
    父板块forum被子帖topic更新信息
    '''
    forum.last_reply_topic_id = topic.id
    forum.last_reply_topic_title = topic.title
    forum.last_reply_topic_preview = topic.last_reply_post_preview
    forum.last_reply_user_id = topic.last_reply_user_id
    forum.last_reply_user_nickname = topic.last_reply_user_nickname
    forum.last_reply_time = topic.last_reply_time


def __forum_update_by_forum(supforum, forum):
    '''
    父板块supforum被子版块forum更新信息
    '''
    supforum.last_reply_topic_id = forum.last_reply_topic_id
    supforum.last_reply_topic_title = forum.last_reply_topic_title
    supforum.last_reply_topic_preview = forum.last_reply_topic_preview
    supforum.last_reply_user_id = forum.last_reply_user_id
    supforum.last_reply_user_nickname = forum.last_reply_user_nickname


def __db_topic_update_forums(topic, is_new=False):
    '''
    新的topic更新父级板块的信息
    如最后回复时间等，帖子数等
    is_new 判断是否为新帖子
    '''
    forum = topic.forum
    __forum_update_by_topic(forum, topic)
    forum.count_topics += 1
    forum.db_save()
    father = forum.supforum
    while father:
        __forum_update_by_forum(father, forum)
        father.count_topics += 1
        father.db_save()
        father = father.supforum


# * 创建板块
def create_forum(kwargs):
    '''
    创建板块
    '''
    forum = Forum(**kwargs)
    forum.db_save()


# * 创建帖子
def create_topic(kwargs):
    '''
    创建一个topic，需要new topic和topic_extend
    再用topic_extend更新topic的内容
    最后新的topic递归更新上级板块们的信息
    '''
    topic, topic_extend = __db_create_topic_with_extend(kwargs)
    if topic_extend:
        topic_extend.db_update_topic(topic)
    __db_topic_update_forums(topic, is_new=True)


def __db_create_topic_with_extend(kwargs):
    '''
    使用事务同时创建topic和topic_extend
    '''
    with Transaction(db):
        data_type = kwargs.get('data_type', None)
        data_id = 0
        assert data_type is not None
        extend = kwargs.get('extend', {})
        topic_extend = __create_topic_extend(data_type, **extend)
        if topic_extend:
            data_id = topic_extend.id
        kwargs['data_id'] = data_id
        topic = Topic(**kwargs)
        __new_topic_init(topic)
        if topic_extend:
            db.session.add(topic_extend)
        db.session.add(topic)
        return topic, topic_extend


# * 创建回帖
def create_post(kwargs):
    '''
    创建一个post，需要new post和post_extend
    再用post_extend更新post的内容
    最后新的post递归更新所属帖子和上级板块们的信息
    '''
    post, post_extend = __db_create_post_with_extend(kwargs)
    topic = post.topic
    topic_extend = __get_topic_extend_of_topic(topic)
    if post_extend:
        post_extend.db_update_post(post)
        if topic_extend:
            post_extend.db_update_tpoic_extend(topic_extend, is_new=True)
    post.db_update_topic(topic, is_new=True)
    if topic_extend:
        topic_extend.db_update_topic(topic)
    __db_topic_update_forums(topic)


def __db_create_post_with_extend(kwargs):
    '''
    使用事务创建post和post_extend
    '''
    with Transaction(db):
        data_type = kwargs.get('data_type', None)
        data_id = 0
        assert data_type is not None
        extend = kwargs.get('extend', {})
        post_extend = __create_post_extend(data_type, **extend)
        if post_extend:
            data_id = post_extend.id
        kwargs['data_id'] = data_id
        post = Post(**kwargs)
        # TODO 是否需要new_post_init
        if post_extend:
            db.session.add(post_extend)
        db.session.add(post)
        return post, post_extend


# * 创建评论
def create_comment(kwargs):
    '''
    创建comment
    实例化comment，然后更新post的评论数即可，post不再更新topic
    '''
    comment = Comment(**kwargs)
    # TODO 是否需要new_comment_init
    comment.db_save()
    comment.db_update_post(comment.post, is_new=True)


# * 获取主页数据
def get_home_page():
    root = Forum.find(1)
    assert root != None
    forums = root.subforums.all()
    forums = sorted(
        forums, key=lambda item: (-item.cmp_key, -item.last_reply_time))
    __make_home_page(forums)
    return forums

# 之后的makeXXX主要功能是处理一些属性值，和一些递归属性，不应该将改变保存到数据库


# * 获取板块页数据
def get_forum_page(forum_id):
    forum = Forum.find(forum_id)
    __make_forum_data(forum)
    return forum

# * 获取帖子页数据


def get_topic_page(topic_id):
    topic = Topic.find(topic_id)
    __make_topic_data(topic)
    return topic


def __make_home_page(forums):
    for forum in forums:
        __make_forum_data(forum)


def __make_forum_data(forum):
    if not forum:
        return
    forum.supforums = get_supforums_data(forum)
    subforums = forum.subforums.all()
    subforums = sorted(
        subforums, key=lambda item: (-item.cmp_key, -item.last_reply_time))
    for subforum in subforums:
        __make_forum_forum_data(subforum)
    forum.subforum_list = subforums
    topics = forum.topics.all()
    topics = sorted(
        topics, key=lambda item: (-item.cmp_key, -item.last_reply_time))
    top_topic_list = []
    other_topic_list = []
    for topic in topics:
        __make_forum_topic_data(topic)
        if topic.cmp_key > 0:
            top_topic_list.append(topic)
        else:
            other_topic_list.append(topic)
    forum.top_topic_list = top_topic_list
    forum.other_topic_list = other_topic_list


def __make_topic_data(topic):
    if not topic:
        return
    topic.supforums = get_supforums_data(topic.forum)
    posts = topic.posts.all()
    # TODO
    # posts = sorted(posts, key=lambda item: -item.last_reply_time)
    for post in posts:
        __make_topic_post_data(post)
    topic.post_list = posts
    topic.topic_time = make_time_str(topic.topic_time)
    topic.extend = __get_topic_extend_of_topic(topic)


def __make_topic_post_data(post):
    if not post:
        return
    post.post_time = make_time_str(post.post_time)
    post.extend = __get_post_extend_of_post(post)
    comments = post.comments.all()
    # TODO
    # comments = sorted(...)
    for comment in comments:
        __make_topic_post_comment_data(comment)
    post.comment_list = comments


def __make_topic_post_comment_data(comment):
    if not comment:
        return
    comment.comment_time = make_time_str(comment.comment_time)


def __make_forum_forum_data(forum):
    if not forum:
        return
    forum.last_reply_time = make_time_str(forum.last_reply_time)


def __make_forum_topic_data(topic):
    if not topic:
        return
    topic.topic_time = make_time_str(topic.topic_time)
    topic.last_reply_time = make_time_str(topic.last_reply_time)


def get_supforums_data(forum):
    ret = []
    if not forum:
        return ret
    now = forum
    while now != None:
        # nothing to do with now
        ret.append(now)
        now = now.supforum
    return ret[::-1]


def make_time_str(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%y-%m-%d %H:%M:%S')
