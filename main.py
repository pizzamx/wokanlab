import webapp2

import weather

def main():
    application = webapp2.WSGIApplication([
        (r'/weather/forecast/(.*?)/(\w+)?', weather.Forecast),
        (r'/weather/history/(.*)', weather.History),
        #(r'/house/dl/(\d)/(.*)', house.Download),
        #(r'/house/sum/(.*)', house.Sum),
        #(r'/house/dailyhistory/', house.QueryArchive),
        #(r'/house/monthlyhistory/', house.QueryMonthlyArchive),
        #(r'/hd/feed', hxdsb.Feed),
        #(r'/hd/update/(.*)', hxdsb.Update),
        #(r'/hd/sw', hxdsb.SectionWorker),
        #(r'/hd/aw', hxdsb.ArticleWorker),
        #(r'/ip', ip.Handler),
        #(r'/temp', temp.Temp)
    ], debug=False)

if __name__ == '__main__':
    main()
