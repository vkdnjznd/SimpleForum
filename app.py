# -*- coding: utf-8 -*
from flask import Flask, json, render_template, request, redirect, url_for, session, jsonify
from flask_wtf.csrf import CSRFProtect, validate_csrf
from flask_bcrypt import Bcrypt
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


@app.route('/', methods=['GET'])
def index():
    if 'nickname' in session:
        return render_template('home.html', nickname=session['nickname'])
    else:
        return render_template('home.html')

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
                session['id'] = data['id']
                session['nickname'] = nickname
                user.update_user(data['id'], None, "lastlogin")
                user.update_user(data['id'], None, "loginstate")
            
    return jsonify({'result' : login_result})

@app.route('/logout', methods=['GET'])
def logout():
    user = models.User(session['id'], 'None', 'None')
    user.update_user(session['id'], None, "loginstate")
    session.pop('id', None)
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


@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        return render_template('write.html')
    else:
        return render_template('write.html')

if __name__ == '__main__':
    csrf = CSRFProtect()
    csrf.init_app(app)
    models.db.init_app(app)

    app.run(port=5000)