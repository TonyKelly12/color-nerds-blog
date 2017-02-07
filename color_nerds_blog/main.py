'''
Created on Jan 31, 2017

@author: toned_000
'''
import os
import webapp2
import jinja2

from google.appengine.ext import db

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
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    hashtag = db.StringProperty(required = False)
    likes = db.IntegerProperty(required = True)

class User(db.Model):
    u_id = db.IntegerProperty(required = True)
    rName = db.StringProperty(required = True)
    sName = db.StringProperty(required = True)
    signup = db.DateTimeProperty(auto_now_add = True)
    email = db.EmailProperty(required = True)

class MainPage(Handler):
    def get(self):
        self.render("index.html")
    
    def post(self):
        title = self.request.get


app = webapp2.WSGIApplication([
    ("/", MainPage)
])


