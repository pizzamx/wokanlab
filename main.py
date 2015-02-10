import wsgiref.handlers

from google.appengine.ext import webapp

import weather, ip, temp, house
def main():
    application = webapp.WSGIApplication([
        (r'/weather/forecast/(.*?)/(\w+)?', weather.Forecast),
        (r'/weather/history/(.*)', weather.History),
        (r'/house/dl/(\d)/(.*)', house.Download),
        (r'/house/sum/(.*)', house.Sum),
        (r'/house/dailyhistory/', house.QueryArchive),
        (r'/house/monthlyhistory/', house.QueryMonthlyArchive),
        #(r'/hd/feed', hxdsb.Feed),
        #(r'/hd/update/(.*)', hxdsb.Update),
        #(r'/hd/sw', hxdsb.SectionWorker),
        #(r'/hd/aw', hxdsb.ArticleWorker),
        (r'/ip', ip.Handler),
        (r'/temp', temp.Temp)
    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
