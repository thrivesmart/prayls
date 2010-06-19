from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from vendor.prayls.lilcontroller import *
from vendor.prayls.lilconfig import LilConfig
from vendor.prayls.lilcookies import LilCookies
from vendor.prayls.lilauthentication import LilAuthentication
from vendor.prayls.lilmodel import LilModel
from app.models.user import *
from app.mailers.usermailer import *
import datetime

class SignupHandler(webapp.RequestHandler):
  def post(self):
    salt_and_pw = LilAuthentication.generate_salt_and_password(self.request.get('user[password]'))
  
    new_user = User(
      first_name = self.request.get('user[first_name]'),
      last_name = self.request.get('user[last_name]'),
      primary_email = self.request.get('user[primary_email]'),
      encrypted_password = salt_and_pw[1],
      password_salt = salt_and_pw[0])
  
    success = True
    error_message = ''
    if not LilModel.UniqueValue(entity = new_user, property_name = 'primary_email'):
      success = False
      error_message = 'There is already an account with your email address.'
    else:
      new_user.put()

    if success:
      # Authenticate, show, and email
      lilcookies = LilCookies(self, LilConfig.config['cookie_secret'])
      LilAuthentication.set_current_user(lilcookies, new_user)
    
      self.response.out.write(
        LilController.Render(
          controller = 'users', 
          view = 'show', 
          layout = 'public', 
          view_locals = {'msg': "Thank you, you now have an account", 'current_user': new_user},
          layout_locals = {'head': {'title': 'Account Created'}, 'current_user': new_user}
        )
      )

      UserMailer.DeliverSignupMessageAndNotification(new_user)

    else:
      self.response.out.write(
        LilController.Render(
          controller = 'welcome', 
          view = 'index', 
          layout = 'public', 
          view_locals = {'msg': "Oh No! There was an error processing your signup: "+ error_message},
          layout_locals = {'head': {'title': 'Error With User Signup'}}
        )
      )
