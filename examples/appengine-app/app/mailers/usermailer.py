from google.appengine.api import mail

class UserMailer:
  @staticmethod
  def DeliverSignupMessageAndNotification(user):
    sender_address = "Support Staff <support@example.com>"
    subject = "Thanks for signing up!"
    body = """
    Thank you so much for creating an Account!

    --
    Example.com (BETA)
    """
    mail.send_mail(sender_address, user.primary_email, subject, body)
    
    subject2 = "[Example.com] New Account Signup"
    body2 = """
    We got a new account!
    
    --
    Example.com (BETA)
    """ % user.key()
    mail.send_mail(sender_address, "admin@example.com", subject2, body2)
  