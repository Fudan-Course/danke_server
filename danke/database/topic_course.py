from danke.database import db
from danke.core.transaction import Transaction

from .topic import Topic


class TopicCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 课程名称:	大气动力学基础
    name = db.Column(db.String(120), nullable=False, default='')
    # 课程代码:	ATMO130001
    code = db.Column(db.String(120), nullable=False, default='')
    # 课程序号:	ATMO130001.01
    index = db.Column(db.String(120), nullable=False, default='')
    # 学期:	2019-2020学年1学期
    term = db.Column(db.String(120), nullable=False, default='')
    # 考试方式	闭卷 （期中+期末闭卷， 论文，其他）
    final = db.Column(db.String(120), nullable=False, default='')
    # 学分:	4
    credit = db.Column(db.Integer, nullable=False, default=0)
    # 开课院系:	大气与海洋科学系
    department = db.Column(db.String(120), nullable=False, default='')
    # 校区:	江湾校区
    campus = db.Column(db.String(120), nullable=False, default='')
    # 备注	校级精品课程 不接受期中退课
    note = db.Column(db.String(120), nullable=False, default='')
    # 是否允许期中退课
    allow_quit = db.Column(db.Boolean, nullable=False, default=False)
    # 选课类别 (七模，)
    category = db.Column(db.String(120), nullable=False, default='')
    # 课程介绍
    raw_description = db.Column(db.Text)  # markdown
    description = db.Column(db.Text)  # rendered markdown
    # 课程教师 (TODO 这里应该改成多个teacher  果然还是NOSQL适合这种场景啊 表还是太麻烦了)
    teacher = db.Column(db.String(120), nullable=False, default='')

    # 以下是自动统计的数据，下面的都是加和，展示时需要除以count_scorers
    # 评分人数
    count_scorers = db.Column(db.Integer, nullable=False, default=0)
    # 难易
    difficulty = db.Column(db.Integer, nullable=False, default=0)
    # 任务量
    tasks = db.Column(db.Integer, nullable=False, default=0)
    # 给分好坏
    grading = db.Column(db.Integer, nullable=False, default=0)
    # 收获多少
    gains = db.Column(db.Integer, nullable=False, default=0)
    # 是否推荐的整体评分
    score = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, name, code, index, term, final, credit, department, campus, note, allow_quit, category, raw_description, description, teacher, **kwargs):
        self.name = name
        self.code = code
        self.index = index
        self.term = term
        self.final = final
        self.credit = credit
        self.department = department
        self.campus = campus
        self.note = note
        self.allow_quit = allow_quit
        self.category = category
        self.raw_description = raw_description
        self.description = description
        self.teacher = teacher

    def __repr__(self):
        print('<Topic Course %r Name %r Teacher %r>' %
              (self.id, self.name, self.teacher))

    # 使用当前extend的信息更新topic的preview等信息
    def db_update_topic(self, topic):
        '''
        topic_course更新topic
        extend更新本体不需要判断是否为new
        '''
        # TODO
        topic.title = f'{self.name}({self.teacher})'
        topic.db_save()

    @staticmethod
    def find(data_id):
        return TopicCourse.query.filter_by(id=data_id).first()


class PostCourse(db.Model):
    # 新增评分和学期字段，这些评分可以前端展开
    id = db.Column(db.Integer, primary_key=True)
    # 难易
    difficulty = db.Column(db.Integer, nullable=False, default=6)
    # 任务量
    tasks = db.Column(db.Integer, nullable=False, default=6)
    # 给分好坏
    grading = db.Column(db.Integer, nullable=False, default=6)
    # 收获多少
    gains = db.Column(db.Integer, nullable=False, default=6)
    # 是否推荐的整体评分
    score = db.Column(db.Integer, nullable=False, default=6)

    def __init__(self, difficulty, tasks, grading, gains, score, **kwargs):
        self.difficulty = difficulty
        self.tasks = tasks
        self.grading = grading
        self.gains = gains
        self.score = score

    def __repr__(self):
        print('<Post %r type %r user_id %r>' %
              (self.id, self.data_type, self.user_id))

    def db_save(self):
        db.session.add(self)
        db.session.commit()

    # 使用当前extend的信息更新post的preview等信息
    def db_update_post(self, post):
        '''
        post_course更新post
        暂无
        '''
        # TODO
        pass

    # 已经存在的extend在被更新前要做什么
    def db_before_update(self, topic_course):
        '''
        消去本extend对topic的分数计算影响
        '''
        topic_course.count_scorers -= 1
        topic_course.difficulty -= self.difficulty
        topic_course.tasks -= self.tasks
        topic_course.grading -= self.grading
        topic_course.gains -= self.gains
        topic_course.score -= self.score
        topic_course.db_save()

    def db_update_topic_extend(self, topic_course, is_new):
        '''
        post_course更新topic_course，需要给出当前post_course是否为新的
        作为更新被调用时必须要先调用db_before_update
        '''
        topic_course.count_scorers += 1
        topic_course.difficulty += self.difficulty
        topic_course.tasks += self.tasks
        topic_course.grading += self.grading
        topic_course.gains += self.gains
        topic_course.score += self.score
        topic_course.db_save()
