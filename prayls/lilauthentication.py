from google.appengine.ext import db
from lilcookies import LilCookies
import random
import hashlib
import hmac
import datetime

class LilAuthentication:
    
  @staticmethod
  def not_authorized(handler, lilcookies, message= None, login_url= '/login'):
    """Redirects the user to login_url, setting `login_message` cookie with the message, if necessary."""
    if message != None:
      # Secure cookie should help to prevent XSS attacks.
      lilcookies.set_secure_cookie(
        name = 'login_message', 
        value = message, 
        expires_days=1)
  
    handler.redirect(login_url)

  @staticmethod
  def pop_login_message(lilcookies):
    """ Retrieves the value in `login_message` cookie, and returns None if it didn't validate or doesn't exist. """
    login_message = lilcookies.get_secure_cookie(name = 'login_message')
    lilcookies.clear_cookie(name = 'login_message')
    return login_message
  
  @staticmethod
  def login_required(handler, lilcookies, user_class, login_url = '/login'):
    """Returns the current user if logged in, redirects to login url if not and returns None.  Sets a cookie `post_login_url` to current request url."""
    current_user = LilAuthentication.get_current_user(lilcookies, user_class)
    if current_user == None:
      lilcookies.set_cookie(
        name = 'post_login_url', 
        value = str(handler.request.url), 
        expires_days=1)
      handler.redirect(login_url)
      return None
    else: return current_user

  @staticmethod
  def logout(lilcookies):
    """Clears all cookies that pertain to login information: `u` and `post_login_url`"""
    lilcookies.clear_cookie('u')
    lilcookies.clear_cookie('post_login_url')

  @staticmethod
  def redirect_to_post_login_url_or_default(handler, lilcookies, default = '/'):
    """Redirects to the `post_login_url` or default, and then clears the `post_login_url`.  Typically used in a login handler."""
    redirection_url = lilcookies.get_cookie(name = 'post_login_url', default = default)
    handler.redirect(redirection_url)
    lilcookies.clear_cookie(name = 'post_login_url')

  @staticmethod
  def set_current_user(lilcookies, user, expires_days = 14):
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
  def password_encrypted(clear_password, pw_salt):
    return hmac.new("--%s--%s--" % (pw_salt, clear_password), digestmod=hashlib.sha1).hexdigest()
    
  @staticmethod
  def generate_salt_and_password(clear_password):
    """ Returns a tuple of a custom salt for the password, as well as a password.
    
    Typically, your user model will store both of these for later authentication
    """
    pw_salt = hmac.new("--%s--%s--" % (datetime.datetime.utcnow(), random.getrandbits(16)), digestmod=hashlib.sha1).hexdigest()
    password = LilAuthentication.password_encrypted(clear_password, pw_salt)
    return (pw_salt, password)
    
  @staticmethod
  def verify_password(clear_password, user_salt, user_encrypted_password):
    """ Returns true or false if the clear password matches the given values, which presumably are stored in your user model"""
    return user_encrypted_password == LilAuthentication.password_encrypted(clear_password, user_salt)
    