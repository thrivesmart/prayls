from google.appengine.ext import db
from lilcookies import LilCookies
import random
import hashlib
import hmac
import datetime

class LilAuthentication:

  @staticmethod
  def login_required(handler, lilcookies, user_class, login_url):
    """Returns the current user if logged in, redirects to login url if not and returns None.  Sets a cookie `post_login_url` to current request url."""
    current_user = get_current_user(lilcookies, user_class)
    if current_user == None:
      lilcookies.set_cookie(name = 'post_login_url', value = handler.request.url(), expires_days=1)
      handler.redirect(login_url)
      return False
    else: return current_user

  @staticmethod
  def logout(lilcookies):
    """Clears all cookies that pertain to login information: `u` and `post_login_url`"""
    lilcookies.clear_cookie('u')
    lilcookies.clear_cookie('post_login_url')

  @staticmethod
  def set_current_user(lilcookies, user, expires_days = 2):
    """Stores the current user in a secure cookie, using LilCookies and `u` as the cookie key.  Assumes user is a db.Model"""
    lilcookies.set_secure_cookie(name = 'u', value = str(user.key()), expires_days = expires_days)
  
  @staticmethod
  def get_current_user(lilcookies, user_class):
    """Gets the current user from the secure cookie using LilCookiesand `u` as the cookie key. 
    
    Returns the db.get() result of it, or returns None if it doesn't exist"""
    user_key = lilcookies.get_secure_cookie(name = 'u')
    if user_key != None:
      return user_class.gql("WHERE __key__ = :1", db.Key(user_key)).get()
    else:
      return None

  @staticmethod
  def generate_salt_and_password(clear_password):
    """ Returns a tuple of a custom salt for the password, as well as a password.
    
    Typically, your user model will store both of these for later authentication
    """
    pw_salt = hmac.new("--%s--%s--" % (datetime.datetime.utcnow(), random.getrandbits(16)), digestmod=hashlib.sha1).hexdigest()
    password = hmac.new("--%s--%s--" % (pw_salt, clear_password), digestmod=hashlib.sha1).hexdigest()
    return [pw_salt, password]
    
  @staticmethod
  def verify_password(clear_password, user_salt, user_encrypted_password):
    """ Returns true or false if the clear password matches the given values, which presumably are stored in your user model"""
    encrypted_clear_pw = hmac.new("--%s--%s--" % (user_salt, clear_password), digestmod=hashlib.sha1).hexdigest()
    return user_encrypted_password == encrypted_clear_pw