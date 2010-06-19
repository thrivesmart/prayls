import Cookie
import datetime
import time
import email.utils
import calendar
import base64
import hashlib
import hmac
import re
import logging

# Ripped from the Tornado Framework's web.py
# http://github.com/facebook/tornado/commit/39ac6d169a36a54bb1f6b9bf1fdebb5c9da96e09
#
# Example: 
# from vendor.prayls.lilcookies import LilCookies
# cookieutil = LilCookies(self, application_settings['cookie_secret'])
# cookieutil.set_secure_cookie(name = 'mykey', value = 'myvalue', expires_days= 365*100)
# cookieutil.get_secure_cookie(name = 'mykey')
class LilCookies:

  @staticmethod
  def _utf8(s):
    if isinstance(s, unicode):
      return s.encode("utf-8")
    assert isinstance(s, str)
    return s

  @staticmethod
  def _time_independent_equals(a, b):
    if len(a) != len(b):
      return False
    result = 0
    for x, y in zip(a, b):
      result |= ord(x) ^ ord(y)
    return result == 0

  def __init__(self, handler, cookie_secret):
    """You must specify the cookie_secret to use any of the secure methods. 
    It should be a long, random sequence of bytes to be used as the HMAC 
    secret for the signature.
    """
    if len(cookie_secret) < 45: 
      raise ValueError("LilCookies cookie_secret should at least be 45 characters long, but got `%s`" % cookie_secret)
    self.handler = handler
    self.request = handler.request
    self.response = handler.response
    self.cookie_secret = cookie_secret
  
  def cookies(self):
    """A dictionary of Cookie.Morsel objects."""
    if not hasattr(self, "_cookies"):
      self._cookies = Cookie.BaseCookie()
      if "Cookie" in self.request.headers:
        try:
          self._cookies.load(self.request.headers["Cookie"])
        except:
          self.clear_all_cookies()
    return self._cookies

  def get_cookie(self, name, default=None):
    """Gets the value of the cookie with the given name, else default."""
    if name in self.cookies():
      return self._cookies[name].value
    return default

  def set_cookie(self, name, value, domain=None, expires=None, path="/",
           expires_days=None, **kwargs):
    """Sets the given cookie name/value with the given options.

    Additional keyword arguments are set on the Cookie.Morsel
    directly.
    See http://docs.python.org/library/cookie.html#morsel-objects
    for available attributes.
    """
    name = LilCookies._utf8(name)
    value = LilCookies._utf8(value)
    if re.search(r"[\x00-\x20]", name + value):
      # Don't let us accidentally inject bad stuff
      raise ValueError("Invalid cookie %r: %r" % (name, value))
    if not hasattr(self, "_new_cookies"):
      self._new_cookies = []
    new_cookie = Cookie.BaseCookie()
    self._new_cookies.append(new_cookie)
    new_cookie[name] = value
    if domain:
      new_cookie[name]["domain"] = domain
    if expires_days is not None and not expires:
      expires = datetime.datetime.utcnow() + datetime.timedelta(
        days=expires_days)
    if expires:
      timestamp = calendar.timegm(expires.utctimetuple())
      new_cookie[name]["expires"] = email.utils.formatdate(
        timestamp, localtime=False, usegmt=True)
    if path:
      new_cookie[name]["path"] = path
    for k, v in kwargs.iteritems():
      new_cookie[name][k] = v
    
    # The 2 lines below were not in Tornado.  Instead, they output all their cookies to the headers at once before a response flush.
    for vals in new_cookie.values():
      self.response.headers._headers.append(('Set-Cookie', vals.OutputString(None)))

  def clear_cookie(self, name, path="/", domain=None):
    """Deletes the cookie with the given name."""
    expires = datetime.datetime.utcnow() - datetime.timedelta(days=365)
    self.set_cookie(name, value="", path=path, expires=expires,
            domain=domain)

  def clear_all_cookies(self):
    """Deletes all the cookies the user sent with this request."""
    for name in self.cookies().iterkeys():
      self.clear_cookie(name)

  def set_secure_cookie(self, name, value, expires_days=30, **kwargs):
    """Signs and timestamps a cookie so it cannot be forged.

    To read a cookie set with this method, use get_secure_cookie().
    """
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = self._cookie_signature(name, value, timestamp)
    value = "|".join([value, timestamp, signature])
    self.set_cookie(name, value, expires_days=expires_days, **kwargs)

  def get_secure_cookie(self, name, value=None):
    """Returns the given signed cookie if it validates, or None."""
    if value is None: value = self.get_cookie(name)
    if not value: return None
    parts = value.split("|")
    if len(parts) != 3: return None
    signature = self._cookie_signature(name, parts[0], parts[1])
    if not LilCookies._time_independent_equals(parts[2], signature):
      logging.warning("Invalid cookie signature %r", value)
      return None
    timestamp = int(parts[1])
    if timestamp < time.time() - 31 * 86400:
      logging.warning("Expired cookie %r", value)
      return None
    try:
      return base64.b64decode(parts[0])
    except:
      return None

  def _cookie_signature(self, *parts):
    hash = hmac.new(self.cookie_secret, digestmod=hashlib.sha1)
    for part in parts: hash.update(part)
    return hash.hexdigest()
