# -*- coding: gb2312 -*-
import sys, urllib, urllib2, cPickle, pprint, logging, re
from google.appengine.api import mail
from google.appengine.api import urlfetch

from datetime import tzinfo, timedelta, datetime, date

from google.appengine.ext import webapp
from google.appengine.ext import db
from django.utils import simplejson

class DailyHouseStat(db.Model):
    stat_date = db.DateProperty()
    #forward = 3 * 4, completed = 3 * 4 + 3, resold = 3 * 3, 36 in total 
    ava_forward = db.ListProperty(int)        #���۷������� ���۷������ ����סլ���� ����סլ���
    offered_forward = db.ListProperty(int)    #�����Ϲ����� �����Ϲ���� סլ�Ϲ����� סլ�Ϲ����
    signed_forward = db.ListProperty(int)     #����ǩԼ���� ����ǩԼ��� סլǩԼ���� סլǩԼ���
    unsigned_completed = db.ListProperty(int) #δǩԼ���� δǩԼ��� δǩԼסլ���� δǩԼסլ���
    offered_completed = db.ListProperty(int)  #�����Ϲ����� �����Ϲ���� סլ�Ϲ����� סլ�Ϲ����
    signed_completed = db.ListProperty(int)   #����ǩԼ���� ����ǩԼ��� סլǩԼ���� סլǩԼ���
    misc_completed = db.ListProperty(int)     #�ַ���Ŀ���� ¥������ ��ʼ�Ǽ����
    ava_resold = db.ListProperty(int)         #���۷�Դ���� ����סլ���� ����סլ���
    new_reg_resold = db.ListProperty(int)     #�·�����Դ���� �·���סլ���� �·���סլ���
    signed_resold = db.ListProperty(int)      #����ǩԼ���� סլǩԼ���� סլǩԼ���
                                                
class MonthlyHouseStat(DailyHouseStat):
    approved_forward = db.ListProperty(int)   #��׼Ԥ�����֤ ��׼Ԥ����� ��׼סլ���� ��׼סլ���

class MonthlyRatio(db.Model):
    stat_date = db.DateProperty()
    ava_forward = db.ListProperty(float)        
    offered_forward = db.ListProperty(float)    
    signed_forward = db.ListProperty(float)     
    unsigned_completed = db.ListProperty(float) 
    offered_completed = db.ListProperty(float)  
    signed_completed = db.ListProperty(float)   
    misc_completed = db.ListProperty(float)     
    ava_resold = db.ListProperty(float)         
    new_reg_resold = db.ListProperty(float)     
    signed_resold = db.ListProperty(float)      
    approved_forward = db.ListProperty(float)   
    
url1 = 'http://bjfdc.bjjs.gov.cn/publicbjjs/statistic/popup_everyday_all.asp?date_statistic=%s'     #05-3-15 +
url2 = 'http://bjfdc.bjjs.gov.cn/publicbjjs/statistic/popup_secondhouse_everyday.asp'   #07-7-1 +

class QueryArchive(webapp.RequestHandler):
    def post(self):
        indices = self.request.get("indices").split(':')
        hideWeekend = self.request.get("hideWeekend") == 'true'
        result = {}
        for stat in self.iterAll():
            if (not hideWeekend) or (hideWeekend and (stat.stat_date.weekday() not in [5, 6])):
                arr = stat.ava_forward + stat.offered_forward + stat.signed_forward + stat.unsigned_completed + stat.offered_completed + \
                    stat.signed_completed + stat.misc_completed + stat.ava_resold + stat.new_reg_resold + stat.signed_resold
                a2 = []
                for index in xrange(len(arr)):
                    if str(index) in indices:
                        a2.append(arr[index])
                result[stat.stat_date.ctime()] = a2
        self.response.out.write(simplejson.dumps(result).replace(', -1', ', null').replace('[-1', '[null'))
        
    def iterAll(self):
        size = 365 * 2  #2 years
        key = None
        end = False
        count = 0
        while not end:
            q = DailyHouseStat.all()    #.filter('stat_date >', date(2009, 3, 1))
            if key:
                q.filter("__key__ > ", key)
            results = q.fetch(size)
            for result in results:
                count += 1
                yield result
            if size > len(results):
                end = True
            else:
                key = results[-1].key()
class QueryMonthlyArchive(webapp.RequestHandler):
    def post(self):
        indices = self.request.get("indices").split(':')
        ids2 = self.calc(indices)
        result = {}
        stats = MonthlyRatio.all().order('stat_date')
        stats_d = MonthlyHouseStat.all().order('stat_date')
        
        #stats_d��һ����
        stat_d = stats_d[0]
        result[stat_d.stat_date.ctime()] = self.fill(stat_d, ids2) + self.fill(None, indices)
            
        for i in range(stats.count()):
            stat = stats[i]
            stat_d = stats_d[i + 1]
            result[stat.stat_date.ctime()] = self.fill(stat, indices) + self.fill(stat_d, ids2)
            #logging.debug('indices: %s, %s, result: %s' % (indices, ids2, result[stat.stat_date.ctime()]))
        self.response.out.write(simplejson.dumps(result).replace(', -1.0', ', null').replace('[-1.0', '[null'))
        
    def calc(self, ids):
        "ͨ��ͬ��/����ѡ��������ȷ����Ӧ��ÿ��ͳ����Ŀ����ţ����ƿڡ�����"
        "7 * 8 + 4 * 6"
        a = []
        for id in ids:
            i = int(id)
            if i >= 0 and i <= 55:
                a.append(str(4 * (i / 8) + (i - 8 * (i / 8)) % 4))
            else:
                i -= 56
                a.append(str(28 + 3 * (i / 6) + (i - 6 * (i / 6)) % 3))
        return set(a)
    
    def fill(self, stat, indices):
        if not stat:
            return [-1] * len(indices)
        arr = stat.ava_forward + stat.offered_forward + stat.signed_forward + stat.approved_forward + stat.unsigned_completed + stat.offered_completed + \
            stat.signed_completed + stat.misc_completed + stat.ava_resold + stat.new_reg_resold + stat.signed_resold
        a = []
        for index in xrange(len(arr)):
            if str(index) in indices:
                a.append(arr[index])
        #logging.debug('indices: %s, result: %s' % (indices, a))
        return a
        
    def get(self):
        self.post()
    
class Sum(webapp.RequestHandler):
    def get(self, d):
        if not d:
            sd = date.today().replace(day=1)
            #cron�Լ��ܵĻ���ȡ�ϸ���
            if sd.month == 1:
                m = 12
                y = sd.year - 1
            else:
                m = sd.month - 1
                y = sd.year
            stats = DailyHouseStat.all().filter('stat_date >=', sd.replace(month=m,year=y)).filter('stat_date <=', sd - timedelta(days=1))
            sd = sd.replace(month=m,year=y)
        else:
            #ָ�����ڣ�ȡ����
            sd = datetime.strptime(d, '%Y-%m-%d').date().replace(day=1)
            if sd.month == 12:
                m = 1
                y = sd.year + 1
            else:
                m = sd.month + 1
                y = sd.year
            stats = DailyHouseStat.all().filter('stat_date >=', sd).filter('stat_date <=', sd.replace(month=m,year=y) - timedelta(days=1))
            ms = MonthlyHouseStat.all().filter('stat_date =', sd).get()
        if stats.count():
            ms = MonthlyHouseStat.all().filter('stat_date =', sd).get()
            if ms:
                ms.delete()
            ms = MonthlyHouseStat(ava_forward=[0, 0, 0, 0], offered_forward=[0, 0, 0, 0], signed_forward=[0, 0, 0, 0], approved_forward = [0, 0, 0, 0], unsigned_completed=[0, 0, 0, 0], offered_completed=[0, 0, 0, 0], signed_completed=[0, 0, 0, 0], misc_completed=[0, 0, 0], ava_resold=[0, 0, 0], new_reg_resold=[0, 0, 0], signed_resold=[0, 0, 0])
            ms.stat_date = sd
            for stat in stats:
                for k in ('ava_forward', 'offered_forward', 'signed_forward', 'unsigned_completed', 
                            'offered_completed', 'signed_completed', 'misc_completed', 'ava_resold', 'new_reg_resold', 'signed_resold'):
                    k = '_' + k
                    if k in stat.__dict__.keys():
                        packed = zip(ms.__dict__[k], stat.__dict__[k])
                        ms.__dict__[k] = [(x if x >= 0 else 0) + (y if y >= 0 else 0) for (x, y) in packed]
            ms.put()

            self.response.out.write('1')
        else:
            self.response.out.write('2')
            
        
class Download(webapp.RequestHandler):
    def get(self, cat, d):
        if cat == '2':    #ÿ������
            if not d:
                sd = date.today()
            else:
                sd = datetime.strptime(d, '%Y-%m-%d').date()
            if sd.day < 3:
                self.response.out.write('3')
                return
            else:
                sd = sd.replace(day=1)
            url = url1 % str(sd)
            try:
                html = urlfetch.fetch(url, deadline=10).content
                if sd.month == 1:
                    m = 12
                    y = sd.year - 1
                else:
                    m = sd.month - 1
                    y = sd.year
                sd = sd.replace(year=y,month=m,day=1)
                #sd=ǰһ����
                stat = MonthlyHouseStat.all().filter('stat_date =', sd).get()
                if not stat:
                    stat = MonthlyHouseStat(ava_forward=[0, 0, 0, 0], offered_forward=[0, 0, 0, 0], signed_forward=[0, 0, 0, 0], unsigned_completed=[0, 0, 0, 0], offered_completed=[0, 0, 0, 0], signed_completed=[0, 0, 0, 0], misc_completed=[0, 0, 0], ava_resold=[0, 0, 0], new_reg_resold=[0, 0, 0], signed_resold=[0, 0, 0])
                    stat.stat_date = sd
                self.handle3(html, stat, sd)
                self.response.out.write('1')            
            except Exception, e:
                self.report(url, e.message)
                self.response.out.write('0')
                raise
        elif cat == '1':    #ÿ������
            if not d:
                d = str(date.today() - timedelta(days=2))
            url = url1 % d
            try:
                html = urlfetch.fetch(url, deadline=10).content
                sd = datetime.strptime(d, '%Y-%m-%d').date()
                
                stat = DailyHouseStat.all().filter('stat_date =', sd).get()
                if not stat:
                    stat = DailyHouseStat(ava_forward=[-1, -1, -1, -1], offered_forward=[-1, -1, -1, -1], signed_forward=[-1, -1, -1, -1], unsigned_completed=[-1, -1, -1, -1], offered_completed=[-1, -1, -1, -1], signed_completed=[-1, -1, -1, -1], misc_completed=[-1, -1, -1], ava_resold=[-1, -1, -1], new_reg_resold=[-1, -1, -1], signed_resold=[-1, -1, -1])
                    stat.stat_date = sd
                self.handle1(html, stat)
                if sd >= date(2007, 7, 1):
                    arr = d.split('-')
                    pl = {'group_everyday_year': int(arr[0]), 'group_everyday_month': int(arr[1]), 'group_everyday_day': int(arr[2])}
                    html = urlfetch.fetch(url2, payload=urllib.urlencode(pl), method=urlfetch.POST, deadline=10).content
                    self.handle2(html, stat)
                stat.put()
                self.response.out.write('1')            
            except Exception, e:
                self.report(url, e.message)
                self.response.out.write('0')
                raise
        else:
            pass
        
    def handle1(self, html, stat):
        #tbs = re.findall(r'(?is)<table.*?bgcolor=#ffffff border=0>.*?</table>', html.decode('gb2312'))
        tbs = re.findall(r'(?is)<table.*?bgcolor="#FFFFFF">.*?</table>', html.decode('gb2312'))
        if not len(tbs):
            logging.info(html)
            raise Exception('[Daily]parse error: %s' % html)
        for table in tbs:
            title = re.search(r'<td.*?class="f1.*?">(.*?)</td>', table).group(1)
            tds = re.finditer(r'(?is)<td align="center".*?>(.*?)</td>', table)
            v = []
            for td in tds:
                try:
                    v.append(int(td.group(1)))
                except Exception, e:
                    if td.group(1) != '&nbsp;':
                        raise Exception('[Daily]fetch found no result: \n%s' % html)
            if not len(v):
                raise Exception('[Daily]fetch found no result: \n%s' % html)
            if title == u'�����ڷ�ͳ��':
                stat.ava_forward = v
            elif title.find(u'�ڷ������Ϲ�') != -1:
                stat.offered_forward = v
            elif title.find(u'�ڷ�����ǩԼ') != -1:
                stat.signed_forward = v
            elif title == u'δǩԼ�ַ�ͳ��':
                stat.unsigned_completed = v
            elif title == u'�ַ���Ŀ���':
                stat.misc_completed = v
            elif title.find(u'�ַ������Ϲ�') != -1:
                stat.offered_completed = v
            elif title.find(u'�ַ�����ǩԼ') != -1:
                stat.signed_completed = v

    def handle3(self, html, stat, sd):
        tbs = re.findall(r'(?is)<table.*?bgcolor="#FFFFFF">.*?</table>', html.decode('gb2312'))
        if not len(tbs):
            raise Exception('[Monthly]fetch found no result: \n%s' % html)
        for table in tbs:
            title = re.search(r'<td.*?class="f1.*?">(.*?)</td>', table).group(1)
            tds = re.finditer(r'(?is)<td align="center".*?>(.*?)</td>', table)
            v = []
            for td in tds:
                try:
                    v.append(int(td.group(1)))
                except:
                    v.append(-1)
            if title.find(u'Ԥ�����') != -1:
                stat.approved_forward = v
                break
        stat.put()

        if sd.month == 1:
            m = 12
            y = sd.year - 1
        else:
            m = sd.month - 1
            y = sd.year
        prev = MonthlyHouseStat.all().filter('stat_date =', sd.replace(year=y,month=m)).get()
        if prev:
            mr = MonthlyRatio.all().filter('stat_date =', sd).get()
            if not mr:
                mr = MonthlyRatio()
                mr.stat_date = sd
            for k in ('ava_forward', 'offered_forward', 'signed_forward', 'approved_forward', 'unsigned_completed', 
                        'offered_completed', 'signed_completed', 'misc_completed', 'ava_resold', 'new_reg_resold', 'signed_resold'):
                arr = []
                k = '_' + k
                #��������
                try:
                    arr += [float(x) / y for (x, y) in zip(stat.__dict__[k], prev.__dict__[k])]
                    #logging.info('[HB]%s --> %d, %d' % (k, stat.__dict__[k], prev.__dict__[k]))
                except Exception,e:
                    for j in range(len(stat.__dict__[k])):
                        arr.append(-1.0)
                #ͬ��ȥ��ͬ��
                prev2 = MonthlyHouseStat.all().filter('stat_date =', sd.replace(year=sd.year-1)).get()
                if prev2:
                    try:
                        arr += [float(x) / y for (x, y) in zip(stat.__dict__[k], prev2.__dict__[k])]
                        #logging.info('[TB]%s --> %d, %d' % (k, stat.__dict__[k], prev2.__dict__[k]))
                    except:
                        for j in range(len(stat.__dict__[k])):
                            arr.append(-1.0)
                else:
                    for j in range(len(stat.__dict__[k])):
                        arr.append(-1.0)
                    
                mr.__dict__[k] = arr
            mr.put()
        

    def handle2(self, html, stat):
        tbs = re.findall(r'(?is)<table.*?class="border-style1">.*?</table>', html.decode('gb2312'))
        v1 = []
        v2 = []
        v3 = []
        for table in tbs:
            tds = re.finditer(r'(?is)<td align="right">(.*?)</td>.*?<td>(.*?)</td>', table)
            for td in tds:
                col, value = td.group(1), td.group(2)
                if col.find(u'���۷�Դ����') != -1:
                    v1.append(int(value))
                elif col.find(u'����סլ����') != -1:
                    v1.append(int(value))
                elif col.find(u'����סլ���') != -1:
                    v1.append(int(value))
                elif col.find(u'�·�����Դ����') != -1:
                    v2.append(int(value))
                elif col.find(u'�·���סլ����') != -1:
                    v2.append(int(value))
                elif col.find(u'�·���סլ���') != -1:
                    v2.append(int(value))
                elif col.find(u'����ǩԼ����') != -1:
                    v3.append(int(value))
                elif col.find(u'סլǩԼ����') != -1:
                    v3.append(int(value))
                elif col.find(u'סլǩԼ���') != -1:
                    v3.append(int(value))
                    
        stat.ava_resold = v1
        stat.new_reg_resold = v2
        stat.signed_resold = v3

    def report(self, url, e):
        msg = 'Error reading url: %s \n%s' % (url, e)
        sender_address = 'pizzamx@gmail.com'
        user_address = "root+appengine@wokanxing.info"
        subject = 'Error report for house'

        mail.send_mail(sender_address, user_address, subject, msg)