# -*- coding: utf-8 -*-
# import MySQLdb
from stucampus.gobye.models import gpas,professes,plan
import codecs
from itertools import chain#用于合并列表
from django.db.models import Q
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

#将数据分割为数组
def divideInfo(Info):
    result_temp = Info.split('  ')
    if len(result_temp)<11:#正常情况下会被分割成11或12个
        result_temp = Info.split('\t')#目前发现有可能以\t分隔
        if len(result_temp)<11:
            return 0
    result_temp[6] = float(result_temp[6])
        #其他情况先不处理...
    return result_temp

#查找挂科科目,并统计已修学分
def getFailCourse(result_now, result_pre,resultFail):
    score = [0.0,0.0,0.0,0.0]
    for x in range(0,len(result_pre)):
        if result_pre[x]!=0:
            if result_pre[x][6]=='0':#第7个为取得学分,如果为0表示挂科
                resultFail.append([result_pre[x][3],result_pre[x][4],result_pre[x][5],result_pre[x][2]])
            else :
                #判断挂科科目是否重修通过
                for fail in resultFail:
                    if fail[0]==result_pre[x][3] and fail[1]==result_pre[x][4] and fail[2]==result_pre[x][5]:
                        resultFail.remove(fail)
                score[getIndex(result_pre[x][4])] += float(result_pre[x][6])
   
    #统计最新选课结果的学分,并查找是否重修挂科科目
    for x in range(0,len(result_now)):
        if result_now[x]!=0:
            #判断挂科科目是否重修
            for fail in resultFail:
                if fail[0]==result_now[x][5] and fail[1]==result_pre[x][4] and fail[2]==result_pre[x][6]:
                    resultFail.remove(fail)
            score[getIndex(result_now[x][4])] += float(result_now[x][6])
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

    ################一下注释代码为不判断粘贴顺序#########
    # loc_comment =  all_text.find('备注')
    # # if loc_now<loc_old:
    #     #添加最新结果
    # result_list = getCource(all_text,loc_comment,1)
    # for x in range(1,len(result_list[0])-1):
    #     if result_list[0][x].replace(' ', '')!='':
    #         result_now.append(result_list[0][x])
    # #添加以前的选课结果
    # location = all_text.find('备注',result_list[1])
    # while location!=-1:
    #     result_list = getCource(all_text,location,0)
    #     for x in range(1,len(result_list[0])-1):
    #         if result_list[0][x].replace(' ', '')!='':
    #             result_pre.append(result_list[0][x])
    #     location = all_text.find('备注',result_list[1])

#判断课程(course_name,course_num)是否已修,已修返回1
def myFind(course_name, course_num,result_now, result_pre, result_fail):
    if course_name.find("体育俱乐部")!=-1:#体育学分特殊处理
        for x in result_now:
            if x[5].find("俱乐部")!=-1:
                return 1
        for x in result_pre:
            if x[3].find("俱乐部")!=-1:
                return 1
        for x in result_fail:
            if x[0].find("俱乐部")==-1:
                return 1
    else :
        #通过对比课程号和课程名来匹配课程。
        for x in result_now:
            if x[2].find(course_num)!=-1 or course_name.find(x[5])!=-1:
                return 1
        for x in result_pre:
            if x[2].find(course_num)!=-1 or course_name.find(x[3])!=-1:
                return 1
        for x in result_fail:
            if x[3].find(course_num)!=-1 or course_name.find(x[0])==-1:
                return 1
    return 0

def updateType(result,profess_id,index):
    for i in range(0,len(result)):
        iget = plan.objects.filter(Q(profess_id=profess_id)).filter(course_name__contains=str(result[i][index]))
        a = iget
        if a:
            result[i][4] = a[0].course_type

#去除课程的英文名。
def Format(find_cource):
    alpha = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', ',Z']
    for x in find_cource:
        x.credit = float(x.credit)
        i = 999
        for a in alpha:
            j = x.course_name.find(a)
            if j!=-1 and j<i and x.course_name[j:].count(')')<2:
                i = j
        x.course_name = x.course_name[:i]

def Compare(stu_major,stu_grade,result_now,result_pre,result_fail,creditNeed):
    iget = professes.objects.filter(year = stu_grade).filter(profess = stu_major)

    if not iget:#找不到相关专业可能是由于未分专业
        iget = professes.objects.filter(year = stu_grade).filter(collega = stu_major)
    if not iget:#如果还找不到就说明有学分了。
        print 1
        return 0

    profess_id = iget[0].id

    iget = gpas.objects.filter(profess_id=str(profess_id))

    creditNeed[0] = float(iget[0].course_grade)
    creditNeed[2] = float(iget[1].course_grade)
    creditNeed[3] = float(iget[2].course_need[iget[2].course_need.find("要求")+2:iget[2].course_need.find("学分")])
    creditNeed[1] = float(iget[2].course_grade)-creditNeed[3]

    find_course=[]
    iget = plan.objects.filter(profess_id=str(profess_id)).filter(Q(course_type='公共必修课')|Q(course_type='学科专业核心课'))
    a = list(iget)
    for x in a:
        find_course.append(x)
    
    updateType(result_now,profess_id,5)#更新已修课程的课程类型
    updateType(result_pre,profess_id,3)

    i = 0
    j = 0
    for x in a:
        if myFind(x.course_name,x.total_number, result_now, result_pre, result_fail)==1:
            find_course.remove(x)
    
    Format(find_course)

    return find_course

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