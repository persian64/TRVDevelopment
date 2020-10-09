# TRV Website Development (Discontinued)
This project was about creating a website for a research community that no longer exists.

The project has been shared on Github so people can learn from it, you are free to distribute, share and make changes to this code. You don't necessary need to pass the credit to me but there is nothing to stop you from doing so. 

I would love to hear from you, please let me know about tips, tricks and methodologies you think I should use; besides that if you would like to start and maintain such a community, you are free to do so.

### Features
- Sign up
- Sign in
- Blog (CRUD)
  - Create 
  - Read 
  - Update 
  - Delete
  - Rich Text editor included 
- Reset password 
- Email verification
- Invitation token
  - creation
  - verification 
- User data update
  - password
  - email
  - username 
- Uitlity functions
  - Validate email 
  - Validate username 
  - Validate password 
  - Get user's IP 
  - Generate random set of characters 
  
### Bad Practices 
- HTML code has been reused for navbar:
  - There is a solution to create a block in jinja2 with ```{% block navbar %} <nav> {% endblock %}``` and then use that whenever you want a navbar but that solution just doesn't work here.
- Too many CSS files
  - There is just too many CSS files that makes the website's design very hard to maintain, currently only I know what's going on, unfortunetly this part of the project is not easy to be used by others.
- The front-end was not designed for mobile users
  - Although it works fine or seems to work fine on iPad and similar devices.

### Vulnerabilities
This application has not been tested and I am not planning to test it but from what I can read in source code, these vulnerabilities are to be found:
- Stored XSS in blog 
- Remote command execution in thumbnail file upload for blog 
- Service side template injection
- Insecure direct object reference 

These vulnerabilities should be present because I haven't add anything to prevent them yet, you should take the code to practice:
- how flask works 
- study the features listed above 
- find these vulnerabilities and may be fix them

## How to use this application?
I have written this application to be as simple as possible, I didn't make use of Flask blueprints because from my point of view they can turn a project into a puzzle-box, the code might not seem structured and that's the reason but it was created for the next developer after me, I have followed the best-practices and made it very clear what each function does, I didn't use variable like x, y, i. 
If you faced any problems, feel free to contact me.


Here is app.py file with comments:
```
# Import the necessary files
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

# These are standard config variable and are very easy to understand
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

# mail settings
# change this according to your needs 
trv.config['MAIL_SERVER']= "mail.privateemail.com"
trv.config['MAIL_PORT'] = 587
trv.config['MAIL_USE_TLS'] = True
trv.config['MAIL_USE_SSL'] = False
trv.config['MAIL_USERNAME'] = "no-reply@researchersvalley.org"
trv.config['MAIL_PASSWORD'] = config.email_password             # this is the password, it's a best practice to always store sensitive stuff elsewhere 
mail = Mail(trv)

trv.url_map.strict_slashes = False              # helps to defeat the problem of automatic redirects like /signup (exists) > /signup/ (doesn't exist) 

login = LoginManager(trv)
# when we try to visit a page that requires us to login, we get redirected to the login view function
login.login_view = 'login'
login.session_protection = 'strong'

# CSRF protection for the entire application 
csrf = CSRFProtect(trv)
csrf.init_app(app=trv)

db = SQLAlchemy(trv)
migrate = Migrate(trv, db)

# this function is used to sign out a user if they are logged in for more than 6 hours without selecting "Remember me" on login
@trv.before_request
def before_request():
    flask.session.permanent = True
    trv.permanent_session_lifetime = timedelta(hours=6)      # if the member doesn't select remember me, we still kick them!


from application import views, models

if __name__ == '__main__':
    trv.run()

```

