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
    ava_forward = db.ListProperty(int)        #���۷�������
                                              #���۷������
                                              #����סլ����
                                              #����סլ���
    offered_forward = db.ListProperty(int)    #�����Ϲ�����
                                              #�����Ϲ����
                                              #סլ�Ϲ�����
                                              #סլ�Ϲ����
    signed_forward = db.ListProperty(int)     #����ǩԼ����
                                              #����ǩԼ���
                                              #סլǩԼ����
                                              #סլǩԼ���
    unsigned_completed = db.ListProperty(int) #δǩԼ����
                                              #δǩԼ���
                                              #δǩԼסլ����
                                              #δǩԼסլ���
    offered_completed = db.ListProperty(int)  #�����Ϲ�����
                                              #�����Ϲ����
                                              #סլ�Ϲ�����
                                              #סլ�Ϲ����
    signed_completed = db.ListProperty(int)   #����ǩԼ����
                                              #����ǩԼ���
                                              #סլǩԼ����
                                              #סլǩԼ���
    misc_completed = db.ListProperty(int)     #�ַ���Ŀ����
                                              #¥������
                                              #��ʼ�Ǽ����
    ava_resold = db.ListProperty(int)         #���۷�Դ����
        					                  #����סլ����
        					                  #����סլ���
    new_reg_resold = db.ListProperty(int)     #�·�����Դ����
          					                  #�·���סլ����
          					                  #�·���סլ���
    signed_resold = db.ListProperty(int)      #����ǩԼ����
              					              #סլǩԼ����
              					              #סլǩԼ���
class MonthlyHouseStat
    approved_forward = db.ListProperty(int)   #��׼Ԥ�����֤
                                              #��׼Ԥ�����
                                              #��׼סլ����
                                              #��׼סլ���
"""
