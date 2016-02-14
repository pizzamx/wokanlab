# -*- coding: utf-8 -*-
import sys, urllib, urllib2, cPickle, pprint, logging, re
from google.appengine.api import mail

from datetime import tzinfo, timedelta, datetime, date
from xml.etree import cElementTree

#from django.utils import simplejson
import json as simplejson

import webapp2
from google.appengine.ext import db

class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(seconds=0)

class CST(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=8)
    def dst(self, dt):
        return timedelta(0)


class TQ(webapp2.RequestHandler):
    CODE_DATA_URL = 'http://weather.com.cn/data/listinfo/city%s.xml'
    WEATHER_DATA_URL = 'http://m.weather.com.cn/data/%s.html'
    LATEST_DATA_URL = 'http://weather.com.cn/data/sk/%s.html'
    WHOLE_DAY_DATA_URL = 'http://flash.weather.com.cn/sk2/%s.xml'
    PICKLE_FILE_PATH = 'tqdata.pickle'

    def __init__(self):
        self.data = {}
        
    def sync(self):
        self.fetch(0, self.data)
        f = open(self.PICKLE_FILE_PATH, 'wb')
        cPickle.dump(self.data, f, 2)
        f.close()
        
    def loadPickle(self):        
        f = open(self.PICKLE_FILE_PATH, 'rb')
        self.data = cPickle.load(f)
        f.close()

    def makeHandler(self, url, param):
        #if we donot need a proxy, just use:
        #
        #return urllib.urlopen(self.CODE_DATA_URL % code)
        try:
            return urllib2.urlopen(url % param)
        except urlfetch.DownloadError:
            msg = 'Error reading url: %s' % self.request.url
            sender_address = 'pizzamx@gmail.com'
            user_address = "root+appengine@wokanxing.info"
            subject = u'天气预报错误报告'

            mail.send_mail(sender_address, user_address, subject, msg)
            return None
        
    def fetch(self, lvl, container, code=''):
        try:
            s = self.makeHandler(self.CODE_DATA_URL, code).read()
        except:
            self.response.set_status(500)
            return
        arr = s.split(',')
        for data_tuple in arr:
            (code, entity) = data_tuple.split('|')
            #entity = entity.decode('utf-8')
            if lvl < 3:
                print '%sCrwaling %s' % ('\t' * lvl, entity)
            if lvl < 2:
                container[entity] = {
                    'code': code,
                    'data': {}
                }
                self.fetch(lvl + 1, container[entity]['data'], code)
            elif lvl == 2:
                container[entity] = {}
                self.fetch(lvl + 1, container[entity], code)
            else:
                container['code'] = entity
                
    def search(self, name):
        if name:
            try:
                name = urllib.unquote(name).decode('utf-8')
            except:
                name = urllib.unquote(name).decode('gbk')
        else:
            name = u'北京'
            
        for (province, provinceData) in self.data.iteritems():
            for (city, cityData) in provinceData['data'].iteritems():
                for (county, countyData) in cityData['data'].iteritems():
                    if county == name:
                        return countyData['code']
        return ''
            
#    def getLatest(self, name):
#        code = self.search(name)
#        if code:
#            return self.makeHandler(self.LATEST_DATA_URL, code).read()
#        return ''
#            
    def dump(self, f):
        """
        for (province, provinceData) in self.data.iteritems():
            f.write('%s(%s)\n' % (province, provinceData['code']))
            for (city, cityData) in provinceData['data'].iteritems():
                f.write('\t%s(%s)\n' % (city, cityData['code']))
                for (county, countyData) in cityData['data'].iteritems():
                    f.write('\t\t%s(%s)\n' % (county, countyData['code']))
        """
    


class Forecast(TQ):
    "天气预报"
    LEGEND_FILE = '/assets/PNG/150x150/%s.png'

    legend_map = {
        0: 'sunny',
        1: 'm-cloudy',
        2: 'fair',
        3: 'm-c-rain',
        4: 'thunder-storm',
        5: 'thunder-storm',
        6: 'rainny-snow',
        7: 'fair-drizzle',
        8: 'drizzle',
        9: 'rainy',
        10: 'shower',
        11: 'sleet',
        12: 'sleet',
        13: 'm-c-snow',
        14: 'flurries',
        15: 'snow',
        16: 'blowing-snow',
        17: 'blizzard',
        18: 'fog',
        19: 'freezing-rain',
        20: 'na',   #老外没有沙尘暴……
        21: 'drizzle',
        22: 'rainy',
        23: 'shower',
        24: 'sleet',
        25: 'sleet',
        26: 'snow',
        27: 'blowing-snow',
        28: 'blizzard',
        29: 'na',
        30: 'na',
        31: 'na'
    }
    
    def get(self, place, format):
        self.loadPickle()
        code = self.search(place)
        if code:
            try:
                stream = self.makeHandler(self.WEATHER_DATA_URL, code).read()
            except:
                self.response.set_status(500)
                return
            data = simplejson.loads(stream)['weatherinfo']
            """
            {"weatherinfo":{
                "city":"福州",
                "date_y":"2009年04月09日",
                "date":"三月十四",
                "cityid":"101230101",
                "temp1":"13℃~24℃",
                "temp2":"13℃~25℃",
                "weather1":"多云",
                "weather2":"多云",
                "img1":"1",
                "img2":"99",
                "img3":"1",
                "img4":"99",
                "wind1":"微风",
                "wind2":"微风",
                "index":"舒适",
                "index_d":"建议着薄型套装等春秋过渡装。年老体弱者宜着套装。但昼夜温差较大，注意适当增减衣服。",
                "index_uv":"弱"
            }}        
            """
            #pprint.pprint(data, self.response.out)
            legend = int(data['img1'])
            if format == 'json':
                output = 'handleWeatherData(' + simplejson.dumps(data, ensure_ascii=False) + ')'
            else:
                output = '''<div><img src="%s" alt="%s" style="float: left;"/>
                        <h2 style="font-size: 70px; margin:0; letter-spacing: 10px;">%s</h2>
                        <div style="">%s</div><div style="">%s</div><div style="">%s</div>
                        </div><div><a href="/weather/forecast/%s/json" target="_blank">I could use a cross-domain callback, thx yo!</a></div>''' % (self.LEGEND_FILE % self.legend_map[legend], data['weather1'].encode('utf-8'), data['city'].encode('utf-8'),                                                    data['date_y'].encode('utf-8'), data['weather1'].encode('utf-8'), data['temp1'].encode('utf-8'), data['city'].encode('utf-8'))
            self.response.write(output)
        else:
            self.response.write('')

class TQModel(db.Model):
    date = db.DateTimeProperty()
    xml = db.TextProperty()
    city = db.StringProperty()

class History(TQ):
    "今日天气曲线"
    def get(self, place):
        self.loadPickle()
        code = self.search(place)
        if code:
            try:
                stream = self.makeHandler(self.WHOLE_DAY_DATA_URL, code).read()
            except:
                self.response.set_status(500)
                return
            dom = cElementTree.fromstring(stream)
            """
            <?xml version="1.0"?>
            <sktq id="101010100" ptime="09-06-24 00:00" city="北京">
                 <qw h="00" wd="27.6" fx="242" fl="1" js="0" sd="36"/>
                 <qw h="23" wd="28.5" fx="254" fl="1.8" js="0" sd="33"/>
                 <qw h="22" wd="29.1" fx="248" fl="2.6" js="0" sd="32"/>
                 <qw h="21" wd="29.9" fx="211" fl="2.3" js="0" sd="31"/>
                 <qw h="20" wd="31.1" fx="200" fl="1.7" js="0" sd="28"/>
                 <qw h="19" wd="32.3" fx="181" fl="2.6" js="0" sd="27"/>
                 <qw h="18" wd="33.6" fx="206" fl="3.8" js="0" sd="24"/>
                 <qw h="17" wd="33.9" fx="37" fl="2" js="0" sd="20"/>
            
                 <qw h="16" wd="34" fx="209" fl="2.1" js="0" sd="17"/>
                 <qw h="15" wd="34.8" fx="221" fl="3.7" js="0" sd="14"/>
                 <qw h="14" wd="34.6" fx="339" fl="2.4" js="0" sd="13"/>
                 <qw h="13" wd="33.7" fx="71" fl="1.8" js="0" sd="16"/>
                 <qw h="12" wd="33.1" fx="338" fl="1.4" js="0" sd="18"/>
                 <qw h="11" wd="30.8" fx="65" fl="3.1" js="0" sd="26"/>
                 <qw h="10" wd="29.2" fx="342" fl="2.1" js="0" sd="30"/>
                 <qw h="09" wd="27.3" fx="71" fl="2.9" js="0" sd="36"/>
                 <qw h="08" wd="23.7" fx="31" fl="1.1" js="0" sd="51"/>
            
                 <qw h="07" wd="23" fx="330" fl="0.8" js="0" sd="54"/>
                 <qw h="06" wd="21.5" fx="327" fl="0.5" js="0" sd="56"/>
                 <qw h="05" wd="21" fx="0" fl="0" js="0" sd="52"/>
                 <qw h="04" wd="20.9" fx="85" fl="1.8" js="0" sd="53"/>
                 <qw h="03" wd="22.8" fx="220" fl="4.2" js="0" sd="44"/>
                 <qw h="02" wd="24.8" fx="214" fl="3.1" js="0" sd="35"/>
                 <qw h="01" wd="24.6" fx="206" fl="1.6" js="0" sd="37"/>
            </sktq>
            """
            ptime = datetime.strptime(dom.get('ptime'), '%y-%m-%d %M:%S')
            m = TQModel(date=ptime, xml=db.Text(stream, encoding="utf-8"), city=code)
            m.put()
            
            self.response.write(ptime)
            for segm in dom.findall('.//qw'):
                pass
            
    def post(self, place):
        self.loadPickle()
        code = self.search(place)
        data = TQModel.all().filter('city =', code).order('date')
        result = {'count': data.count(), 'data': []}
        years = [];
        int_data = []   #interim data
        for tq in data:
            xml = re.sub(r'city=".*?"', '', tq.xml)
            dom = cElementTree.fromstring(xml)
            a = dom.findall('qw')
            r = [(float(a[0].get(k)) if a[0].get(k) else 0) for k in ['wd', 'wd', 'fl', 'js', 'sd']]
            r[0] = 35
            for t in a:
                try:
                    wd = float(t.get('wd'))
                    #if wd <= 0:
                    #    continue
                    r[0] = min(r[0], wd)    #最低温度
                    r[1] = max(r[1], wd)    #最高温度
                    r[2] = max(float(t.get('fl')), r[2])
                    r[3] = max(float(t.get('js')), r[3])
                    r[4] = max(float(t.get('sd')), r[4])
                except:     #可能抓取数据错误……
                    pass
                    #r[int(t.get('h'))] = [0] * 4
            r.insert(0, '2010/%d/%d' % (tq.date.month, tq.date.day))
            r.append(tq.date.year)
            if not tq.date.year in years:
                years.append(tq.date.year)
            int_data.append(r)
        result['years'] = years
        f_data = {} #final data
        for d in int_data:
            if f_data.has_key(d[0]):
                rec = f_data[d[0]]
            else:
                rec = f_data[d[0]] = []
                for x in years: rec.append(None)
            rec[years.index(d[6])] = [d[1], d[2], d[3], d[4], d[5]]
        result['data'] = f_data
        
        #TODO: header expire set
        self.response.write(simplejson.dumps(result))

if __name__ == '__main__':
    tq = TQ()
    tq.loadPickle()
    raw = tq.search(u'福州')
    data = json.loads(raw)
    pprint.pprint(data)
