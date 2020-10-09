from app import trv, db
import flask
from application.models import Users, Invitations, Posts
from flask_login import current_user, login_user, logout_user, login_required, fresh_login_required
from werkzeug.urls import url_parse
from utilities.get_ip import get_ip
from utilities.validate_email import validate_email
from utilities.validate_username import validate_username
from utilities.validate_password import validate_password
from utilities.generate_random_password import gen_password
from application.activation_token import generate_confirmation_token, confirm_token
from datetime import datetime
from application.email import send_email
from utilities.generate_invite_code import gen_invite_code
from base64 import b64encode
from sqlalchemy import desc



@trv.route('/')
def index():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('home'))
    latest_posts = Posts.query.order_by(desc(Posts.time)).limit(6)
    return flask.render_template('./index.html', latest_posts=latest_posts)


@trv.route('/blog')
def blog():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('home'))
    post_page = flask.request.args.get('page', type=int, default=1)
    posts_per_page = Posts.query.order_by(desc(Posts.time)).paginate(per_page=6, page=post_page, error_out=True)

    return flask.render_template('./main/blog.html', posts=posts_per_page)


@trv.route('/about')
def about():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('home'))
    return flask.render_template('./main/about.html')

@trv.route('/responsible-disclosure')
def bug_hunting():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('home'))
    return flask.render_template('./main/security_program.html')


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
            new_user = Users(username=member_username, email=member_email, invitation_code=invitation_code, ip_address=get_ip(),
                             account_confirmed=False, user_agent=flask.request.headers.get('User-Agent'))
            new_user.set_password(member_password)
            #valid_token.expired = True                      # to specify that an invitation has expired
            db.session.add(new_user)
            db.session.commit()

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


@trv.route('/confirm/<token>')
def confirm_email(token):
    if current_user.is_authenticated:
        flask.flash("Email confirmation succeed.")
        return flask.redirect(flask.url_for('user_settings'))

    email = confirm_token(token=token)
    user = Users.query.filter_by(email=email).first()

    if user is None:
        flask.flash("The confirmation link is invalid or has expired.")
        return flask.redirect(flask.url_for('login'))

    if user.account_confirmed == True:
        flask.flash("The account is already activated, please login.")
        return flask.redirect(flask.url_for('login'))

    if user.account_confirmed == False:
        user.account_confirmed = True
        user.confirmed_on = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flask.flash("Your account has been activated, you can login now.")
        return flask.redirect(flask.url_for('login'))

    return flask.render_template("./main/member_login.html")


@trv.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('home'))

    if flask.request.method == 'POST':
        member_email = flask.request.form['member_email']
        user = Users.query.filter_by(email=member_email).first()

        # Check if the email is allowed:
        if validate_email(member_email) == False:
            flask.flash("You can't use that email here, sorry.")
            return flask.redirect(flask.url_for('reset_password'))

        # check if the account is activated:
        if user.account_confirmed == False:
            flask.flash("You must first activate your account, please check your email.")
            return flask.redirect(flask.url_for('reset_password'))

        if user is None:
            flask.flash("That email doesn't exist!")
            return flask.redirect(flask.url_for('reset_password'))

        if user is not None:
            new_pass = gen_password()
            html = flask.render_template("./mail_messages/password_reset_token.html", new_pass=new_pass)
            subject = "Reset your password"
            send_email(user.email, subject, html)
            user.set_password(new_pass)
            db.session.commit()

        else:
            flask.flash("Something went wrong, please try again.")
            return flask.redirect(flask.url_for('reset_password'))

    return flask.render_template('./main/password_reset.html')


@trv.errorhandler(404)
def not_found_404(e):
    return flask.render_template('./misc/4xx.html'), 404

@trv.errorhandler(500)
def internal_server_error(e):
    return flask.render_template('./misc/5xx.html'), 500

@trv.errorhandler(401)
def not_found_404(e):
    return 401


"""
The following code defines view functions for the pages after when you are logged in
All of these require the user to be logged in!
"""
@trv.route('/home')
@login_required
def home():
    current_user_posts = Posts.query.order_by(desc(Posts.time)).filter_by(post_author=current_user.username).limit(6)
    curr_user_total_posts = Posts.query.order_by(desc(Posts.time)).filter_by(post_author=current_user.username).all()

    members_posts = Posts.query.order_by(desc(Posts.time)).limit(6)
    total_member_posts = Posts.query.order_by(desc(Posts.time)).all()

    return flask.render_template('./logged_in/index.html', current_user_posts=current_user_posts,
                                 curr_user_total_posts=len(curr_user_total_posts),
                                 members_posts=members_posts, total_member_posts=len(total_member_posts))


@trv.route('/blog/posts')
@login_required
def members_posts():
    post_page = flask.request.args.get('page', type=int, default=1)
    posts_per_page = Posts.query.order_by(desc(Posts.time)).paginate(per_page=12, page=post_page, error_out=True)

    return flask.render_template('./logged_in/blog/others_posts.html', posts=posts_per_page)


@trv.route('/blog/my-posts')
@login_required
def currUsrPosts():
    post_page = flask.request.args.get('page', type=int, default=1)
    posts_per_page = Posts.query.order_by(desc(Posts.time)).filter_by(post_author=current_user.username).paginate(per_page=12, page=post_page, error_out=True)

    return flask.render_template('./logged_in/blog/my_posts.html', posts=posts_per_page)


@trv.route('/generate-invite-code', methods=['GET', 'POST'])
@login_required
def gen_invite():
    user_data = Users.query.filter_by(username=current_user.username).first()

    invitations = Invitations.query.all()
    used_tokens = Users.query.order_by(Users.invitation_code).first()
    print(used_tokens)
    token_status = ''
    if used_tokens in invitations:
        token_status += 'Expired'
    if not used_tokens in invitations:
        token_status += 'Not Used'

    if flask.request.method == 'POST':
        member_confirmation = flask.request.form.get('member_confirmation')
        user_data = Users.query.filter_by(username=current_user.username).first()

        if user_data.check_password(member_confirmation) and member_confirmation != '':
            curr_user = Users.query.filter_by(username=current_user.username).first()
            create_invite = Invitations(invitation_code=gen_invite_code(), creator=curr_user)
            db.session.add(create_invite)
            db.session.commit()
            flask.flash("You just created an invite code.")
            flask.redirect(flask.url_for('gen_invite'))

        else:
            flask.flash("Something went wrong, check your password or contact us at discord.")
    return flask.render_template('./logged_in/gen_invite.html', all_codes=user_data.created_invitations, token_status=token_status)


@trv.route('/settings', methods=['GET', 'POST'])
@login_required
@fresh_login_required
def user_settings():
    if flask.request.method == 'POST':

        # Check password now:
        current_pass = flask.request.form['current_password']
        user_data = Users.query.filter_by(username=current_user.username).first()

        if not user_data.check_password(current_pass) or current_pass == '':
            flask.flash("Please confirm that you entered the correct current password.")
            return flask.redirect(flask.url_for('user_settings'))


        # Check username now:
        new_username = flask.request.form.get('new_username')
        curr_user = Users.query.filter_by(username=new_username).first()

        if new_username != '':
            if validate_username(new_username) == False:
                flask.flash("Usernames should be between 6-16 characters, contain letters, digits, underscore and dots.")
                return flask.redirect(flask.url_for('user_settings'))

            if new_username == current_user.username:
                flask.flash("That username is your current username")
                return flask.redirect(flask.url_for('user_settings'))

            if curr_user is not None:
                flask.flash("Sorry, that username is in use.")
                return flask.redirect(flask.url_for('user_settings'))

            if validate_username(new_username) == True:
                user_data.username = new_username
                db.session.commit()
                flask.flash("Your username has been changed.")
                return flask.redirect(flask.url_for('user_settings'))


        # Check email now:
        new_email = flask.request.form.get('new_email')
        curr_email = Users.query.filter_by(email=current_user.email).first()
        user_data = Users.query.filter_by(email=new_email).first()

        if new_email != '':
            if validate_email(new_email) == False:
                flask.flash("You can't use that email here, sorry.")
                return flask.redirect(flask.url_for('user_settings'))

            if new_email == current_user.username:
                flask.flash("That email is your current email")
                return flask.redirect(flask.url_for('user_settings'))

            if user_data is not None:
                flask.flash("Sorry, that email is in use.")
                return flask.redirect(flask.url_for('user_settings'))

            if validate_email(new_email) == True:
                curr_email.email = new_email
                curr_email.account_confirmed = False
                db.session.commit()

                token = generate_confirmation_token(curr_email.email)
                confirm_url = flask.url_for('confirm_email', token=token, _external=True)
                html = flask.render_template('./mail_messages/account_activation.html', confirm_url=confirm_url)
                subject = 'Please confirm your email'
                send_email(curr_email.email, subject, html)
                flask.flash("Your email address has been changed, please confirm your account.")
                return flask.redirect(flask.url_for('user_settings'))


        # Change password now:
        new_password = flask.request.form.get('new_password')
        confirm_password = flask.request.form.get('confirm_password')
        user_data = Users.query.filter_by(username=current_user.username).first()

        if new_password != '':

            if validate_password(new_password) == False:
                flask.flash(f"""That password is weak, use this instead: {gen_password()}""")
                return flask.redirect(flask.url_for('user_settings'))

            if new_password != confirm_password:
                flask.flash("Make sure your passwords match.")
                return flask.redirect(flask.url_for('user_settings'))

            if new_password == confirm_password:
                user_data.set_password(new_password)
                db.session.commit()
                flask.flash("Your password has been changed.")
                return flask.redirect(flask.url_for('user_settings'))

    return flask.render_template('./logged_in/account/settings.html')


@trv.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    if flask.request.method == "POST":
        post_title = flask.request.form['post_title']
        post_thumbnail = flask.request.files.get('post_thumbnail')
        post_text = flask.request.form['user_post']

        if post_title == '':
            flask.flash("You cannot leave post title empty, go back and change that")
            return flask.redirect(flask.url_for('create_post'))

        if post_text == '' or len(post_text) < 120:
            flask.flash("Make sure the post is not empty or is not less than 120 characters.")
            return flask.redirect(flask.url_for('create_post'))

        post_creator = Users.query.filter_by(username=current_user.username).first()
        post_url = f"{datetime.now().strftime('%H-%M-%S-%b-%d-%Y')}-{post_title.replace(' ', '-')}"

        save = Posts(post_title=post_title, post_thumbnail=post_thumbnail.read(), thumbnail_name=post_thumbnail.filename,
                     post_text=post_text, post_url=post_url, creator=post_creator, creation_date=datetime.now().strftime('%H-%M-%S-%b-%d-%Y'),
                     post_author=current_user.username, post_about=post_text[:120])
        db.session.add(save)
        db.session.commit()
        flask.flash("You just created a post.")
        return flask.redirect(flask.url_for('currUsrPosts'))

    return flask.render_template('./logged_in/blog/blog.html')


@trv.route('/blog/posts/<post_url>/delete')
@login_required
def delete_post(post_url):
    post = Posts.query.filter_by(post_url=post_url).first()
    db.session.delete(post)
    db.session.commit()
    flask.flash("The post has been deleted successfully!")

    return flask.redirect(flask.url_for('currUsrPosts'))


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


@trv.route('/blog/posts/<post_url>')
def view_post(post_url):
    get_post = Posts.query.filter_by(post_url=post_url).first()
    get_author_posts = Users.query.filter_by(username=get_post.post_author).first()
    posts_by_others = Posts.query.all()

    return flask.render_template("./logged_in/blog/post.html", show_post=get_post.post_text, show_title=get_post.post_title,
                                 show_image=b64encode(get_post.post_thumbnail).decode("utf8"), post_title=get_post.post_title,
                                 post_author=get_post.post_author, list_author_posts=get_author_posts.created_posts,
                                 post_creation_date=get_post.creation_date, list_others_posts=posts_by_others)


@trv.route('/logout')
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for('index'))
