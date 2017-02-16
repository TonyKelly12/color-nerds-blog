'''
Created on Jan 31, 2017

@author: toned_000
'''
import os
import re
import webapp2
import jinja2

from string import letters
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

GOOGLE_APPLICATION_CREDENTIALS = "E:\Color Nerds\Web Design\GitHub Repo's\Blogg App\color_nerds_blog\GOOGLE_APPLICATION_CREDENTIALS\Color Nerds Blog-5c4bbb37a2fe.json"

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

def render_post(response, post):
    response.out.write('<b>' + post.title + '</b><br>')
    response.out.write(post.content)
    
class Post(db.Model):
    #user_id = db.IntegerProperty(required = True)
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_mod = db.DateTimeProperty(auto_now=True)
    #hashtag = db.StringProperty(required = False)
    #likes = db.IntegerProperty(required = True)

    def render(self): #NOT Working
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)

#class User(db.Model):
#    u_id = db.IntegerProperty(required=True)
#    rName = db.StringProperty(required=True)
#    sName = db.StringProperty(required=True)
#    signup = db.DateTimeProperty(auto_now_add=True)
#    email = db.EmailProperty(required=True)



class Index(Handler): #This is probably the problem
   def render_front(self):
      self.render("index.html")

   def get(self):
     self.render_front()

def blog_key(name='default'):
    return db.Key.from_path('blogs', name)



class BlogPage(Handler):
    def get(self):
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        self.render("blog.html", posts=posts)

class PostPage(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return
        self.render("permalink.html", post=post)

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


class Login(Handler):
    def get(self):
        self.render("login.html")

class Signup(Handler):
    def get(self):
        self.render("signup.html")
app = webapp2.WSGIApplication([
    ("/", Index),
    ("/signup", Signup),
    ("/login", Login),
    ("/blog/?", BlogPage),
    ("/blog/([0-9]+)", PostPage),
    ("/blog/newpost", NewPost)

],
debug=True)


