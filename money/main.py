import wsgiref.handlers

from google.appengine.ext import webapp

import money

def main():
    application = webapp.WSGIApplication([
        (r'/money/upload', money.Upload),
        (r'.*', money.Index)
    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
