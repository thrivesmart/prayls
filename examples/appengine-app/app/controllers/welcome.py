from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from vendor.prayls.lilconfig import *
from vendor.prayls.lilcontroller import *
from vendor.prayls.lilcookies import LilCookies
from vendor.prayls.lilauthentication import *
from app.models.user import *
import logging

class WelcomeHandler(webapp.RequestHandler):
  def get(self):
    lilcookies = LilCookies(self, LilConfig.config['cookie_secret'])
    current_user = LilAuthentication.get_current_user(lilcookies, User)

    self.response.out.write(
      LilController.Render(
        controller = 'welcome', 
        view = 'index', 
        layout = 'public', 
        view_locals = {'msg': "Welcome to Example.com!"},
        layout_locals = {'head': {'title': 'Welcome!'}, 'current_user': current_user}
      )
    )
