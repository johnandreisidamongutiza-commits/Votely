from flask import Flask
from datetime import timedelta

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password':'',
    'database':'vsystem_db',
    'auth_plugin':'mysql_native_password'
}

def reg_app():
    app = Flask(__name__)
    app.secret_key = 'Secret'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    from voting_system.Authentication.login import auth
    from voting_system.Admin.admin import admin
    from voting_system.User.user import user
    from voting_system.SuperAdmin.superadmin import superadmin
    
    app.register_blueprint(auth)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(superadmin, url_prefix='/superadmin')
    
    return app
