from google.appengine.ext import db

class User(db.Model):
  first_name = db.StringProperty(required=True)
  last_name = db.StringProperty(required=True)
  primary_email = db.EmailProperty(required=True, indexed=True)
  encrypted_password = db.StringProperty(indexed=True)
  password_salt = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add=True, indexed=True)
