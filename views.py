#coding:utf8
from django.shortcuts import render

from django.http import HttpResponse
# Create your views here.
from stucampus.gobye.models import gpas
from datadeal import delSpace,getIndex,DivedeAll,divideInfo,getFailCourse,getCource,getAllCource,myFind,updateType,Compare,Sort
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def index(request):
    return render(request, 'gobye/login.html')

def result(request):
    if request.method =="POST":
        top_info = request.POST.get('select-course')
        bottom_info = request.POST.get('grade')
    
    all_text = top_info.decode('utf-8')+bottom_info.decode('utf-8') 
	# all_text = open('test.txt').read().decode('gb2312')
    #删除多余换行
    all_text = delSpace(all_text)

    if all_text.find(u'学号')==-1 or all_text.find(u'主修专业')==-1:
        return HttpResponse("找不到学号或主修专业")

    #获取专业及年纪
    stu_num = all_text[all_text.find(u'学号')+3:all_text.find(u'姓名')-2]
    stu_grade = stu_num[:4]
    stu_major = all_text[all_text.find(u'主修专业')+5:all_text.find(u'序号')-1]
    while stu_major.find(' ')!=-1:
        stu_major = stu_major.replace(' ','')

    try:
        #获取所有选课结果
        result_pre = []#记录以前的成绩
        result_now = []#记录本学期选课
        getAllCource(all_text,result_now,result_pre)
        DivedeAll(result_now)
        DivedeAll(result_pre)

        #分析以前的成绩,判断挂科科目
        result_fail = []#储存挂科科目.注:result_fail[0]为课程名,result_fail[1]为选修或必修,2为学分
        creditNeed = [0.0,0.0,0.0,0.0]

        #与培养方案比较，计算需修学分

        final_result = Compare(stu_major,stu_grade,result_now,result_pre,result_fail,creditNeed)

        creditGet = getFailCourse(result_now, result_pre,result_fail)#creditGet[0]为必修已获取学分,creditGet[1]为选修已获取学分
        #区分公共必修，专业必修
        CourseP = []#公共必修
        CourseM = []#专业必修
        CoursePE = []#公共选修
        CourseME = []#专业选修

        if final_result==0:
            print "error2"
        else :
            #print "主修专业:"+stu_major
            #print "年级:"+stu_grade
            #print "已修公共必修学分:"+str(creditGet[0])+"    已修公共选修学分:"+str(creditGet[1])+"      已修专业必修学分:"+str(creditGet[2])+"    已修专业选修学分:"+str(creditGet[3])
            #print "需修公共必修学分:"+str(creditNeed[0])+"    需修公共选修学分:"+str(creditNeed[1])+"      需修专业必修学分:"+str(creditNeed[2])+"    需修专业选修学分:"+str(creditNeed[3])
            result_final = []
            for each_final in final_result:
                each_result = []
                each_result.append(each_final.id)
                each_result.append(each_final.profess_id)
                each_result.append(each_final.course_name)
                each_result.append(each_final.total_number)
                each_result.append(each_final.credit)
                each_result.append(each_final.credit_type)
                each_result.append(each_final.course_type)
                result_final.append(each_result)
                
            Sort(CourseP, CoursePE, CourseM, CourseME, result_final, 6, 0)
            Sort(CourseP, CoursePE, CourseM, CourseME, result_pre, 4, 1)
            Sort(CourseP, CoursePE, CourseM, CourseME, result_now, 4, 2)

        creditLack = [creditNeed[0] - creditGet[0],creditNeed[1] - creditGet[1],creditNeed[2] - creditGet[2],creditNeed[3] - creditGet[3]]
        lack = creditLack[0]+creditLack[1]+creditLack[2]+creditLack[3]

    except :
        return HttpResponse("Error")

    # if len(result_fail)>0:
    #     print "挂科科目:"
    #     for i in result_fail:
    #         print "课程名:"+i[0]+"    学分类型:"+i[1]+"    学分:"+i[2]

    return render(request, 'gobye/result.html',{'CourseP':CourseP,'CourseM':CourseM,'CoursePE':CoursePE,'CourseME':CourseME,'creditGet':creditGet,'creditNeed':creditNeed,'lack':lack,'creditLack':creditLack})