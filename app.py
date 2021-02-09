# -*- coding: utf-8 -*
from flask import Flask, json, render_template, request, redirect, url_for, session, jsonify
from flask_wtf.csrf import CSRFProtect, validate_csrf
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import timedelta

from register_security import *
from init import create_app, formdata_to_dict
from schema import models


app = create_app()
bcrypt = Bcrypt(app)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes = 5)

def login_required(f):
    @wraps(f)
    def check_login(*args, **kwargs):
        if 'id' in session:
            return f(*args, **kwargs)
        else:
            return render_template('access_error.html', login_error=True)
    return check_login

@app.route('/', methods=['GET'])
def index():
    # data = {'title' : "test3", 'contents' : "aaa", 'writer' : 'admin'}
    nb, fb, qb, sb = models.NoticeBoard(), models.FreeBoard(), models.QuestionBoard(), models.SecretBoard()
    post_list = [models.get_post(nb), models.get_post(fb), models.get_post(qb), models.get_post(sb)]

    data = {'notice' : post_list[0], 'free' : post_list[1], 'question' : post_list[2], 'secret' : post_list[3]}
    data['nickname'] = session.get('nickname', None)

    return render_template('home.html', data=data)

@app.route('/login', methods=['POST'])
def login():
    data = formdata_to_dict(request.form)

    login_result = 'ID is not exist'
    nickname = ""
    validator = AccountValidator(data, ['id', 'password'])

    # check id exist
    if (validator.is_duplicated()):
        login_result = 'Check your inputs'
        validator.validate()
        if (validator.result):
            login_result = 'ID or Password is wrong'
            user = models.User(data['id'], 'None', 'None')
            userinfo = user.get_userinfo()
            password = userinfo['password']

            if (bcrypt.check_password_hash(password, data['password'])):
                login_result = 'OK'
                nickname = userinfo['nickname']
                session['id'] = userinfo['id']
                session['user_id'] = data['id']
                session['nickname'] = nickname

                user.update_user(data['id'], None, "lastlogin")
                user.update_user(data['id'], None, "loginstate")
            
    return jsonify({'result' : login_result})

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    user = models.User(session['id'], 'None', 'None')
    user.update_user(session['id'], None, "loginstate")
    session.pop('id', None)
    session.pop('user_id', None)
    session.pop('nickname', None)

    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # print(data)
        # --> ImmutableMultiDict([('id', '1234123'), ('nickname', '1234123'), ('password', '1234qwer!'), ('password_c', '1234qwer!')])

        data = formdata_to_dict(request.form)
        del data['csrf_token']

        validator = AccountValidator(data)
        validator.validate()

        if (validator.result):
            enc_password = bcrypt.generate_password_hash(data['password'])
            user = models.User(data['id'], data['nickname'], enc_password)
            user.add_user()

        return render_template('register_result.html', result=validator.result)

    elif request.method == "GET":
        params = request.args.to_dict()
        if not params:
            return render_template('access_error.html')

        if params['step'] == "agree":
            return render_template('register_agree.html')
        elif params['step'] == "create":
            if not params['RegisterToken'] or params['RegisterToken'] == "undefined":
                return render_template('access_error.html')

            rc = RegisterCipher()
            try:
                enc = rc.decrypt_str(params['RegisterToken'])
                if (not enc or rc.get_timeover(enc)):
                    return render_template('access_error.html')
                else:
                    return render_template('register_create.html')
            except:
                return render_template('access_error.html')
        else:
            return render_template('404.html')

    else:
        return redirect(url_for('index'))

@app.route('/board', methods = ['GET'])
def board():
    params = request.args.to_dict()
    if not params:
        return redirect(url_for('index'))
    
    NUM_PER_PAGE = 10

    data = {}
    type = params['type']
    page = int(params.get('page', 1))
    boardNum = params.get('boardNum', "")

    if (not boardNum):
        boardNum = None
    else:
        boardNum = int(boardNum)
        if type == 'secret':
            if 'id' in session:
                is_admin = models.Admin(session['id']).check_admin()
                if (not is_admin):
                    return redirect(url_for('board_auth', type=type, page=page, boardNum=boardNum))
            else:
                return redirect(url_for('board_auth', type=type, page=page, boardNum=boardNum))
    
    board = ""
    if type == 'notice':
        board = models.NoticeBoard()
    elif type == 'free':
        board = models.FreeBoard()
    elif type == 'question':
        board = models.QuestionBoard()
    elif type == 'secret':
        board = models.SecretBoard()
    else:
        type = None
    
    if (type is None):
        return render_template('access_error.html')

    total_post_cnt = board.query.count()
    data['post'] = models.get_post(board, (page - 1) * NUM_PER_PAGE, NUM_PER_PAGE, boardNum)
    if (total_post_cnt != 0 and total_post_cnt % NUM_PER_PAGE == 0):
        data['total_page'] = total_post_cnt // NUM_PER_PAGE
    else:
        data['total_page'] = total_post_cnt // NUM_PER_PAGE + 1
  
    data['nickname'] = session.get('nickname', None)

    if (data):
        if (boardNum):
            return render_template('home_detail.html', data=data)
        else:
            return render_template('home_board.html', data=data, type=type)
    else:
        if (boardNum):
            return render_template('access_error.html')
        else:
            return render_template('home_board.html', data=data, type=type)

# for secret board
@app.route('/board_auth', methods=['GET', 'POST'])
def board_auth():
    data = {}
    data['nickname'] = session.get('nickname', None)
    if request.method == 'GET':
        params = request.args.to_dict()
        if 'type' not in params or 'boardNum' not in params:
            return render_template('access_error.html')

        return render_template('home_locked.html', data=data)
    else:
        dict = formdata_to_dict(request.form)

        sb = models.SecretBoard()
        data['post'] = models.get_post(sb, None, None, dict['boardNum'])
        if (data['post']['password'] == dict['postPw']):
            return render_template('home_detail.html', data=data)
        else:
            return render_template('access_error.html')

@app.route('/board_write', methods=['GET', 'POST'])
@login_required
def write():
    if request.method == 'POST':
        data = formdata_to_dict(request.form)
        type = data['boardType'].lower()
        if (not type):
            return redirect(url_for('index'))

        MAX_TITLE_LENGTH = 32;
        MAX_CONTENTS_LENGTH = 300;

        # length validate
        t_len, c_len = map(len, [data['title'], data['contents']])
        if (not t_len or not c_len or t_len > MAX_TITLE_LENGTH or c_len > MAX_CONTENTS_LENGTH):
            return render_template('access_error.html', post_error=True)

        data['writer_id'] = session['id']
        board = ""
        is_update = bool(data.get('boardNum', ""))

        if type == 'notice':
            is_admin = models.Admin(session['id']).check_admin()
            if (is_admin):
                board = models.NoticeBoard(data)
            else:
                return render_template('access_error.html', auth_error=True)
        elif type == 'free':
            board = models.FreeBoard(data)
        elif type == 'question':
            board = models.QuestionBoard(data)
        elif type == 'secret':
            data['password'] = data.get('postPassword')
            board = models.SecretBoard(data)
        
        if (board):
            if is_update:
                board.update_post(data['boardNum'], data)
                return redirect(url_for('board', type=type, page=data['page'], boardNum=data['boardNum']))
            else:
                board.add_post()
                return redirect(url_for('board', type=type, page="1"))
        else:
            return render_template('access_error.html', post_error=True)

    else:
        params = request.args.to_dict()
        if not params:
            return redirect(url_for('index'))

        data = {}
        data['title'] = params.get('title', "")
        data['contents'] = params.get('contents', "")
        data['boardNum'] = params.get('boardNum', "")
        data['page'] = params.get('page', 1)
        data['nickname'] = session.get('nickname', None)

        if params['type'] == 'notice':   
            is_admin = models.Admin(session['id']).check_admin()
            if (not is_admin):
                return render_template('access_error.html', auth_error=True)
            else:
                data['is_admin'] = True

        return render_template('home_write.html', data=data)



@app.route('/getRegisterToken', methods = ['POST'])
def genToken():
    rc = RegisterCipher()
    token = rc.encrypt_str(rc.genTime)
    return jsonify({'token' : token})

@app.route('/checkDuplicated_ID', methods = ['POST'])
def checkID():
    data = formdata_to_dict(request.form)

    validator = AccountValidator(data, ['id'])
    validator.validate()
    return jsonify({'result' : str(validator.result)})

@app.route('/deletePost', methods=['POST'])
@login_required
def delete_post():
    data = formdata_to_dict(request.form)
    type = data['type']
    board = ""
    result = "You are not this post owner"

    if type == 'notice':
        is_admin = models.Admin(session['id']).check_admin()
        if (is_admin):
            board = models.NoticeBoard()
    elif type == 'free':
        board = models.FreeBoard()
    elif type == 'question':
        board = models.QuestionBoard()
    elif type == 'secret':
        board = models.SecretBoard()
    
    if (board):
        post = board.query.filter_by(id = data['boardNum']).first()
        if (post is None):
            result = "This post is not exist"
        else:
            post_owner = post.writer_id
            if (post_owner == session['id']):
                result = "OK"
                board.delete_post(data['boardNum'])
        
    return jsonify({'result' : result})

        


if __name__ == '__main__':
    csrf = CSRFProtect()
    csrf.init_app(app)
    models.db.init_app(app)
    # models.db.create_all(app=app)
    
    app.run(port=5000)
    
