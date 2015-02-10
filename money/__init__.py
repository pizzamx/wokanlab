# -*- coding: utf-8 -*-
import logging
import wsgiref.handlers

from xml.etree import cElementTree
from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext import db
from money.model import Category, Expense, SharedCounter

class Index(webapp.RequestHandler):
    def get(self):
        pass
    
class Upload(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
            <html><body>
                <form enctype="multipart/form-data" method="post">
                    <input type="file" name="xml" /><input type="submit" value="upload" />
                </form>
            </body></html>
        """)
    
    def post(self):
        counter = SharedCounter.get_or_insert('_exp')
        stream = self.request.get('xml')
        dom = cElementTree.fromstring(stream)

        def import_cats():
            #导入支出类别
            for cat in dom.findall('.//CATEGORY'):
                if cat.get('DESCRIPTION') != '系统预置类目，不能修改删除':
                    name = cat.get('NAME')
                    type = int(cat.get('CTYPE'))
                    if type == 2:
                        c = Category(key_name='c_' + name)
                        c.name = name
                        if cat.get('FNAME'):
                            c.daddy = Category.get_by_key_name('c_' + cat.get('FNAME'))
                        c.put()
        def import_trans():
            #导入支出明细
            for trans in dom.findall('.//TRANS'):  #python带的ElementTree版本(1.2.6)不支持@语法
                if trans.get('TRANSTYPE') == '2':
                    incexp = trans.getchildren()[0]
                    index = counter.count
                    exp = Expense(parent=counter, key_name='_exp_%d' % index)
                    exp.index = index
                    exp.date = datetime.strptime(trans.get('TRANSDATE'), '%Y-%m-%d').date()
                    exp.amount = float(incexp.get('AMOUNT'))
                    if trans.get('DESCRIPTION'):
                        exp.note = trans.get('DESCRIPTION')
                    exp.category = Category.get_by_key_name('c_' + incexp.get('CATEGORY'))
                    exp.put()
                    
                    counter.count += 1
                    counter.put()
        #db.run_in_transaction(_import)
        import_cats()