import wsgiref.handlers
import sys
import re
import HTMLParser

from google.appengine.ext import webapp
from google.appengine.api import urlfetch

class MyHTMLParser(HTMLParser.HTMLParser):
	getIt = False
	subnets = None
	def handle_starttag(self, tag, attrs):
		if tag == 'pre':
			self.getIt = True
	def handle_endtag(self, tag):
		if tag == 'pre':
			self.getIt = False
	def handle_data(self, data):
		if self.getIt:
			self.subnets = map(lambda l: re.compile(r'\s+').split(l)[:-1], data.split("\n")[4:-1])
			self.parse()
	def parse(self):
		for (nn, hm, nm) in self.subnets:
			parts = nm.split('.')
			self.out.write('%s/%d<br/>' % (nn, ''.join(map(lambda s: self.d2b(int(s)), parts)).count('1')))
	def d2b(self, d):
		if d == 0:
			return '0'
		b = ''
		while d != 0:
			r = d % 2
			b += str(r)
			d -= r
			d /= 2
		return b[::-1]

class Handler(webapp.RequestHandler):
    def get(self):
        f = urlfetch.fetch('https://www.nic.edu.cn/RS/ipstat/internalip/real.html')

        parser = MyHTMLParser()
        parser.out = self.response.out
        try:
        	parser.feed(f.content)
        	parser.close()
        except HTMLParser.HTMLParseError, e:
        	self.response.out.write(e)
