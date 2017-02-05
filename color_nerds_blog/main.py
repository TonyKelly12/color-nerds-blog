'''
Created on Jan 31, 2017

@author: toned_000
'''
import webapp2

class MainPage(webapp2.RequestHandler):
    
    def get(self):
        self.response.out.write("<h1>Hello, World!</h1>")

app = webapp2.WSGIApplication([
    ("/", MainPage)
])


