import re
from datetime import timedelta, date

f = open(r'D:\temp\e.txt')
s = f.read()
f.close()



tbs = re.findall(r'<table.*?class="border-style1">.*?</table>', s, re.S)
for table in tbs:
    tds = re.finditer(r'<td align="right">(.*?)</td>.*?<td>(.*?)</td>', table, re.S)
    for td in tds:
        print td.group(1), td.group(2)
        
"""
tbs = re.findall(r'<table.*?bgcolor="#FFFFFF">.*?</table>', s, re.S)
for table in tbs:
    title = re.search(r'<td.*?class="f1.*?">(.*?)</td>', table).group(1)
    print title
    tds = re.finditer(r'<td align="center">(.*?)</td>', table, re.S)
    for td in tds:
        print td.group(1)

d = date(2007, 3, 15)
while d < date.today():
    d += timedelta(days=1)
    
class DailyHouseStat
    ava_forward = db.ListProperty(int)        #可售房屋套数
                                              #可售房屋面积
                                              #可售住宅套数
                                              #可售住宅面积
    offered_forward = db.ListProperty(int)    #网上认购套数
                                              #网上认购面积
                                              #住宅认购套数
                                              #住宅认购面积
    signed_forward = db.ListProperty(int)     #网上签约套数
                                              #网上签约面积
                                              #住宅签约套数
                                              #住宅签约面积
    unsigned_completed = db.ListProperty(int) #未签约套数
                                              #未签约面积
                                              #未签约住宅套数
                                              #未签约住宅面积
    offered_completed = db.ListProperty(int)  #网上认购套数
                                              #网上认购面积
                                              #住宅认购套数
                                              #住宅认购面积
    signed_completed = db.ListProperty(int)   #网上签约套数
                                              #网上签约面积
                                              #住宅签约套数
                                              #住宅签约面积
    misc_completed = db.ListProperty(int)     #现房项目个数
                                              #楼栋个数
                                              #初始登记面积
    ava_resold = db.ListProperty(int)         #可售房源套数
        					                  #可售住宅套数
        					                  #可售住宅面积
    new_reg_resold = db.ListProperty(int)     #新发布房源套数
          					                  #新发布住宅套数
          					                  #新发布住宅面积
    signed_resold = db.ListProperty(int)      #网上签约套数
              					              #住宅签约套数
              					              #住宅签约面积
class MonthlyHouseStat
    approved_forward = db.ListProperty(int)   #批准预售许可证
                                              #批准预售面积
                                              #批准住宅套数
                                              #批准住宅面积
"""
