from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from vendor.prayls.lilconfig import *
from vendor.prayls.lilcontroller import *
from vendor.prayls.lilauthentication import *
from vendor.prayls.lilcookies import *
from app.models.user import *
import logging

class LoginsHandler(webapp.RequestHandler):
  def post(self):
    lilcookies = LilCookies(self, LilConfig.config['cookie_secret'])
    potential_user = User.gql("WHERE primary_email = :1", self.request.get('email')).get()
    
    if potential_user != None:
      if LilAuthentication.verify_password(
        clear_password = self.request.get('password'), 
        user_salt = potential_user.password_salt, 
        user_encrypted_password = potential_user.encrypted_password):
        LilAuthentication.set_current_user(lilcookies, potential_user)
        LilAuthentication.redirect_to_post_login_url_or_default(self, lilcookies)
        return True
      
    self.response.out.write(
      LilController.Render(
        controller = 'sessions', 
        view = 'login', 
        layout = 'public', 
        view_locals = {'msg': 'Sorry, that was the wrong email and password combination!'},
        layout_locals = {'head': {'title': 'Welcome Back! Login'}}
      )
    )

  def get(self):
    self.response.out.write(
      LilController.Render(
        controller = 'sessions', 
        view = 'login', 
        layout = 'public', 
        view_locals = {},
        layout_locals = {'head': {'title': 'Welcome Back! Login'}}
      )
    )
    
class LogoutsHandler(webapp.RequestHandler):
  def get(self):
    lilcookies = LilCookies(self, LilConfig.config['cookie_secret'])
    LilAuthentication.logout(lilcookies)
    
    self.response.out.write(
      LilController.Render(
        controller = 'sessions', 
        view = 'logout', 
        layout = 'public', 
        view_locals = {},
        layout_locals = {'head': {'title': 'Thank You! Come again'}}
      )
    )