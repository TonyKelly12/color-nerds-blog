'''
Created on Jan 31, 2017

@author: toned_000
'''
import os
import random
import re
import webapp2
import jinja2
import hmac
import hashlib
from string import letters
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

secret = 'UwDx^YBPG8@5&mQY'

                                #### Global Functions #####
#this function is for rendering
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

#this function adds the secret to hash & value
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

#this function check to see if the seceret + val == hash
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

#this function creats a random salt
def sprinkle_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

#this function hash's the password
def make_pw_hash(username, pw, salt = None):
    if not salt:
        salt = sprinkle_salt()
    h = hashlib.sha256(username + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

#I think this function checks that the pwrd matches the hash
def valid_pw(username, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(username, password, salt)

#this function creates a user key
def user_key(group = 'default'):
    return db.Key.from_path('user', group)

                   ##### Main WEbApp Handler + Render funcions #####

class Handler(webapp2.RequestHandler):

    #basic render function pt1
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # basic render function pt2
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    # basic render function pt3
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    #this function sets the cookie
    def set_cookie(self, username, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (username, cookie_val)
        )

    #this function reads the cookie
    def read_cookie(self, username):
        cookie_val = self.request.cookies.get(username)
        return cookie_val and check_secure_val(cookie_val)

    #this function logs user in
    def login(self, user):
        self.set_cookie('user_id', str(user.key().id()))

    #this function logs user out
    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    #this function checks for valid cookie for returning user
    def initialize(self, *a, **kw):
            webapp2.RequestHandler.initialize(self, *a, **kw)
            uid = self.read_cookie('user_id')
            self.user = uid and User.by_id(int(uid))

#global render function for entire post
def render_post(response, post):
    response.out.write('<b>' + post.title + '</b><br>')
    response.out.write(post.content)
    
                                ##### Post DataBase #####

class Post(db.Model):
    #user_id = db.IntegerProperty(required = True)
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_mod = db.DateTimeProperty(auto_now=True)
    #hashtag = db.StringProperty(required = False)
    #likes = db.IntegerProperty(required = True)

    #this functions adds line breaks in post content
    def render(self): #NOT Working
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)

                               ####User Data Base#######

class User(db.Model):
    #u_id = db.IntegerProperty#
    username = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.EmailProperty

    #this method allows lookup by id for user class
    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent=user_key())

    # this method allows lookup by name for user class
    @classmethod
    def by_name(cls, username):
        u = cls.all().filter('username =', username).get()
        return u

    # this method creates user but does not store in db
    @classmethod
    def register(cls, username, pw, email=None):
        pw_hash = make_pw_hash(username, pw)
        return cls(parent=user_key(),
                    username=username,
                    pw_hash=pw_hash,
                    email=email)

    #this method validates login of user
    @classmethod
    def login(cls, username, pw):
        u = cls.by_name(username)
        if u and valid_pw(username, pw, u.pw_hash):
            return u


                                   ###  Main Index  ###

class Index(Handler):
   def render_front(self):
      self.render("index.html")

   def get(self):
     self.render_front()

def blog_key(name='default'):
    return db.Key.from_path('blogs', name)

##### Welcome Page. Signup Login Options ####

class Welcome(Handler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username=username)
        else:
            self.redirect('/signup')

                ####### The Front Blog Page Showing 20 Entries #######

class BlogPage(Handler):
    def get(self):
        posts = db.GqlQuery("select * from Post order by created desc limit 20")
        self.render("blog.html", posts=posts)

                        ####### Post Page Permalink ######

class PostPage(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return
        self.render("permalink.html", post=post)

                             ###### New Post Page ######

class NewPost(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            p = Post(parent=blog_key(), title=title, content=content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "You need a title and a post"
            self.render("newpost.html", title=title, content=content, error=error)

                                  #### Login Page ###

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

                                  #### Logout Page ###

class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect('/login')


                                ###### Signup Page#######

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

        params = dict(username=self.username,
                      email=self.email)

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
        self.redirect('/blog/welcome?username='+self.username)

class Register(Signup):
    def done(self):
        #Check to see if the user exist#
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup.html', error_username=msg)
        else:
            u=User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog/welcome2')

class Welcome2(Handler):
    def get(self):
        if self.user:
            self.render('welcome.html', username=self.user.username)
        else:
            self.redirect('/signup')

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
    ("/blog/newpost", NewPost)

],
debug=True)


