#coding:utf-8
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

def getFailCourse(result_pre,resultFail):
    score = [0.0,0.0]
    flag = 1#标记本条数据是否被分割成11份
    for x in range(0,len(result_pre)):
        result_temp = result_pre[x].split('  ')
        if len(result_temp)<11:#正常情况下会被分割成11或12个
            result_temp = result_pre[x].split('\t')#目前发现有可能以\t分隔
            if len(result_temp)<11:
                flag=0
            #其他情况先不处理...

        if flag==1:
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

all_text = open('test.txt').read().decode('gb2312')
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

print "挂科科目:"
for i in result_fail:
    print "课程名:"+i[0]+"    学分类型:"+i[1]+"    学分:"+i[2]