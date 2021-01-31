from flask import Flask

def formdata_to_dict(data):
    data = {key: value for key, value in data.items()}
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