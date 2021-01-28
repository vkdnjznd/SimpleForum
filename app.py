# -*- coding: utf-8 -*
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_wtf.csrf import CSRFProtect, validate_csrf
from flask_bcrypt import Bcrypt
from register_security import *
from schema import models


def formdata_to_dict(data):
    data = {name: key for name, key in data.items()}
    return data

# define and settings app
def create_app():
    app = Flask(__name__)
    APP_SECRET_KEY = "APP_SECRET_KEY"
    
    app.config['SECRET_KEY'] = APP_SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://forum_admin:1234@localhost:3306/forum"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BCRYPT_LEVEL'] = 10
    
    return app


app = create_app()
bcrypt = Bcrypt(app)
csrf = CSRFProtect()
csrf.init_app(app)
models.db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template('home.html')
    else:
        data = request.form
        print(data)
        return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # print(data)
        # --> ImmutableMultiDict([('id', '1234123'), ('nickname', '1234123'), ('password', '1234qwer!'), ('password_c', '1234qwer!')])

        data = formdata_to_dict(request.form)
        del data['csrf_token']

        validator = RegisterValidator(data)
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
            return render_template('access_error.html')

    else:
        return redirect(url_for('index'))

@app.route('/getRegisterToken', methods = ['POST'])
def genToken():
    rc = RegisterCipher()
    token = rc.encrypt_str(rc.genTime)
    return jsonify({'token' : token})

@app.route('/checkDuplicated_ID', methods = ['POST'])
def checkID():
    data = request.form
    data = formdata_to_dict(data)

    validator = RegisterValidator(data, ['id'])
    validator.validate()
    return jsonify({'result' : str(validator.result)})


@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        return render_template('write.html')
    else:
        return render_template('write.html')

if __name__ == '__main__':
    app.run(port=5000)