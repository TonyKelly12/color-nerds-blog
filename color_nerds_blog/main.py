'''
Created on Jan 31, 2017

@author: toned_000
'''
import os
import random
import re
import cgi
import urllib
import webapp2
import jinja2
import hmac
import time
import hashlib
import random
from functools import wraps
from string import letters
from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

secret = 'UwDx^YBPG8@5&mQY'


#### Global Functions #####
def gen_id():
    u_id = str(random.uniform(0, 1))
    return u_id


# this function is for rendering
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


# this function adds the secret to hash & value
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


# this function check to see if the seceret + val == hash
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


# this function creats a random salt
def sprinkle_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


# this function hash's the password
def make_pw_hash(username, pw, salt=None):
    if not salt:
        salt = sprinkle_salt()
    h = hashlib.sha256(username + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


# I think this function checks that the pwrd matches the hash
def valid_pw(username, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(username, password, salt)


# this function builds the user key
def user_key(group='default'):
    return ndb.Key('User', 'group')


# this function builds the post key
def post_key(group='default'):
    return ndb.Key('Post', group, parent=user_key)


# this function builds the comment key
def comment_key(group='default'):
    return ndb.Key('Comment', group, parent=post_key)


def login_required(f):
    @wraps(f)
    def wrap(self, *a, **kw):
        if self.user:
            # print User.session
            return f(self, *a, **kw)
        else:
            return self.redirect('/login')

    return wrap


def p_edit_auth(f):
    @wraps(f)
    def wrap(self, *a, **kw):
        if self.user.username == Post.username:
            return f(self, *a, **kw)

    return wrap


def c_edit_auth(f):
    @wraps(f)
    def wrap(self, *a, **kw):
        if self.user.username == Comment.username:
            return f(self, *a, **kw)

    return wrap







    ##### Main WEbApp Handler + Render funcions #####


class Handler(webapp2.RequestHandler):
    # basic render function pt1
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # basic render function pt2
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    # basic render function pt3
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    # this function sets the cookie
    def set_cookie(self, username, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (username, cookie_val)
        )

    # this function reads the cookie
    def read_cookie(self, username):
        cookie_val = self.request.cookies.get(username)
        return cookie_val and check_secure_val(cookie_val)

    # this function logs user in
    def login(self, user):
        self.set_cookie('user_id', str(user.key.id()))

    # this function logs user out
    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    # this function checks for valid cookie for returning user
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


# global render function for entire post
def render_post(response, post, comment):
    response.out.write('<b>' + Post.title + '</b><br>')
    response.out.write(post.content)
    response.out.write(comment.comments)


def render_comment(response, comment):
    response.out.write(Comment.comments)


####User Data Base#######

class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)

    # this method allows lookup by id for user class
    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent=user_key())

    # this method allows lookup by name for user class
    @classmethod
    def by_name(cls, username):
        u = cls.query().filter(cls.username == username).get()
        return u

    # this method creates user but does not store in db
    @classmethod
    def register(cls, username, pw):
        pw_hash = make_pw_hash(username, pw)

        return cls(parent=user_key(),
                   username=username,
                   pw_hash=pw_hash,
                   )

    # this method validates login of user
    @classmethod
    def login(cls, username, pw):
        u = cls.by_name(username)
        if u and valid_pw(username, pw, u.pw_hash):
            return u


##### Post DataBase ###
class Post(ndb.Model):
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_mod = ndb.DateTimeProperty(auto_now=True)
    username = ndb.StringProperty(required=True)
    likes = ndb.IntegerProperty(required=True, default=0)

    # this method allows lookup by id for user class
    @classmethod
    def by_id(cls, pid):
        return cls.get_by_id(pid, parent=post_key())

    # this method allows lookup by name for user class
    @classmethod
    def by_title(cls, title):
        p = cls.query().filter(cls.title == title).get()
        return p

    # this functions adds line breaks in post content

    def render(self):  # NOT Working
        self._render_text = self.content.replace('<br>', '\n')
        return render_str("post.html", p=self)

    def like_count(self):
        self.like = self.like + 1
        return self.like









        ##### Comment DataBase #####


class Comment(ndb.Model):
    comments = ndb.StringProperty(required=True)
    username = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_mod = ndb.DateTimeProperty(auto_now=True)
    post_id = ndb.IntegerProperty(required=True)

    # this functions adds line breaks in post content
    @classmethod
    def by_id(cls, cid):
        return cls.get_by_id(cid, parent=comment_key())

    def render(self):
        self._render_text = self.comments.replace('\n', '<br>')  # NOT Working
        return render_str("comment.html", c=self)

        # Post Page Permalink #


class Likes(ndb.Model):
    username = ndb.StringProperty(required=True)
    post_id = ndb.IntegerProperty(required=True)





    ###  Main Index  ###


class Index(Handler):
    def render_front(self):
        posts = Post.query().order(-Post.created).fetch(3)
        if self.user:
            self.render("main.html", posts=posts, username=self.user.username)
        else:
            self.render("main.html", posts=posts)

    def get(self):
        self.render_front()


# Builds blogs key

def blog_key(name='post', parent=user_key):
    return ndb.Key('blogs', name)


def cmt_key(name='comment', parent=post_key):
    return ndb.Key('blogs', name)


# Welcome Page. Signup Login Options #

class Welcome(Handler):
    @login_required
    def get(self):
        username = self.request.get('username')

        if valid_username(username):
            self.render('welcome.html', username=username)
        else:
            self.redirect('/signup')


# The Front Blog Page Showing 20 Entries #

class BlogPage(Handler):
    @login_required
    def get(self):
        posts = Post.query().order(-Post.created).fetch(20)
        comments = Comment.query().order(-Comment.created)
        self.render("blog.html", posts=posts, username=self.user.username, comments=comments)

    def post(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        posts = key.get()


# Post Page Permalink #

class PostPage(Handler):
    @login_required
    def get(self, post_id):
        key = ndb.Key(Post, int(post_id), parent=blog_key())
        post = key.get()
        comments = Comment.query().filter(Comment.post_id == int(post_id))

        print "comments and post id", comments, post_id

        if not post:
            self.error(404)
            return

        post._render_text = post.content.replace('\n', '<br>')
        self.render("permalink.html", post=post, comments=comments, username=self.user.username)

    def post(self, post_id):
        comments = self.request.get('comment')
        likes = self.request.get('likes')

        print likes
        if comments:
            print "this is the comment:", comments
            key = ndb.Key('Post', int(post_id), parent=blog_key())
            post = key.get()
            c = Comment(comments=comments, post_id=int(post_id), username=self.user.username)
            c.put()
            self.redirect('/comment/%s' % str(c.key.id()))  # needs to refresh also

        if likes:
            key = ndb.Key('Post', int(post_id), parent=blog_key())
            post = key.get()
            l = Likes(username=self.user.username, post_id=int(likes), parent=blog_key())
            like_Nquery = Likes.query().filter(Likes.username == self.user.username)
            for lk in like_Nquery:
                if any(lk.username) != lk.username:######PRoblem here
                    msg = "No Double Dipping, Like a different post!"
                    self.render("permalink.html", error=msg, post=post, comments=comments, username=self.user.username)

                else:
                    l.put()
                    like_query = Likes.query().filter(Likes.post_id == post.key.id())
                    like_count = like_query.count()
                    post.likes = int(like_count)
                    post.put()




            self.redirect('/blog/%s' % int(post_id) )

        else:
            self.render('welcome.html')

class EditPost(Handler):
    @login_required
    def get(self, post_id):
        key = ndb.Key(Post, int(post_id), parent=blog_key())
        post = key.get()
        comments = Comment.query().filter(Comment.post_id == int(post_id))
        print "comments and post id", comments, post_id

        if not post:
            self.error(404)
            return

        post._render_text = post.content.replace('\n', '<br>')
        self.render("editPost.html", post=post, comments=comments, username=self.user.username)

    @p_edit_auth
    def post(self, post_id):
        postkey = ndb.Key('Post', int(post_id), parent=blog_key())
        post = postkey.get()
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            post.content = content
            post.title = title
            post.put()

        self.redirect('/blog/%s' % int(post_id))


class EditComment(Handler):
    @login_required
    def get(self, comment_id):

        commentkey = ndb.Key('Comment', int(comment_id))
        ecomment = commentkey.get()

        if not ecomment:
            self.error(404)
            return

        ecomment._render_text = ecomment.comments.replace('\n', '<br>')
        self.render("editComment.html", c=ecomment, username=self.user.username)

    @c_edit_auth
    def post(self, comment_id):
        commentkey = ndb.Key('Comment', int(comment_id))
        ecomment = commentkey.get()
        content = self.request.get("comment")
        if content:
            ecomment.comments = content
            ecomment.put()
        self.redirect('/comment/%s' % str(ecomment.key.id()))


# New Post Page #

class NewPost(Handler):
    @login_required
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        if title and content:

            p = Post(parent=blog_key(), title=title, content=content, username=self.user.username)

            p.put()

            self.redirect('/blog/%s' % str(p.key.id()))
        else:
            error = "You need a title and a post"
            self.render("newpost.html", title=title, content=content, error=error, username=self.user.username)


# Login Page #

class Login(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog/welcome2')
        else:
            msg = "Invalid Login"
            self.render("login.html", error=msg)


# Logout Page #

class Logout(Handler):
    @login_required
    def get(self):
        self.logout()
        self.redirect('/login')


# Signup Page#

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    return username and USER_RE.match(username)


PASS_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    return password and PASS_RE.match(password)


EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_email(email):
    return not email or EMAIL_RE.match(email)


class Signup(Handler):
    def get(self):
        self.render("signup.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')
        # self.u_id = gen_id()
        params = dict(username=self.username,
                      email=self.email, )

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Signup2(Signup):
    def done(self):
        self.redirect('/blog/welcome?username=' + self.username + self.u_id)


class Register(Signup):
    def done(self):
        # Check to see if the user exist#
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup.html', error_username=msg)
        else:

            u = User.register(self.username, self.password, )
            u.put()

            self.login(u)
            self.redirect('/blog/welcome2')


# Welcome Page#

class Welcome2(Handler):
    @login_required
    def get(self):
        if self.user:
            self.render('welcome.html', username=self.user.username)
        else:
            self.redirect('/signup')


# Login Page#
class LoginName(Handler):
    @login_required
    def get(self):
        if self.user:
            self.render('login-name.html', username=self.user.username)


### URL Handlers #####

app = webapp2.WSGIApplication([
    ("/", Index),
    ("/blog/welcome", Welcome),
    ("/blog/welcome2", Welcome2),
    ("/signup", Register),
    ("/login", Login),
    ("/logout", Logout),
    ("/blog/?", BlogPage),
    ("/blog/([0-9]+)", PostPage),
    ("/blog/newpost", NewPost),
    ("/edit/([0-9]+)", EditPost),
    ("/comment/([0-9]+)", EditComment),
    ("/likes", Likes)

],
    debug=True)
