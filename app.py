import flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import timedelta
from flask_mail import Mail
from configs import config
from flask_wtf.csrf import CSRFProtect



trv = flask.Flask(__name__)
#mail = Mail(trv)

trv.config["SECRET_KEY"] = '(Th"E{p)wwv-=!QE/{$d>S`|x!L)+Qj_QhK(#~atA^{u>ixI;>_eXkC(1@?D!D4Xw'
trv.config["SECURITY_PASSWORD_SALT"] = ')+Qj_QhK(#~atA^{u>ixI;'
trv.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.db')
trv.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
trv.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
trv.config['WTF_CSRF_ENABLED'] = True

# google reCaptcha configs:
trv.config['RECAPTCHA_PUBLIC_KEY'] = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
trv.config['RECAPTCHA_PRIVATE_KEY'] = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
trv.config['RECAPTCHA_OPTIONS'] = {'theme': 'black'}
trv.config['RECAPTCHA_USE_SSL'] = False

# mail settings:
trv.config['MAIL_SERVER']= "mail.privateemail.com"
trv.config['MAIL_PORT'] = 587
trv.config['MAIL_USE_TLS'] = True
trv.config['MAIL_USE_SSL'] = False
trv.config['MAIL_USERNAME'] = "no-reply@researchersvalley.org"
trv.config['MAIL_PASSWORD'] = config.email_password
mail = Mail(trv)


trv.url_map.strict_slashes = False              # helps to defeat the problem of automatic redirects

login = LoginManager(trv)
# when we try to visit a page that requires us to login, we get redirected to the login view function
login.login_view = 'login'
login.session_protection = 'strong'

csrf = CSRFProtect(trv)
csrf.init_app(app=trv)

db = SQLAlchemy(trv)
migrate = Migrate(trv, db)

@trv.before_request
def before_request():
    flask.session.permanent = True
    trv.permanent_session_lifetime = timedelta(hours=6)      # if the member doesn't select remember me, we still kick them!


from application import views, models


if __name__ == '__main__':
    trv.run()

