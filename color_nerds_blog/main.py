'''
Created on Jan 31, 2017

@author: toned_000
'''
import os
import webapp2
import jinja2

from string import letters
from google.appengine.ext import db
#from jinja2 import Environment, PackageLoader, select_autoescape
hidden_html = """
<input type="hidden" name="food" value="%s">
"""

item_html = "<li>%s</li>"

shopping_list_html = """
<br>
<br>
<h2>Shopping List</h2>
<ul>
%s
</ul>

"""

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape= True)

class Handler(webapp2.RequestHandler):
    
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
class Post(db.Model):
    user_id = db.IntegerProperty(required = True)
    title = db.StringProperty(required = True)
    bpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_mod = db.DateTimeProperty(auto_now = True)
    hashtag = db.StringProperty(required = False)
    likes = db.IntegerProperty(required = True)

class User(db.Model):
    u_id = db.IntegerProperty(required = True)
    rName = db.StringProperty(required = True)
    sName = db.StringProperty(required = True)
    signup = db.DateTimeProperty(auto_now_add = True)
    email = db.EmailProperty(required = True)

class Index(Handler):
    def render_front(self, title="", bpost="", error=""):
        self.render("blog.html", title = title, bpost = bpost, error = error)

    def blog_key(name = 'default'):
        return db.Key.from_path('blogs', name)

    def get(self):
        self.render_front()

   

class Login(Handler):
    def get(self):
        self.render("login.html")

class Signup(Handler):
    def get(self):
        self.render("signup.html")

class BlogPage(Handler):
    def get(self):
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        self.render("blog.html", posts = posts)

class PostPage(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return
        self.render("post.html", post = post)

class NewPost(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        bpost = self.request.get("post")

        if title and bpost:
            P = Post(parent = blog_key(), subject = subject, content = content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "You need a title and a post"
            self.render("newpost.html", subject = subject, content = content, error = error)

app = webapp2.WSGIApplication([
    ("/", Index),
    ("/signup", Signup),
    ("/login", Login),
    ("/blog", BlogPage),
    ("/blog/post/([0-9]+)", PostPage),
    ("/blog/newpost", NewPost)

],
debug = True)


