#coding:utf-8
import codecs
from itertools import chain#用于合并列表
#设置python默认编码为utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
#

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

all_text = open('test.txt').read().decode('gb2312')
if all_text.find('学号')==-1 or all_text.find('主修专业')==-1:
    #找不到学号或主修专业
    print "error"


#获取专业及年纪
stu_num = all_text[all_text.find('学号')+3:all_text.find('姓名')-2]
stu_grade = stu_num[:4]
loc_id = all_text.find('序号')#记录序号的位置
stu_major = all_text[all_text.find('主修专业')+5:loc_id-4]


#判断复制粘贴的顺序
loc_now = all_text.find('学分：')#最新结果的冒号为全角
loc_old = all_text.find('学分:')#最新结果的冒号为全角

#获取所有选课结果
result = []
if loc_now<loc_old:
    #添加最新结果
    result_list = getCource(all_text,loc_id,1)
    for x in range(1,len(result_list[0])-1):
        result.append(result_list[0][x])
    #添加以前的选课结果
    location = all_text.find('序号',result_list[1])
    while location!=-1:
        result_list = getCource(all_text,location,0)
        for x in range(2,len(result_list[0])-1):
            result.append(result_list[0][x])
        location = all_text.find('序号',result_list[1])
else :
    #添加以前的选课结果
    location = all_text.find('序号',loc_id)
    while loc_old!=-1:
        result_list = getCource(all_text,location,0)
        for x in range(2,len(result_list[0])-1):
            result.append(result_list[0][x])
        location = all_text.find('序号',result_list[1])
        loc_old = all_text.find('学分:',location)
        #序号后面找不到'学分:'则说明以前的选课结果已经获取完毕
    #添加最新结果
    result_list = getCource(all_text,location,1)
    for x in range(1,len(result_list[0])-1):
        result.append(result_list[0][x])

for i in range(0,len(result)):
        print result[i]

print stu_major
print stu_grade