# This defines the routes of the application.  Any time they need to be changed, look here!
from app.controllers import *

class Routes(object):
  @staticmethod
  def Get():
    return [
      ('/', welcome.WelcomeHandler),
      ('/signup', users.SignupHandler),
      ('/login', sessions.LoginsHandler),
      ('/logout', sessions.LogoutsHandler)
    ]