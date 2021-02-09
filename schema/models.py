from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Table, Text, desc, asc
from sqlalchemy.inspection import inspect
from sqlalchemy.sql.expression import true
from sqlalchemy.sql.sqltypes import NullType
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# convert QueryObject to Dict
def as_dict(rows):
    dict = rows.__dict__
    if 'writer_id' in dict.keys():
        dict['writer'] = User.query.filter_by(id=dict['writer_id']).first().nickname
        del dict['writer_id']

    del dict['_sa_instance_state'] # delete sqlalchemy instance info

    return dict

def get_post(board, skip=0, number=3, target_id=None):
    if (target_id is not None):
            row = board.query.filter_by(id = target_id).first()
            if row is None:
                return {}
            else:
                return as_dict(row)
    else:
        tb = board.__tablename__
        rows = db.session.execute('SELECT * FROM ' + tb + ' ORDER BY ' + tb + '.posted_date DESC LIMIT ' + str(skip) + ', ' + str(number))

        columns = [c_attr.key for c_attr in inspect(board).mapper.column_attrs]
        items = []
        for row in rows:
            item = {}
            for idx in range(len(columns)):
                item[columns[idx]] = row[idx]
            items.append(item)
        
        for item in items:
            item['writer'] = User.query.filter_by(id=item['writer_id']).first().nickname
            del item['writer_id']
        
        return items

class User(db.Model):
    __tablename__ = 'user_tb'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'} # if you use unicode character

    id = db.Column(db.Integer, primary_key = True, unique=True, autoincrement=True)
    user_id = db.Column(db.String(16), nullable= False)
    nickname = db.Column(db.String(16), nullable= False)
    password = db.Column(db.String(128), nullable= False)
    loginstate = db.Column(db.Boolean)
    lastlogin = db.Column(db.DateTime)

    def __init__(self, user_id, nickname, password):
        self.user_id = user_id
        self.nickname = nickname
        self.password = password

    def add_user(self):
        new_user = User(self.user_id, self.nickname, self.password)
        
        db.session.add(new_user)
        db.session.commit()
    
    def update_user(self, user_id, update_data, update_type):
        id = self.query.filter_by(user_id = user_id).first()
        if id is None:
            return -1
        else:
            if (update_type == 'nickname'):
                id.nickname = update_data['nickname']
            elif (update_type == 'password'):
                # need to encrypt
                id.password = update_data['password']
            elif (update_type == 'lastlogin'):
                id.lastlogin = datetime.now()
            elif (update_type == 'loginstate'):
                if (not id.loginstate or id.loginstate is None):
                    id.loginstate = True
                else:
                    id.loginstate = False
            
            db.session.commit()

    def delete_user(self, user_id):
        self.query.filter_by(user_id = user_id).delete()
        db.session.commit()

    def get_userinfo(self, user_id=None, id=None):
        row = None
        if (id is not None):
            row = self.query.filter_by(id = id).first()
        elif (user_id is None):
            user_id = self.user_id
            row = self.query.filter_by(user_id = user_id).first()

        if row is None:
            raise ValueError
        else:
            return as_dict(row)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key = True, unique=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable = False)

    def __init__(self, user_id, name=False):
        if (name):
            self.user_id = User(None, None, None).get_userinfo(user_id=user_id).first().id
        else:
            self.user_id = user_id

    def add_admin(self):
        new_admin = Admin(self.user_id)

        db.session.add(new_admin)
        db.session.commit()

    def drop_admin(self):
        self.query.filter_by(user_id = self.user_id).delete()
        db.session.commit()
    
    def check_admin(self):
        row = self.query.filter_by(user_id = self.user_id).first()
        if row is None:
            return False
        else:
            return True

        
class Board(db.Model):
    __abstract__ = True # abstract class
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.Integer, primary_key = True, unique=True, autoincrement=True)
    title = db.Column(db.String(32), nullable = False)
    contents = db.Column(db.Text, nullable = False)
    writer_id = db.Column(db.Integer, nullable = False)
    posted_date = db.Column(db.DateTime, nullable = False, default = db.func.now())

    def __init__(self, data={}):
        if (data):
            self.postable = True
            title_len, contents_len = map(len, [data['title'].replace(" ", ""), data['contents'].replace(" ", "")])
            if (title_len == 0 or contents_len == 0):
                raise ValueError
            else:
                self.title = data['title']
                self.contents = data['contents']
                self.writer_id = data['writer_id']
                self.posted_date = datetime.now()
        else:
            self.postable = False
    
    def add_post(self):
        if (self.postable):
            db.session.add(self)
            db.session.commit()
        else:
            raise ValueError
    
    def delete_post(self, id):
        self.query.filter_by(id = id).delete()
        db.session.commit()

    def update_post(self, id, new_data):
        new_post = Board(new_data)
        if (new_post.postable):
            before_data = self.query.filter_by(id = id).first()
            before_data.title = new_data['title']
            before_data.contents = new_data['contents']
            before_data.posted_date = datetime.now()

            db.session.commit()
        else:
            raise ValueError


class NoticeBoard(Board):
    __tablename__ = 'noticeBoard_tb'
    
class FreeBoard(Board):
    __tablename__ = 'freeBoard_tb'

class QuestionBoard(Board):
    __tablename__ = 'questionBoard_tb'

class SecretBoard(Board):
    __tablename__ = 'secretBoard_tb'

    password = db.Column(db.String(128), nullable = False)

    def __init__(self, data={}):
        if (data):
            self.postable = True
            super().__init__(data)
            self.password = data['password']
        else:
            self.postable = False

    def update_post(self, id, new_data):
        new_post = SecretBoard(new_data)
        if (new_post.postable):
            before_data = self.query.filter_by(id = id).first()
            before_data.title = new_data['title']
            before_data.contents = new_data['contents']
            before_data.password = new_data['password']
            before_data.posted_date = datetime.now()

            db.session.commit()
        else:
            raise ValueError


