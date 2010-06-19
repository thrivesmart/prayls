#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from config.routes import *
from vendor.prayls.lilconfig import *

def main():
  application_settings = LilConfig.Load()
  application = webapp.WSGIApplication(Routes.Get(), debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
