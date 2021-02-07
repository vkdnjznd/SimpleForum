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
    post_list = [nb.get_post(0, 3), fb.get_post(0, 3), qb.get_post(0, 3), sb.get_post(0, 3)]

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
    
    if type == 'notice':
        nb = models.NoticeBoard()
        data['post'] = nb.get_post((page - 1) * NUM_PER_PAGE, NUM_PER_PAGE, boardNum)
    elif type == 'free':
        fb = models.FreeBoard()
        data['post'] = fb.get_post((page - 1) * NUM_PER_PAGE, NUM_PER_PAGE, boardNum)
    elif type == 'question':
        qb = models.QuestionBoard()
        data['post'] = qb.get_post((page - 1) * NUM_PER_PAGE, NUM_PER_PAGE, boardNum)
    elif type == 'secret':
        sb = models.SecretBoard()
        data['post'] = sb.get_post((page - 1) * NUM_PER_PAGE, NUM_PER_PAGE, boardNum)
    else:
        type = None
    
    if (type is None):
        return render_template('access_error.html')

    if (data):
        data['nickname'] = session.get('nickname', None)
        if (boardNum):
            return render_template('home_detail.html', data=data)
        else:
            return render_template('home_board.html', data=data, type=type)
    else:
        if (boardNum):
            return render_template('access_error.html')
        else:
            return render_template('home_board.html', type=type)

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

        # add writer in session id
        if 'id' in session.keys():
            data['writer_id'] = session.get('id')
        else:
            return redirect(url_for('board', type="notice", page="1"))

        if type == 'notice':
            is_admin = models.Admin(session['id']).check_admin()
            if (is_admin):
                nb = models.NoticeBoard(data)
                nb.add_post()
            else:
                return render_template('access_error.html', auth_error=True)
        elif type == 'free':
            fb = models.FreeBoard(data)
            fb.add_post()
        elif type == 'question':
            qb = models.QuestionBoard(data)
            qb.add_post()
        elif type == 'secret':
            data['password'] = data.get('postPassword', 1234) # default password 1234
            sb = models.SecretBoard(data)
            sb.add_post()
        else:
            type = None

        return redirect(url_for('board', type=type, page="1"))
    else:
        params = request.args.to_dict()
        if not params:
            return redirect(url_for('index'))

        data = {}
        if params['type'] == 'notice':   
            is_admin = models.Admin(session['id']).check_admin()
            if (not is_admin):
                return render_template('access_error.html', auth_error=True)
            else:
                data['is_admin'] = True

        data['nickname'] = session.get('nickname', None)
        return render_template('home_write.html', data=data)

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
        data['post'] = sb.get_post(None, None, dict['boardNum'])
        if (data['post']['password'] == dict['postPw']):
            return render_template('home_detail.html', data=data)
        else:
            return render_template('access_error.html')


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


if __name__ == '__main__':
    csrf = CSRFProtect()
    csrf.init_app(app)
    models.db.init_app(app)
    models.db.create_all(app=app)

    app.run(port=5000)
