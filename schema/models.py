from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    # convert QueryObject to Dict
    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

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
                id.loginstate = not id.loginstate
            
            db.session.commit()

    def delete_user(self, user_id):
        self.query.filter_by(user_id = user_id).delete()
        db.session.commit()

