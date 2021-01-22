# -*- coding: utf-8 -*
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
from register_security import *

app = Flask(__name__)

# Mysql Connect information
def get_connection():
    conn = pymysql.connect(host = 'localhost', user = 'test', password = '1234', db = 'mydb', charset = 'utf8')
    return conn

def check_id_db(id):
    conn = get_connection()
    curs = conn.cursor()

    sql = "select id from user_tb where id = (%s)"
    curs.execute(sql, (id))
    rows = curs.fetchall()

    conn.close()

    if (len(rows) == 0):
        return False
    else:
        return True

def insert_data(data):
    conn = get_connection()
    curs = conn.cursor()

    sql = "insert into user_tb(id, password) values (%s, %s)"
    curs.execute(sql, (data['id'], data['password']))

    conn.commit()
    conn.close()

def check_login(data):
    conn = get_connection()
    curs = conn.cursor()

    err_msg = ""
    if (check_id_db(data['id'])):
        sql = "select password from user_tb where id = (%s)"
        curs.execute(sql, data['id'])
        password = curs.fetchone()
        conn.close()

        if password[0] == data['password']:
            return err_msg
        else:
            err_msg = "비밀번호가 틀립니다."
            return err_msg
    else:
        conn.close()
        err_msg = "아이디가 존재하지 않습니다."
        return err_msg

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
        data = request.form
        # print(data)
        # --> ImmutableMultiDict([('agree_1', 'on'), ('agree_2', 'on')])

        if (data['agree_1'] == 'on' and data['agree_2'] == 'on'):
            # Generate Key..
            return render_template('register_agree.html')

        if (data['password'] != data['c_password']):
            return render_template('register_create.html')    
        else:
            insert_data(data)
            return redirect(url_for('index'))
    
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
            enc = rc.decrypt_str(params['RegisterToken'])
            try:
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


@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        return render_template('write.html')
    else:
        return render_template('write.html')

if __name__ == '__main__':
    app.run(port=5000)
