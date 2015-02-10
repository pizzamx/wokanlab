# -*- coding: gb2312 -*-
import sys, urllib, urllib2, cPickle, pprint, logging, re, os
from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.api.labs.taskqueue import Queue, Task

from mako.template import Template
from mako.lookup import TemplateLookup

from datetime import tzinfo, timedelta, datetime, date

from google.appengine.ext import webapp
from google.appengine.ext import db
from django.utils import simplejson

base = 'http://epaper.hdzxw.com'
ignore_list = (u'广告', u'国内新闻', u'国际新闻', u'体育新闻', u'娱乐新闻', u'个股点评', u'理财周刊', u'体育彩票', u'福利彩票', u'财经新闻',u'福清长乐',u'证券新闻',
               u'汽车周刊')

class FeedItem(db.Model):
    date = db.DateTimeProperty()
    title = db.StringProperty()
    section = db.StringProperty()
    content = db.TextProperty()
    url = db.StringProperty()
    
class Parser(webapp.RequestHandler):
    def parse(self, url, pattern):
        try:
            result = []
            r = urlfetch.fetch(url, deadline=10)
            html = r.content
            if html.find('koa21') != -1:     #版面嵌了一个iframe，怀疑是电信搞的
                p = r'<frame name="hello" src="(.*?)">'
                m = re.search(p, html)
                if m:
                    uri = m.group(1)
                    url = '%s%s' % (base, uri)
                    return self.parse(url, pattern)
                else:
                    logging.error('Got iframe injection, but no target uri found')
            matches = re.finditer(pattern, html.decode('gb2312'))
            for m in matches:
                result.append(m.groups())
            return result
        except Exception, e:
            #self.report(url, e.message)
            #self.response.out.write('0')
            logging.error(e.message)
            return []
        
    def report(self, url, e):
        msg = 'Error reading url: %s \n%s' % (url, e)
        sender_address = 'pizzamx@gmail.com'
        user_address = "root+appengine@wokanxing.info"
        subject = 'Error report for house'

        mail.send_mail(sender_address, user_address, subject, msg)

class Update(Parser):
    def get(self, d):
        if not d:
            d = date.today()
        else:
            d = datetime.strptime(d, '%Y-%m-%d').date()
            
        old_count = FeedItem.all().filter('date =', d).count()
        
        dstr = d.strftime('%Y%m%d')
        url = '%s/%s/1/index.html' % (base, dstr)
        pattern = ur'<a href=(.*?)>第(.*?)版:(.*?)</a>'
        items = self.parse(url, pattern)    #读取版面列表，跳过导读，到广告版为止
        index = 1
        for item in items:
            section = item[2]
            if section in ignore_list:
                continue
            url = '%s/%s/%s' % (base, dstr, item[0][3:])
            pattern = r'<td class=.*?onmouseover=.*?><a href =(.*?)>(.*?)</a></td>'
            task = Task(url='/hd/sw', params={'url': url, 'pattern': pattern, 'dstr': dstr, 'index': index, 's': section})
            task.add('hd-section-queue')
            index += 1
                
class SectionWorker(Parser):
    def post(self):
        url = self.request.get('url')
        pattern = self.request.get('pattern')
        dstr = self.request.get('dstr')
        i = self.request.get('index')
        d = datetime.strptime(dstr, '%Y%m%d')
        s = self.request.get('s')
        
        index = 0
        
        items = self.parse(url, pattern)    #读取版面文章列表
        for item in items:
            title = item[1]
            url = item[0]
            if title.startswith(u'· '):
                title = title[2:]
            #url是这样的：../2/content_0.htm
            #要变成：/2/icontent0.htm
            url = '%s/%s/%s/icontent%s' % (base, dstr, url[3:url.find('/', 3)], url[-6:])
            key_name = '%s_%s_%d' % (dstr, i, index)
            fi = FeedItem(date=d, section=s, title=title.replace('&nbsp', ' '), url=url, key_name=key_name)
            fi.put()
            task = Task(url='/hd/aw', params={'url': url, 'pattern': r'(?mis)<body.*?>(.*?)</body>', 'key': key_name})
            task.add('hd-detail-queue')
            index += 1
    
class ArticleWorker(Parser):
    def post(self):
        url = self.request.get('url')
        pattern = self.request.get('pattern')
        key = self.request.get('key')
        
        items = self.parse(url, pattern)
        fi = FeedItem.get_by_key_name(key)
        try:
            content = items[0][0]
            parent = url[:url.rfind('/')]
            content = re.sub(r'(?mis)(<img.*?src=)"(.*?)">', r'\1"%s/\2">' % parent, content)
            fi.content = content
            fi.put()
        except Exception, e:
            self.response.set_status(404)
            #logging.error('Failed extracting article: %s. Items: %s, msg: %s' % (url, items, e.message))

class Feed(webapp.RequestHandler):
    def get(self):
        data = FeedItem.all().order('-date').fetch(200)
        mylookup = TemplateLookup(directories=[os.path.dirname(__file__)], format_exceptions=True)
        template =  mylookup.get_template('atom.xml')
        self.response.headers['Content-type'] = 'application/xml; charset=utf-8'
        self.response.out.write(template.render_unicode(data=data, now=datetime.now()))
        
    def query(self, dumpComments):
        return self.queryCommentFeed() if dumpComments else self.queryPostFeed() 