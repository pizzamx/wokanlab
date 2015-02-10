# -*- coding: utf-8 -*-
from google.appengine.ext import db

class Category(db.Model):
    name = db.StringProperty()
    type = db.IntegerProperty(default=2)     #1=收入，2=支出
    daddy = db.SelfReferenceProperty()
    
class Expense(db.Model):
    #index = db.IntegerProperty()
    date = db.DateProperty(auto_now_add=True)
    amount = db.FloatProperty()
    category = db.ReferenceProperty(Category)
    note = db.StringProperty()
    
class SharedCounter(db.Model):
    name = db.StringProperty()
    count = db.IntegerProperty(required=True, default=0)