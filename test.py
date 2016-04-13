#coding:utf-8
import MySQLdb
import codecs
from itertools import chain#用于合并列表
#设置python默认编码为utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
#

def delSpace(all_text):
    while all_text.find('\r\n')!=-1:
        all_text = all_text.replace('\r\n','\n')
    while all_text.find('\n\n')!=-1:
        all_text = all_text.replace('\n\n','\n')
    return all_text

def stringCmp(string1,string2):
    if string1 == string2:
        return 1
    return 0

def divideInfo(Info):
    result_temp = Info.split('  ')
    if len(result_temp)<11:#正常情况下会被分割成11或12个
        result_temp = Info.split('\t')#目前发现有可能以\t分隔
        if len(result_temp)<11:
            return 0
        #其他情况先不处理...
    return result_temp

def getFailCourse(result_pre,resultFail):
    score = [0.0,0.0]
    flag = 1#标记本条数据是否被分割成11份
    for x in range(0,len(result_pre)):
        result_temp = divideInfo(result_pre[x])
        if result_temp!=0:
            if result_temp[6]=='0':#第7个为取得学分,如果为0表示挂科
                resultFail.append([result_temp[3],result_temp[4],result_temp[5]])
            else :
                #判断挂科科目是否重修通过
                for fail in resultFail:
                    if fail[0]==result_temp[3] and fail[1]==result_temp[4] and fail[2]==result_temp[5]:
                        resultFail.remove(fail)
                score[stringCmp(result_temp[4],'选修')] += float(result_temp[6])
    return score

def getCource(all_text,begin,type):
    #type==1为获取最新结果
    if type==1:
        loc_now = all_text.find('学分：',begin)#最新结果的冒号为全角
    else :
        loc_now = all_text.find('学分:',begin)#最新结果的冒号为全角
    temp = []
    temp.append(all_text[begin:loc_now].split('\n'))
    temp.append(loc_now)
    return temp

def getAllCource(all_text,result_now,result_pre):
    #判断复制粘贴的顺序
    loc_now = all_text.find('学分：')#最新结果的冒号为全角
    loc_old = all_text.find('学分:')#最新结果的冒号为全角

    loc_comment =  all_text.find('备注')
    if loc_now<loc_old:
        #添加最新结果
        result_list = getCource(all_text,loc_comment,1)
        for x in range(1,len(result_list[0])-1):
            if result_list[0][x].replace(' ', '')!='':
                result_now.append(result_list[0][x])
        #添加以前的选课结果
        location = all_text.find('备注',result_list[1])
        while location!=-1:
            result_list = getCource(all_text,location,0)
            for x in range(1,len(result_list[0])-1):
                if result_list[0][x].replace(' ', '')!='':
                    result_pre.append(result_list[0][x])
            location = all_text.find('备注',result_list[1])
    else :
        #添加以前的选课结果
        location = all_text.find('备注',loc_comment)
        while loc_old!=-1:
            result_list = getCource(all_text,location,0)
            for x in range(1,len(result_list[0])-1):
                if result_list[0][x].replace(' ', '')!='':
                    result_pre.append(result_list[0][x])
            location = all_text.find('备注',result_list[1])
            loc_old = all_text.find('学分:',location)
            #序号后面找不到'学分:'则说明以前的选课结果已经获取完毕
        #添加最新结果
        result_list = getCource(all_text,location,1)
        for x in range(1,len(result_list[0])-1):
            if result_list[0][x].replace(' ', '')!='':
                result_now.append(result_list[0][x])

def myFind(cource_name,source,index):#查找cource_name是否有包含source列表中的第index项
    for x in source:
        result_temp = divideInfo(x)
        if result_temp!=0:
            if cource_name.find(result_temp[index])!=-1:
                return 1
    return 0
#数据库表信息
#table:gpas
#| id | profess_id | course_type     | course_grade | course_need
#table:plan
#id | profess_id | course_name                   | total_number | credit | credit_type | course_type
#table:profess
#id | year | collega   | profess
def Compare(stu_major,stu_grade,result_now,result_pre,result_fail,elective_credits):
    result_return = []#储存返回的结果,第一项为仍需选修的学分
    conn  = MySQLdb.connect(
        db = 'gobye',
        user = 'root',
        passwd = '123456',
        host = 'localhost',
        charset='utf8'
    )

    #查询专业id
    cursor = conn.cursor()
    sql = 'select * from professes where profess=\''+stu_major+'\'and year='+stu_grade
    cursor.execute(sql)
    if cursor.fetchone()==None:#找不到相关专业可能是由于未分专业
        sql = 'select * from professes where collega=\''+stu_major+'\'and year='+stu_grade
        cursor.execute(sql)

    temp  =  cursor.fetchone()
    if temp==None:#如果还找不到就说明有问题了。
        return 0

    profess_id = temp[0]
    sql = 'select * from gpas where profess_id ='+str(profess_id)
    cursor.execute(sql)
    result_return.append(float(cursor.fetchall()[2][3])-float(elective_credits))#计算仍需选修的学分

    #筛选未修的必修课程
    find_cource=[]
    sql = "select * from plan where profess_id = "+str(profess_id)+" and (course_type='公共必修课' or course_type='学科专业核心课')"
    cursor.execute(sql)
    a = cursor.fetchall()
    i = 0
    j=0
    for x in a:
        if not((myFind(x[2],result_now,5)==1 or myFind(x[2],result_pre,3)==1) and myFind(x[2],result_fail,0)==0):
            #not里面的条件：如果result_now和result_pre都找到了且在挂科科目中找不到说明该课已过，不用再修了
            #加个not说明该课需要修，添加到find_cource
            find_cource.append(x)
    cursor.close()
    conn.close()
    result_return.append(find_cource)
    return result_return

all_text = open('test4.txt').read().decode('gb2312')
#删除多余换行
all_text = delSpace(all_text)

if all_text.find('学号')==-1 or all_text.find('主修专业')==-1:
    #找不到学号或主修专业
    print "error"

#获取专业及年纪
stu_num = all_text[all_text.find('学号')+3:all_text.find('姓名')-2]
stu_grade = stu_num[:4]
stu_major = all_text[all_text.find('主修专业')+5:all_text.find('序号')-1]

#获取所有选课结果
result_pre = []#记录以前的成绩
result_now = []#记录本学期选课
getAllCource(all_text,result_now,result_pre)

#输出获取结果,测试结果是否正确
print "now:"
for i in range(0,len(result_now)):
    print result_now[i]
print "pre:"
for i in range(0,len(result_pre)):
    print result_pre[i]

print "主修专业:"+stu_major
print "年级:"+stu_grade
#

#分析以前的成绩,判断挂科科目
result_fail = []#储存挂科科目.注:result_fail[0]为课程名,result_fail[1]为选修或必修,2为学分
score = getFailCourse(result_pre,result_fail)#score[0]为必修已获取学分,score[1]为选修已获取学分

print "已修必修学分:"+str(score[0])+"    已修选修学分:"+str(score[1])

if len(result_fail)>0:
    print "挂科科目:"
    for i in result_fail:
        print "课程名:"+i[0]+"    学分类型:"+i[1]+"    学分:"+i[2]

#与培养方案比较，计算需修学分\
final_result = Compare(stu_major,stu_grade,result_now,result_pre,result_fail,score[1])
if final_result==0:
    print "error"
else :
    print '仍需选修学分:'+str(final_result[0])

    print '仍需必修课程:'
    for x in final_result[1]:
        print str(x[0])+' '+str(x[1])+' '+str(x[2])+' '+str(x[3])+' '+str(x[4])+' '+str(x[5])+' '+str(x[6])



