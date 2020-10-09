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
```py
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


Singup:
```py 
@trv.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('home'))
    if flask.request.method == 'POST':
        member_username = flask.request.form['member_username']
        member_email = flask.request.form['member_email']
        member_password = flask.request.form['member_passwd']
        repeat_password = flask.request.form['repeat_password']
        invitation_code = flask.request.form['invitation_code']
        existing_username = Users.query.filter_by(username=member_username).first()
        existing_email = Users.query.filter_by(email=member_email).first()

        # Check if the email is allowed:
        if validate_email(member_email) == False:
            flask.flash("You can't use that email here, sorry.")
            return flask.redirect(flask.url_for('signup'))

        # Check if username is allowed:
        if validate_username(member_username) == False:
            flask.flash("Usernames should be between 6-16 characters, contain letters, digits, underscore and dots.")
            return flask.redirect(flask.url_for('signup'))


        # Check if email or username is in use
        if existing_username or existing_email is not None:
            flask.flash("The email or username is in use.")
            return flask.redirect(flask.url_for('signup'))

        # Ensure the password is strong
        if validate_password(member_password) == False:
            flask.flash(f"""That password is weak, use this instead: {gen_password()}""")
            return flask.redirect(flask.url_for('signup'))

        # Ensure the password and repeat password match
        if member_password != repeat_password:
            flask.flash("Passwords didn't match, please try again.")
            return flask.redirect(flask.url_for('signup'))

        valid_token = Invitations.query.filter_by(invitation_code=invitation_code).first()
        # Check if the provided invitation_code is in Invitations table
        if  valid_token is not None:
            # Writes form data to Users table 
            new_user = Users(username=member_username, email=member_email, invitation_code=invitation_code, ip_address=get_ip(),
                             account_confirmed=False, user_agent=flask.request.headers.get('User-Agent'))
            new_user.set_password(member_password)
            #valid_token.expired = True                      # to specify that an invitation has expired
            db.session.add(new_user)
            db.session.commit()
            # Sends email verification to user's email 
            token = generate_confirmation_token(new_user.email)
            confirm_url = flask.url_for('confirm_email', token=token, _external=True)
            html = flask.render_template('./mail_messages/account_activation.html', confirm_url=confirm_url)
            subject = 'Please confirm your email'
            send_email(new_user.email, subject, html)

            flask.flash("Singup was succeed, please check your email for account activation.")
            return flask.redirect(flask.url_for('login'))
        else:
            flask.flash("Something went wrong, please try again.")
            return flask.redirect(flask.url_for('signup'))
    return flask.render_template('./main/member_signup.html')
```

Login:
```py
@trv.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('home'))
    if flask.request.method == 'POST':
        member_username = flask.request.form['member_username']
        member_password = flask.request.form['member_password']
        remember_me = flask.request.form.get('remember_me')
        existing_user = Users.query.filter_by(username=member_username).first()

        # if username is not in use or the given password does not match the hash stored in database : if no username or wrong password
        if existing_user is None or not existing_user.check_password(member_password):
            flask.flash('Invalid username or password')
            return flask.redirect(flask.url_for('login'))

        # check if the account is activated:
        if existing_user.account_confirmed == False:
            flask.flash("You must first activate your account, please check your email or click here to resend email.")
            return flask.redirect(flask.url_for('login'))

        # check if the user is logging in from the user-agent/IP address that they registered with or last logged in:
        """
        if existing_user.ip_address != get_ip() or existing_user.user_agent != flask.request.headers.get('User-Agent'):
            flask.flash("It seems like you are logging from an unrecognized location or device, as a security precaution we have locked this account down. "
                        "To unlock the account, please check your email.")
            return flask.redirect(flask.url_for('login'))
        """

        if existing_user:
            login_user(existing_user, remember=remember_me)

        else:
            flask.flash("Something went wrong, please try again.")
            return flask.redirect(flask.url_for('login'))
        # todo: if the user visits a protected page, they are required to login, but after the login, the user should be redirected to that protected page
        next_page = flask.request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = flask.url_for('home')
        return flask.redirect(next_page)
    return flask.render_template('./main/member_login.html')
```

Blog - Create post:
```py 
@trv.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    if flask.request.method == "POST":
        post_title = flask.request.form['post_title']
        post_thumbnail = flask.request.files.get('post_thumbnail')
        post_text = flask.request.form['user_post']

        # checks if the post title is empty 
        if post_title == '':
            flask.flash("You cannot leave post title empty, go back and change that")
            return flask.redirect(flask.url_for('create_post'))

        # checks if the post_text is empty of it's length is less than 120 characters
        # note: this counts the HTML characters or the source code of summernote, not the actual data!
        if post_text == '' or len(post_text) < 120:
            flask.flash("Make sure the post is not empty or is not less than 120 characters.")
            return flask.redirect(flask.url_for('create_post'))

        post_creator = Users.query.filter_by(username=current_user.username).first()
        post_url = f"{datetime.now().strftime('%H-%M-%S-%b-%d-%Y')}-{post_title.replace(' ', '-')}"
        
        # Writes post to Posts table
        save = Posts(post_title=post_title, post_thumbnail=post_thumbnail.read(), thumbnail_name=post_thumbnail.filename,
                     post_text=post_text, post_url=post_url, creator=post_creator, creation_date=datetime.now().strftime('%H-%M-%S-%b-%d-%Y'),
                     post_author=current_user.username, post_about=post_text[:120])
        db.session.add(save)
        db.session.commit()
        flask.flash("You just created a post.")
        return flask.redirect(flask.url_for('currUsrPosts'))

    return flask.render_template('./logged_in/blog/blog.html')
```

Blog - Edit post:
```py 
@trv.route('/blog/posts/<post_url>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_url):
    post = Posts.query.filter_by(post_url=post_url).first()

    if flask.request.method == 'POST':

        post_title = flask.request.form['post_title']
        post_thumbnail = flask.request.files.get('post_thumbnail')
        post_text = flask.request.form['user_post']

        if post_title == '':
            flask.flash("You cannot leave post title empty, go back and change that")
            return flask.redirect(flask.url_for('edit_post'))

        if len(post_title) > 150:
            flask.flash("You cannot add more than 150 characters in your post title!")
            flask.flash("You cannot ")

        if post_text == '' or len(post_text) < 120:
            flask.flash("Make sure the post is not empty or is not less than 120 characters.")
            return flask.redirect(flask.url_for('edit_post'))

        post_creator = Users.query.filter_by(username=current_user.username).first()
        post_url_ = f"{post.creation_date}-{post_title.replace(' ', '-')}"

        # todo: something's messged up here, fix it
        db.session.delete(post)
        update = Posts(post_title=post_title, post_thumbnail=post_thumbnail.read(), thumbnail_name=post_thumbnail.filename,
                     post_text=post_text, creator=post_creator, post_author=current_user.username, post_about=post_text[:120],
                       creation_date=post.creation_date)
        update.post_url = post_url_
        db.session.commit()

        flask.flash("Your post was updated.")
        return flask.redirect(flask.url_for('currUsrPosts'))

    return flask.render_template('./logged_in/blog/edit_blog.html', post_title=post.post_title, post_thumbnail=post.post_thumbnail,
                                 post_text=post.post_text)
```



























