from datetime import date, timedelta
import time, urllib2

d1 = date(2005,3,1)
b = 0

lurl = 'http://localhost:8080/house/sum/%s'
rurl = 'http://lab.wokanxing.info/house/sum/%s'

while d1 < date.today():
    time.sleep(b)
    url = rurl % d1
    try:
        f = urllib2.urlopen(url)
        if f.read() == '2':
            print '[SKIP]%s' % d1
        elif f.read() == '0':
            print '[PROBLEM]%s' % d1
            continue
        else:
            print '[OK]%s' % d1
    except Exception, e:
        print '[PROBLEM]%s' % d1
        continue
    if d1.month == 12:
        m = 1
        y = d1.year + 1
    else:
        m = d1.month + 1
        y = d1.year
    d1 = d1.replace(month=m,year=y)
    
