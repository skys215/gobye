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
re_del_html = re.compile(r'<[^>]+>',re.S)
re_op_value = re.compile(r'[\d]+')
re_profess = re.compile(r'级，.+')
re_collega = re.compile(r'.+，?')
all_collega_no = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','22','24','30']
for each_op in all_grade_option:
    
    grade = re_op_value.findall(str(each_op))
    if(grade[0]=='00'):
        continue
    for collega_no in all_collega_no:
        
        url = 'http://192.168.2.224/pyfa/view_pyfa.asp?nj='+grade[0]+'&xydh='+collega_no
        request = urllib.request.urlopen(url)
        reader = request.read()
        
        soup = BeautifulSoup(reader,'html.parser')
        all_profess_detail = soup.find_all('td',class_='ncontents')
        if all_profess_detail:
            for profess_detail in all_profess_detail:
                detail = re_profess.findall(profess_detail.a.text)
                collega = profess_detail.a.text.split('，')[0]
                profess = detail[0].replace(" ","")[2:]
                url = 'http://192.168.2.224/pyfa/'+profess_detail.a.get('href')[2:]
                print (url)
                request = urllib.request.urlopen(url)
                reader = request.read()
                
                soup = BeautifulSoup(reader,'html.parser')
                try:#有些专业没辅修啊，没辅修啊，没辅修啊
                    all_course_table = soup.find('table',id='fb4').find_all('td',class_='ncontents')
                except:
                    continue
                conn = pymysql.Connect(
                                        user = 'root',
                                        db='gobye',
                                        charset='utf8')
                cursor = conn.cursor()
                sql = 'select id from professes where year='+grade[0]+' and collega="'+collega+'" and profess="'+profess+'"'
                cursor.execute(sql)
                profess_id = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                #搜索专业ID并存储在profess_id下    
                count = 1
                for each_course in all_course_table:
                    if (count%17==3):
                        course_name = each_course.text.strip()
                    if (count%17==2):
                        total_number = each_course.text.strip()
                    if (count%17==5):
                        credit = each_course.text.strip()
                    if (count%17==16):
                        credit_type = each_course.text.strip()
                        
                        
                        if(course_name==''):
                            continue
                        conn = pymysql.Connect(
                                               user = 'root',
                                               db='gobye',
                                               charset='utf8')
                        cursor = conn.cursor()
                        sql = 'insert into plan(profess_id,course_name,total_number,credit,credit_type,course_type) values('+str(profess_id)+',"'+str(course_name)+'","'+str(total_number)+'","'+str(credit)+'","'+str(credit_type)+'","辅修课程")'
                        print (sql)
                        cursor.execute(sql)
                        conn.commit()
                        cursor.close()
                        conn.close()
                    count = count +1
                        
                
                

                            
                        
        
                
                
                