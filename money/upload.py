# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.tools import bulkloader

from xml.etree import cElementTree
from datetime import datetime

from money.model import Category, Expense, SharedCounter

class AlbumLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Album',
                               [('title', str),
                                ('artist', str),
                                ('publication_date',
                                 lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date()),
                                ('length_in_minutes', int)
                               ])

loaders = [AlbumLoader]


def prepare():
    f = open(r'c:\Documents and Settings\Administrator\Desktop\2009年5月5日.xml', 'r')
    dom = cElementTree.parse(f)
    o = open('trans.csv', 'w')

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
            
    o.close()
    f.close()

if __name__ == '__main__':
    prepare()