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

def getIndex(string):
    if string == "公共必修课" or string == '必修':
        return 0
    elif string == '公共选修课' or string == '选修':
        return 1
    elif string == '学科专业核心课':
        return 2
    elif string == '学科专业选修课':
        return 3

def DivedeAll(result):
    for i in range(0,len(result)):
        result[i] = divideInfo(result[i])

def divideInfo(Info):
    result_temp = Info.split('  ')
    if len(result_temp)<11:#正常情况下会被分割成11或12个
        result_temp = Info.split('\t')#目前发现有可能以\t分隔
        if len(result_temp)<11:
            return 0
        #其他情况先不处理...
    return result_temp

def getFailCourse(result_pre,resultFail):
    score = [0.0,0.0,0.0,0.0]
    flag = 1#标记本条数据是否被分割成11份
    for x in range(0,len(result_pre)):
        if result_pre[x]!=0:
            if result_pre[x][6]=='0':#第7个为取得学分,如果为0表示挂科
                resultFail.append([result_pre[x][3],result_pre[x][4],result_pre[x][5]])
            else :
                #判断挂科科目是否重修通过
                for fail in resultFail:
                    if fail[0]==result_pre[x][3] and fail[1]==result_pre[x][4] and fail[2]==result_pre[x][5]:
                        resultFail.remove(fail)
                score[getIndex(result_pre[x][4])] += float(result_pre[x][6])
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
        if cource_name.find(x[index])!=-1:
            return 1
    return 0
def updateType(result,profess_id,cursor,index):
    for i in range(0,len(result)):
        sql = "select * from plan where profess_id = "+str(profess_id)+" and course_name like '%"+result[i][index]+"%'"
        cursor.execute(sql)
        a = cursor.fetchall()
        if len(a)!=0:
            result[i][4] = a[0][6]
#数据库表信息
#table:gpas
#| id | profess_id | course_type     | course_grade | course_need
#table:plan
#id | profess_id | course_name                   | total_number | credit | credit_type | course_type
#table:profess
#id | year | collega   | profess
def Compare(stu_major,stu_grade,result_now,result_pre,result_fail,creditNeed):
    conn  = MySQLdb.connect(
        db = 'gobye',
        user = 'root',
        passwd = '123456',
        host = 'localhost',
        charset='utf8'
    )

    #查询专业id
    cursor = conn.cursor()
    sql = 'select * from professes where profess=\''+stu_major+'\' and year='+stu_grade
    cursor.execute(sql)
    if cursor.fetchone()==None:#找不到相关专业可能是由于未分专业
        sql = 'select * from professes where collega=\''+stu_major+'\'and year='+stu_grade
        cursor.execute(sql)
    temp  =  cursor.fetchone()
    if temp==None:#如果还找不到就说明有问题了。
        print 1
        return 0
    profess_id = temp[0]
    sql = 'select * from gpas where profess_id ='+str(profess_id)
    cursor.execute(sql)

    fetchTemp = cursor.fetchall()

    creditNeed[0] = float(fetchTemp[0][3])
    creditNeed[2] = float(fetchTemp[1][3])
    creditNeed[3] = float(fetchTemp[2][4][fetchTemp[2][4].find("要求")+2:fetchTemp[2][4].find("学分")])
    creditNeed[1] = float(fetchTemp[2][3])-creditNeed[3]
    
    #筛选未修的必修课程
    find_cource=[]
    sql = "select * from plan where profess_id = "+str(profess_id)+" and (course_type='公共必修课' or course_type='学科专业核心课')"
    cursor.execute(sql)
    a = cursor.fetchall()

    updateType(result_now,profess_id,cursor,5)#更新已修课程的课程类型
    updateType(result_pre,profess_id,cursor,3)

    i = 0
    j = 0
    for x in a:
        if not((myFind(x[2],result_now,5)==1 or myFind(x[2],result_pre,3)==1) and myFind(x[2],result_fail,0)==0):
            #not里面的条件：如果result_now和result_pre都找到了且在挂科科目中找不到说明该课已过，不用再修了
            #加个not说明该课需要修，添加到find_cource
            find_cource.append(x)
    cursor.close()
    conn.close()
    return find_cource

def Sort(CourseP, CoursePE, CourseM, CourseME, source, index, flag):
    for x in source:
        if flag == 1:
            temp = [x[1], x[2], x[3], x[6], x[4], '.']
        elif flag == 2:
            temp = [x[1], x[2], x[5], x[6], x[4], '.']
        elif flag == 0:
            temp = ["XXXXX", x[3], x[2], x[4], x[6], x[5]]
        if str(x[index]) == "公共必修课" or str(x[index]) == '必修':
            CourseP.append(temp)
        elif str(x[index]) == '公共选修课' or str(x[index]) == '选修':
            CoursePE.append(temp)
        elif str(x[index]) == '学科专业核心课':
            CourseM.append(temp)
        elif str(x[index]) == '学科专业选修课':
            CourseME.append(temp)

##################################main#############################################
all_text = open('test6.txt').read().decode('gb2312')
#删除多余换行
all_text = delSpace(all_text)

if all_text.find('学号')==-1 or all_text.find('主修专业')==-1:
    #找不到学号或主修专业
    print "error"

#获取专业及年纪
stu_num = all_text[all_text.find('学号')+3:all_text.find('姓名')-2]
stu_grade = stu_num[:4]
stu_major = all_text[all_text.find('主修专业')+5:all_text.find('序号')-1]
while stu_major.find(' ')!=-1:
    stu_major = stu_major.replace(' ','')

#获取所有选课结果
result_pre = []#记录以前的成绩
result_now = []#记录本学期选课
getAllCource(all_text,result_now,result_pre)

DivedeAll(result_now)
DivedeAll(result_pre)

#分析以前的成绩,判断挂科科目
result_fail = []#储存挂科科目.注:result_fail[0]为课程名,result_fail[1]为选修或必修,2为学分
creditGet = getFailCourse(result_pre,result_fail)#creditGet[0]为必修已获取学分,creditGet[1]为选修已获取学分
creditNeed = [0.0,0.0,0.0,0.0]

if len(result_fail)>0:
    print "挂科科目:"
    for i in result_fail:
        print "课程名:"+i[0]+"    学分类型:"+i[1]+"    学分:"+i[2]

#与培养方案比较，计算需修学分

final_result = Compare(stu_major,stu_grade,result_now,result_pre,result_fail,creditNeed)

#区分公共必修，专业必修
CourseP = []#公共必修
CourseM = []#专业必修
CoursePE = []#公共选修
CourseME = []#专业选修

if final_result==0:
    print "error"
else :
    print "主修专业:"+stu_major
    print "年级:"+stu_grade
    print "已修公共必修学分:"+str(creditGet[0])+"    已修公共选修学分:"+str(creditGet[1])+"      已修专业必修学分:"+str(creditGet[2])+"    已修专业选修学分:"+str(creditGet[3])
    print "需修公共必修学分:"+str(creditNeed[0])+"    需修公共选修学分:"+str(creditNeed[1])+"      需修专业必修学分:"+str(creditNeed[2])+"    需修专业选修学分:"+str(creditNeed[3])
    Sort(CourseP, CoursePE, CourseM, CourseME, final_result, 6, 0)
    Sort(CourseP, CoursePE, CourseM, CourseME, result_pre, 4, 1)
    Sort(CourseP, CoursePE, CourseM, CourseME, result_now, 4, 2)

    print '仍需公共必修课程:'
    for x in CourseP:
        print str(x[0])+' '+str(x[1])+' '+str(x[2])+' '+str(x[3])+' '+str(x[4])+' '+str(x[5])
    print '仍需专业必修课程:'
    for x in CourseM:
        print str(x[0])+' '+str(x[1])+' '+str(x[2])+' '+str(x[3])+' '+str(x[4])+' '+str(x[5])
    print '仍需公共选修课程:'
    for x in CoursePE:
        print str(x[0])+' '+str(x[1])+' '+str(x[2])+' '+str(x[3])+' '+str(x[4])+' '+str(x[5])
    print '仍需专业选修课程:'
    for x in CourseME:
        print str(x[0])+' '+str(x[1])+' '+str(x[2])+' '+str(x[3])+' '+str(x[4])+' '+str(x[5])


# # 输出获取结果,测试结果是否正确
# print "now:"
# for i in range(0,len(result_now)):
#     for j in range(0,len(result_now[i])):
#         print result_now[i][j]
# print "pre:"
# for i in range(0,len(result_pre)):
#     for j in range(0,len(result_pre[i])):
#         print result_pre[i][j]

