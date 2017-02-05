'''
Created on Jan 31, 2017

@author: toned_000
'''
import webapp2
import jinja2

form_html = """
<form>
<h2>Add a Food</h2>
<input type = "text" name ="food">
<input type = "hidden"
<button>Add</button>
</form>
"""

#template_dir = os.path.join(os.path.dirname(__file__), 'templates')
#jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Handler(webapp2.RequestHandler):
    
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

  #  def render_str(self, template, **params):
  #      t = jinja_env.get_template(template)
  #      return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
class MainPage(Handler):
    def get(self):
        self.write(form_html)


app = webapp2.WSGIApplication([
    ("/", MainPage)
])


