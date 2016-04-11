#coding:gb18030
from bs4 import BeautifulSoup
import http.cookiejar
import urllib.request
import re
import pymysql

url = 'http://192.168.2.224/pyfa/view_pyfa.asp'
cookiejar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))
urllib.request.install_opener(opener)
request = urllib.request.urlopen(url)
reader = request.read()

soup = BeautifulSoup(reader,'html.parser')
all_grade_option = soup.find_all('option')
re_profess = re.compile(r'级，.+')
re_collega = re.compile(r'.+，?')
re_op_value = re.compile(r'[\d]+')
all_collega_no = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','22','24','30']
for each_op in all_grade_option:
    
    grade = re_op_value.findall(str(each_op))
    if(grade[0]=='00'):
        continue
    for collega_no in all_collega_no:
        url = 'http://192.168.2.224/pyfa/view_pyfa.asp?nj='+grade[0]+'&xydh='+collega_no
        #grade[0]锟疥级 collega学院
        request = urllib.request.urlopen(url)
        reader = request.read()
        #reader = reader.decode('utf-8')
        
        soup = BeautifulSoup(reader,'html.parser')
        all_profess_detail = soup.find_all('td',class_='ncontents')
        if all_profess_detail:
            for profess_detail in all_profess_detail:
                detail = re_profess.findall(profess_detail.a.text)
                collega = profess_detail.a.text.split('，')[0]
                profess = detail[0].replace(" ","")[2:]
                #profess~专业你懂的-
                print ('http://192.168.2.224/pyfa/'+profess_detail.a.get('href')[2:])
                
                conn = pymysql.Connect(
                                user = 'root',
                                db='gobye',
                                charset='utf8')
                cursor = conn.cursor()
                sql_insert = 'insert into professes(year,collega,profess) values('+grade[0]+',"'+collega+'","'+profess+'")'
                cursor.execute(sql_insert)
                conn.commit()
                cursor.close()
                conn.close()
                

        
    


