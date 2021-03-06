# coding: UTF-8
from django.db.models import Q

import xlwt,random
import os,sys, re
import datetime
from backend.logging import loginfo
from users.models import TeacherProfile
from teacher.models import TeacherInfoSetting,ProgressReport,ProjectAchivement
from adminStaff.models import ProjectSingle,Re_Project_Expert
from common.models import ProjectMember,BasisContent
from common.utils import getScoreTable
from settings import TMP_FILES_PATH,MEDIA_URL
from const import *
from common.utils import getScoreTable, getScoreForm,getFinalScoreTable,getFinalScoreForm

def get_xls_path(request,exceltype,proj_set,specialname="",eid="",year=-1):
    """
        exceltype = EXCELTYPE_DICT 导出表类型
        proj_set 筛选出导出的项目集
        specialtype 基本科研业务经费科研专题项目的
    """

    loginfo(p=proj_set,label="get_xls_path")
    loginfo(p = exceltype,label = "exceltype")
    print exceltype
    EXCELTYPE_DICT = EXCELTYPE_DICT_OBJECT()
    if exceltype == "achievementInfo":
        file_path = xls_info_conclusionresult(request, proj_set, year)
    elif exceltype == EXCELTYPE_DICT.INFO_COLLECTION:
        file_path = xls_info_collection(request,proj_set,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_FUNDSUMMARY:
        file_path = xls_info_fundsummay(request,proj_set,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_SUMMARY:
        file_path = xls_info_summary(request,proj_set,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_FUNDBUDGET:
        file_path = xls_info_fundbudget(request,proj_set,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_TEACHERINFO:
        file_path = xls_info_teacherinfo(request,eid)
    #初审表
    elif exceltype == EXCELTYPE_DICT.INFO_BASESUMMARYSCIENCE_PREVIEW:
        file_path = xls_info_basesummary_preview(request,proj_set,1,specialname,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_FRONT_PREVIEW:
        file_path = xls_info_basesummary_preview(request,proj_set,2,specialname,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_OUTSTANDING_PREVIEW:
        file_path = xls_info_basesummary_preview(request,proj_set,3,specialname,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_HUMANITY_PREVIEW:
        file_path = xls_info_humanity_preview(request,proj_set,eid,1)
    elif exceltype == EXCELTYPE_DICT.INFO_IMPORTANTPROJECT_PREVIEW:
        file_path = xls_info_importantproject_preivew(request,proj_set,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_LABORATORY_PREVIEW:
        file_path = xls_info_laboratory_preview(request,proj_set,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_BASESUMMARY_PREVIEW:
        file_path = xls_info_humanity_preview(request,proj_set,eid,2)
    #终审表
    elif exceltype == EXCELTYPE_DICT.INFO_FINAL_BASESUMMARY_PREVIEW:
        file_path = xls_info_humanity_preview(request,proj_set,eid,2)
    elif exceltype == EXCELTYPE_DICT.INFO_FINAL_HUMANITY_PREVIEW:
        file_path = xls_info_humanity_preview(request,proj_set,eid,1)
    elif exceltype == EXCELTYPE_DICT.INFO_FINAL_IMPORTANTPROJECT_PREVIEW:
        file_path = xls_info_importantproject_preivew(request,proj_set,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_FINAL_LABORATORY_PREVIEW:
        file_path = xls_info_laboratory_preview(request,proj_set,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_FINAL_BASESUMMARYSCIENCE_PREVIEW:
        file_path = xls_info_basesummary_preview(request,proj_set,1,specialname,eid)
    elif exceltype == EXCELTYPE_DICT.INFO_FINAL_FRONT_PREVIEW:
        #前沿交叉终审表
        file_path = xls_info_final_front_preview(request,proj_set)     
    else:#EXCELTYPE_DICT.INFO_FINAL_OUTSTANDING_PREVIEW
        file_path = xls_info_basesummary_preview(request,proj_set,3,specialname,eid)      
    return MEDIA_URL + "tmp" + file_path[len(TMP_FILES_PATH):]


def xls_info_fundbudget_gen():
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')
    style = cell_style(horizontal=True,vertical=True)
    # generate header
    worksheet.write_merge(0, 0, 0, 10, '项目预算支出总和表',style)

    # generate body
    worksheet.write_merge(1, 1, 0, 0 ,'流水号')
    worksheet.write_merge(1, 1, 1, 1 ,'项目编号')
    worksheet.write_merge(1, 1, 2, 2 ,'项目名称')
    worksheet.write_merge(1, 1, 3, 3 ,'项目负责人')
    worksheet.write_merge(1, 1, 4, 4 ,'学院')
    worksheet.write_merge(1, 1, 5, 5 ,'立项年度')
    worksheet.write_merge(1, 1, 6, 6 ,'专题类型')
    worksheet.write_merge(1, 1, 7, 7 ,'支出总和')
    worksheet.write(1,8,"设备费预算")
    worksheet.write(1,9,"材料费预算")
    worksheet.write(1,10,"测试化验加工预算费预算")
    worksheet.write(1,11,"燃料动力费预算")
    worksheet.write(1,12,"差旅费预算")
    worksheet.write(1,13,"会议费预算")
    worksheet.write(1,14,"国际合作与交流费预算")
    worksheet.write(1,15,"出版费预算")
    worksheet.write(1,16,"劳务费预算")
    worksheet.write(1,17,"专家咨询费预算")

    worksheet.col(1).width = len('项目编号') * 400
    worksheet.col(2).width = len('项目名称') * 800
    return worksheet, workbook

def xls_info_fundbudget(request,proj_set,eid):
    """
    """

    xls_obj, workbook = xls_info_fundbudget_gen()

    proj_set = proj_set.order_by("projectfundbudget__serial_number")
    _number= 1
    
    for proj_obj in proj_set:
        teacher = TeacherProfile.objects.get(id = proj_obj.teacher.id)
        manager = teacher.teacherinfosetting
        row = 1 + _number
        xls_obj.write(row, 0, unicode(proj_obj.projectfundbudget.serial_number))
        xls_obj.write(row, 1, unicode(proj_obj.project_code)) 
        xls_obj.write(row, 2, unicode(proj_obj.title))
        xls_obj.write(row, 3, unicode(manager.name))
        xls_obj.write(row, 4, unicode(proj_obj.teacher.college))
        xls_obj.write(row, 5, unicode(proj_obj.approval_year))
        xls_obj.write(row, 6, unicode(proj_obj.project_special))
        xls_obj.write(row, 7, unicode(proj_obj.projectfundbudget.total_budget))
        xls_obj.write(row,8,unicode(int(proj_obj.projectfundbudget.equacquisition_budget)+int(proj_obj.projectfundbudget.equtrial_budget)+int(proj_obj.projectfundbudget.equrent_budget)))
        xls_obj.write(row,9,unicode(proj_obj.projectfundbudget.material_budget))
        xls_obj.write(row,10,unicode(proj_obj.projectfundbudget.testcosts_budget))
        xls_obj.write(row,11,unicode(proj_obj.projectfundbudget.fuelpower_budget))
        xls_obj.write(row,12,unicode(proj_obj.projectfundbudget.travel_budget))
        xls_obj.write(row,13,unicode(proj_obj.projectfundbudget.conference_budget))
        xls_obj.write(row,14,unicode(proj_obj.projectfundbudget.cooperation_budget))
        xls_obj.write(row,15,unicode(proj_obj.projectfundbudget.publish_budget))
        xls_obj.write(row,16,unicode(proj_obj.projectfundbudget.laborcosts_budget))
        xls_obj.write(row,17,unicode(proj_obj.projectfundbudget.expertadvice_budget))

        _number+= 1
    # write xls file
    save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年大连理工大学项目预算支出总和表"))
    workbook.save(save_path)
    return save_path


def xls_info_fundsummay_gen():
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')
    style = cell_style(horizontal=True,vertical=True)
    # generate header
    worksheet.write_merge(0, 0, 0, 10, '项目决算金额总和表',style)

    # generate body
    worksheet.write_merge(1, 1, 0, 0, '流水号')
    worksheet.write_merge(1, 1, 1, 1, '项目编号')
    worksheet.write_merge(1, 1, 2, 2, '项目名称')
    worksheet.write_merge(1, 1, 3, 3, '项目负责人')
    worksheet.write_merge(1, 1, 4, 4, '学院')
    worksheet.write_merge(1, 1, 5, 5, '立项年度')
    worksheet.write_merge(1, 1, 6, 6, '专题类型')
    worksheet.write_merge(1, 1, 7, 7, '预算金额')
    worksheet.write_merge(1, 1, 8, 8, '决算金额')
    worksheet.write_merge(1, 1, 9, 9, '结余金额')
    worksheet.write(1,10,"设备费支出")
    worksheet.write(1,11,"材料费支出")
    worksheet.write(1,12,"测试化验加工预算费支出")
    worksheet.write(1,13,"燃料动力费支出")
    worksheet.write(1,14,"差旅费支出")
    worksheet.write(1,15,"会议费支出")
    worksheet.write(1,16,"国际合作与交流费支出")
    worksheet.write(1,17,"出版费支出")
    worksheet.write(1,18,"劳务费支出")
    worksheet.write(1,19,"专家咨询费支出")

    worksheet.col(1).width = len('项目编号') * 400
    worksheet.col(2).width = len('项目名称') * 800
    
    return worksheet, workbook

def xls_info_fundsummay(request,proj_set,eid):
    """
    """

    xls_obj, workbook = xls_info_fundsummay_gen()
    proj_set = proj_set.order_by("projectfundsummary__serial_number")
    _number= 1
    for proj_obj in proj_set:
        teacher = TeacherProfile.objects.get(id = proj_obj.teacher.id)
        manager = teacher.teacherinfosetting
        loginfo(p=manager,label="manager")
        row = 1 + _number
        xls_obj.write(row, 0, unicode(proj_obj.projectfundsummary.serial_number))
        xls_obj.write(row, 1, unicode(proj_obj.project_code))
        xls_obj.write(row, 2, unicode(proj_obj.title))
        xls_obj.write(row, 3, unicode(manager.name))
        xls_obj.write(row, 4, unicode(proj_obj.teacher.college))
        xls_obj.write(row, 5, unicode(proj_obj.approval_year))
        xls_obj.write(row, 6, unicode(proj_obj.project_special))
        xls_obj.write(row, 7, unicode(proj_obj.projectfundsummary.total_budget))
        xls_obj.write(row, 8, unicode(proj_obj.projectfundsummary.total_expenditure))
        xls_obj.write(row, 9, unicode(int(proj_obj.projectfundsummary.total_budget)-int(proj_obj.projectfundsummary.total_expenditure)))
        xls_obj.write(row, 10, unicode(int(proj_obj.projectfundsummary.equacquisition_expenditure)+int(proj_obj.projectfundsummary.equtrial_expenditure)+int(proj_obj.projectfundsummary.equrent_expenditure)))
        xls_obj.write(row,11,unicode(proj_obj.projectfundsummary.material_expenditure))
        xls_obj.write(row,12,unicode(proj_obj.projectfundsummary.testcosts_expenditure))
        xls_obj.write(row,13,unicode(proj_obj.projectfundsummary.fuelpower_expenditure))
        xls_obj.write(row,14,unicode(proj_obj.projectfundsummary.travel_expenditure))
        xls_obj.write(row,15,unicode(proj_obj.projectfundsummary. conference_expenditure))
        xls_obj.write(row,16,unicode(proj_obj.projectfundsummary.cooperation_expenditure))
        xls_obj.write(row,17,unicode(proj_obj.projectfundsummary.publish_expenditure))
        xls_obj.write(row,18,unicode(proj_obj.projectfundsummary.laborcosts_expenditure))
        xls_obj.write(row,19,unicode(proj_obj.projectfundsummary.expertadvice_expenditure))
        _number+= 1
    # write xls file
    save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年大连理工大学项目决金额总和表"))
    workbook.save(save_path)
    return save_path



def xls_info_laboratory_preview_gen(request):
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')
    style = cell_style(horizontal=True,vertical=True)
    # generate header
    worksheet.write_merge(0, 0, 0,5 + EXPERT_NUM ,"%s%s" % (str(datetime.date.today().year), "年度大连理工大学基本科研业务费重点实验室科研专题项目申请评审结果汇总表"),style)
    # generate body
    worksheet.write_merge(1, 1, 0, 0, '序号')
    worksheet.write_merge(1, 1, 1, 1, '项目名称')
    worksheet.write_merge(1, 1, 2, 2, '申请人')
    worksheet.col(2).width = len('项目名称') * 400
    worksheet.write_merge(1, 1, 3, 3, '金额(万)')
    for i in range(0,EXPERT_NUM):
        add_col = i 
        worksheet.write_merge(1,1,4+add_col,4+add_col,'专家'+str(i + 1))
    worksheet.write_merge(1, 1, 4 + EXPERT_NUM, 4 + EXPERT_NUM, '平均分1')
    worksheet.write_merge(1, 1, 5 + EXPERT_NUM, 5 + EXPERT_NUM, '平均分2')
    worksheet.write_merge(1, 1, 6 + EXPERT_NUM, 6 + EXPERT_NUM, '平均分3')


    return worksheet, workbook

def xls_info_laboratory_preview(request,proj_set,specialtype="",eid=""):
    """
    """

    xls_obj, workbook = xls_info_laboratory_preview_gen(request)

    _number= 1
    index = 1
    for proj_obj in proj_set:
        teacher = TeacherProfile.objects.get(id = proj_obj.teacher.id)
        manager = teacher.teacherinfosetting
        re_project_expert_list = Re_Project_Expert.objects.filter(project_id = proj_obj)
        
        row = 1 + _number
        xls_obj.write(row, 0, unicode(index)) 
        xls_obj.write(row, 1, unicode(proj_obj.title)) 
        xls_obj.write(row, 2, unicode(manager.name))
        xls_obj.write(row, 3, unicode(proj_obj.projectfundsummary.total_budget))
        i = 0
        score_list = []
        average_score_1 = 0
        average_score_2 = 0
        average_score_3 = 0
        for re_expert_temp in re_project_expert_list:
            if eid==TYPE_ALLOC[0]:
                score_table = getScoreTable(re_expert_temp.project).objects.get_or_create(re_obj = re_expert_temp)[0]
            if eid == TYPE_FINAL_ALLOC[0]:
                score_table = getFinalScoreTable(re_expert_temp.project).objects.get_or_create(re_obj = re_expert_temp)[0]
            if score_table.get_total_score():
                xls_obj.write(row,4 + i,unicode(score_table.get_total_score()))
                score_list.append(score_table.get_total_score())
                i += 1
        average_score_1 = average(score_list)
        if (len(score_list) > 4):
            score_list=delete_max_and_min(score_list)
            average_score_2 = average(score_list)
            score_list=delete_max_and_min(score_list)
            average_score_3 = average(score_list)
        xls_obj.write(row, 4+EXPERT_NUM,unicode(average_score_1))
        xls_obj.write(row, 5+EXPERT_NUM,unicode(average_score_2))
        xls_obj.write(row, 6+EXPERT_NUM,unicode(average_score_3))
        _number+= 1
        index += 1

    # write xls file
    if eid==TYPE_ALLOC[0]:
        save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年度大连理工大学基本科研业务费重点实验室科研专题项目申请初审结果汇总表"))
    if eid == TYPE_FINAL_ALLOC[0]:
        save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年度大连理工大学基本科研业务费重点实验室科研专题项目申请终审结果汇总表"))
    workbook.save(save_path)
    return save_path


def xls_info_importantproject_preivew_gen(request):
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')
    style = cell_style(horizontal=True,vertical=True)
    # generate header
    worksheet.write_merge(0, 0, 0,5 + EXPERT_NUM ,"%s%s" % (str(datetime.date.today().year), "年大连理工大学基本科研业务费重大项目培育科研专题项目申请评审结果汇总表"),style)
    # generate body
    worksheet.write_merge(1, 1, 0, 0, '序号')
    worksheet.write_merge(1, 1, 1, 1, '项目名称')
    worksheet.write_merge(1, 1, 2, 2, '申请人')
    worksheet.col(2).width = len('项目名称') * 400
    worksheet.write_merge(1, 1, 3, 3, '金额(万)')
    for i in range(0,EXPERT_NUM):
        add_col = i 
        worksheet.write_merge(1,1,4+add_col,4+add_col,'专家'+str(i + 1))
    worksheet.write_merge(1, 1, 4 + EXPERT_NUM, 4 + EXPERT_NUM, '平均分1')
    worksheet.write_merge(1, 1, 5 + EXPERT_NUM, 5 + EXPERT_NUM, '平均分2')
    worksheet.write_merge(1, 1, 6 + EXPERT_NUM, 6 + EXPERT_NUM, '平均分3')

    return worksheet, workbook

def xls_info_importantproject_preivew(request,proj_set,specialtype="",eid=""):
    """
    """

    xls_obj, workbook = xls_info_importantproject_preivew_gen(request)
    _number= 1
    index = 1
    for proj_obj in proj_set:
        teacher = TeacherProfile.objects.get(id = proj_obj.teacher.id)
        manager = teacher.teacherinfosetting
        re_project_expert_list = Re_Project_Expert.objects.filter(project_id = proj_obj)
        row = 1 + _number
        xls_obj.write(row, 0, unicode(index)) 
        xls_obj.write(row, 1, unicode(proj_obj.title)) 
        xls_obj.write(row, 2, unicode(manager.name))
        xls_obj.write(row, 3, unicode(proj_obj.projectfundsummary.total_budget))
        i = 0
        score_list = []
        average_score_1 = 0
        average_score_2 = 0
        average_score_3 = 0
        for re_expert_temp in re_project_expert_list:
            if eid==TYPE_ALLOC[0]:
                score_table = getScoreTable(re_expert_temp.project).objects.get_or_create(re_obj = re_expert_temp)[0]
            if eid == TYPE_FINAL_ALLOC[0]:
                score_table = getFinalScoreTable(re_expert_temp.project).objects.get_or_create(re_obj = re_expert_temp)[0]
            if score_table.get_total_score():
                xls_obj.write(row,4 + i,unicode(score_table.get_total_score()))
                score_list.append(score_table.get_total_score())
                i += 1
        average_score_1 = average(score_list)
        if (len(score_list) > 4):
            score_list=delete_max_and_min(score_list)
            average_score_2 = average(score_list)
            score_list=delete_max_and_min(score_list)
            average_score_3 = average(score_list)
        xls_obj.write(row, 4+EXPERT_NUM,unicode(average_score_1))
        xls_obj.write(row, 5+EXPERT_NUM,unicode(average_score_2))
        xls_obj.write(row, 6+EXPERT_NUM,unicode(average_score_3))

        _number+= 1
        index += 1
    # write xls file
    if eid==TYPE_ALLOC[0]:
        save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年大连理工大学基本科研业务费重大项目培育科研专题项目申请初审结果汇总表"))
    if eid == TYPE_FINAL_ALLOC[0]:
        save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年大连理工大学基本科研业务费重大项目培育科研专题项目申请终审结果汇总表"))
    workbook.save(save_path)
    return save_path


def xls_info_humanity_preview_gen(request,str1):
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')
    style = cell_style(horizontal=True,vertical=True)
    # generate header
    worksheet.write_merge(0, 0, 0,5 + EXPERT_NUM ,"%s%s" % (str(datetime.date.today().year), "年大连理工大学基本科研业务费%s项目申请评审结果汇总表"%str1),style)
    # generate body
    worksheet.write_merge(1, 1, 0, 0, '序号')
    worksheet.write_merge(1, 1, 1, 1, '项目名称')
    worksheet.write_merge(1, 1, 2, 2, '申请人')
    worksheet.col(2).width = len('项目名称') * 400
    worksheet.write_merge(1, 1, 3, 3, '金额(万)')
    for i in range(0,EXPERT_NUM):
        add_col = i 
        worksheet.write_merge(1,1,4+add_col,4+add_col,'专家'+str(i + 1))
    worksheet.write_merge(1, 1, 4 + EXPERT_NUM, 4 + EXPERT_NUM, '平均分1')
    worksheet.write_merge(1, 1, 5 + EXPERT_NUM, 5 + EXPERT_NUM, '平均分2')


    return worksheet, workbook

def xls_info_final_front_preview_gen(request,max_expert_num=EXPERT_NUM):
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet("sheet1")
    style =cell_style(horizontal=True,vertical=True)
    worksheet.write_merge(0,0,0,5+2*max_expert_num,"%s%s"%(str(datetime.date.today().year), "年大连理工大学基本科研业务费前沿交叉学科基础科研业务费终审结果汇总表"),style)
    worksheet.write_merge(1, 2, 0, 0, '序号',style)
    worksheet.write_merge(1, 2, 1, 1, '项目名称',style)
    worksheet.write_merge(1, 2, 2, 2, '申请人',style)
    worksheet.col(1).width = len('项目名称') * 800
    worksheet.write_merge(1, 2, 3, 3, '金额(万)',style)
    for i in range(0,max_expert_num):
        add_col = i*2
        worksheet.write_merge(1,1,4+add_col,5+add_col,'专家'+str(i + 1),style)
        worksheet.write_merge(2,2,4+add_col,4+add_col,'评分',style)
        worksheet.write_merge(2,2,5+add_col,5+add_col,'交叉程度(%)',style)
    worksheet.write_merge(1, 2, 4 + max_expert_num*2, 4 + max_expert_num*2, '平均分',style)
    worksheet.write_merge(1, 2, 5 + max_expert_num*2, 5 + max_expert_num*2, '平均交叉程度(%)',style)
    return worksheet,workbook

def xls_info_final_front_preview(request,proj_set,specialtype=""):
    max_expert_num=0;
    for proj_obj in proj_set:
        re_project_expert_list = Re_Project_Expert.objects.filter(project_id = proj_obj)
        max_expert_num=max(len(re_project_expert_list),max_expert_num)
    xls_obj,workbook = xls_info_final_front_preview_gen(request,max_expert_num)
    _number= 2
    index = 1
    style =cell_style(horizontal=True,vertical=True)
    for proj_obj in proj_set:
        teacher = TeacherProfile.objects.get(id = proj_obj.teacher.id)
        manager = teacher.teacherinfosetting
        re_project_expert_list = Re_Project_Expert.objects.filter(project_id = proj_obj)
        row = 1 + _number
        xls_obj.write(row, 0, unicode(index),style) 
        xls_obj.write(row, 1, unicode(proj_obj.title),style) 
        xls_obj.write(row, 2, unicode(manager.name),style)
        xls_obj.write(row, 3, unicode(proj_obj.projectfundsummary.total_budget),style)
        i = 0
        score_list1 = []
        score_list2 = []
        average_score_1 = 0
        average_score_2 = 0
        for re_expert_temp in re_project_expert_list:
            score_table = getFinalScoreTable(re_expert_temp.project).objects.get_or_create(re_obj = re_expert_temp)[0]
            if score_table.get_total_score():
                xls_obj.write(row,4 + i,unicode(score_table.get_total_score()),style)
                score_list1.append(score_table.get_total_score())
            if score_table.get_comments():
                xls_obj.write(row,5+i,unicode(score_table.get_comments()),style)
                score_list2.append(score_table.get_comments())
            i += 2
        average_score_1 = average(score_list1)
        average_score_2 = average(score_list2)

        # if (len(score_list) > 2):
        #     delete_max_and_min(score_list)
        #     average_score_2 = average(score_list)
        xls_obj.write(row, 4+max_expert_num*2,unicode(average_score_1),style)
        xls_obj.write(row, 5+max_expert_num*2,unicode(average_score_2),style)

        _number+= 1
        index += 1
    # write xls file
    save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年大连理工大学基本科研业务费前沿交叉学科基础科研业务费终审结果汇总表"))
    workbook.save(save_path)
    return save_path

def xls_info_humanity_preview(request,proj_set,eid="",stype=1):
    """
    """
    str1=""
    if stype==1:str1="人文社科科研专题"
    if stype==2:str1="基本科研"
    xls_obj, workbook = xls_info_humanity_preview_gen(request,str1)

    _number= 1
    index = 1
    for proj_obj in proj_set:
        teacher = TeacherProfile.objects.get(id = proj_obj.teacher.id)
        manager = teacher.teacherinfosetting
        re_project_expert_list = Re_Project_Expert.objects.filter(project_id = proj_obj)
        row = 1 + _number
        xls_obj.write(row, 0, unicode(index)) 
        xls_obj.write(row, 1, unicode(proj_obj.title)) 
        xls_obj.write(row, 2, unicode(manager.name))
        xls_obj.write(row, 3, unicode(proj_obj.projectfundsummary.total_budget))
        i = 0
        score_list = []
        average_score_1 = 0
        average_score_2 = 0
        for re_expert_temp in re_project_expert_list:
            if eid==TYPE_ALLOC[0]:
                score_table = getScoreTable(re_expert_temp.project).objects.get_or_create(re_obj = re_expert_temp)[0]
            if eid == TYPE_FINAL_ALLOC[0]:
                score_table = getFinalScoreTable(re_expert_temp.project).objects.get_or_create(re_obj = re_expert_temp)[0]
            if score_table.get_total_score():
                xls_obj.write(row,4 + i,unicode(score_table.get_total_score()))
                score_list.append(score_table.get_total_score())
                i += 1
        average_score_1 = average(score_list) 
        if (len(score_list) > 2):
            delete_max_and_min(score_list)
            average_score_2 = average(score_list)
        xls_obj.write(row, 4+EXPERT_NUM,unicode(average_score_1))
        xls_obj.write(row, 5+EXPERT_NUM,unicode(average_score_2))

        _number+= 1
        index += 1
    # write xls file
    if eid==TYPE_ALLOC[0]:
        save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年大连理工大学基本科研业务费%s项目申请初审结果汇总表"%str1))
    if eid == TYPE_FINAL_ALLOC[0]:
        save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年大连理工大学基本科研业务费%s项目申请终审结果汇总表"%str1))
    workbook.save(save_path)
    return save_path

def xls_info_basesummary_preview_gen(request,specialtype):
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')
    style = cell_style(horizontal=True,vertical=True)
    if specialtype == 1:
        typename = "理科基础科研专题"
        sectype = "是否理科基础科研（100分）"
    elif specialtype == 2:
        typename = "前沿学科科研专题"
        sectype = "对所评内容熟悉度A、B、C"
    else:
        typename = "优秀青年人才基础科研专题"
        sectype = "对所评内容熟悉度A、B、C"
    # generate header
    worksheet.write_merge(0, 0, 0,2 + 2*EXPERT_NUM ,typename + '项目结题验收评审打分汇总表',style)
    # generate body
    worksheet.write_merge(1, 2, 0, 0, '序号')
    worksheet.write_merge(1, 2, 1, 1, '项目名称')
    worksheet.col(1).width = len('项目名称') * 400
    worksheet.write_merge(1, 2, 2, 2, '申请人')
    for i in range(0,EXPERT_NUM):
        add_col = i * 2
        worksheet.write_merge(1,1,3+add_col,4+add_col,'专家'+str(i + 1))
        worksheet.write_merge(2,2,3+add_col,3+add_col,'评分(100分)')
        worksheet.write_merge(2,2,4+add_col,4+add_col,sectype)
    worksheet.write_merge(1,2,3+EXPERT_NUM*2,3+EXPERT_NUM*2,'平均分')
    return worksheet, workbook

def xls_info_basesummary_preview(request,proj_set,specialtype,specialname,eid):
    """
    """

    xls_obj, workbook = xls_info_basesummary_preview_gen(request,specialtype)

    _number= 2
    index = 1
    for proj_obj in proj_set:
        teacher = TeacherProfile.objects.get(id = proj_obj.teacher.id)
        manager = teacher.teacherinfosetting
        re_project_expert_list = Re_Project_Expert.objects.filter(project_id = proj_obj)
        row = 1 + _number
        xls_obj.write(row, 0, unicode(index)) 
        xls_obj.write(row, 1, unicode(proj_obj.title)) 
        xls_obj.write(row, 2, unicode(manager.name))
        i = 0
        average_score = 0
        score_list = []
        for re_expert_temp in re_project_expert_list:
            if eid==TYPE_ALLOC[0]:
                score_table = getScoreTable(re_expert_temp.project).objects.get_or_create(re_obj = re_expert_temp)[0]
            if eid == TYPE_FINAL_ALLOC[0]:
                score_table = getFinalScoreTable(re_expert_temp.project).objects.get_or_create(re_obj = re_expert_temp)[0]
            if score_table.get_total_score():
                if specialtype == 1:
                    score_tmp = score_table.get_total_score() + int(score_table.get_comments())
                else:
                    score_tmp = score_table.get_total_score()
                score_list.append(score_tmp)
                xls_obj.write(row,3 + i*2,unicode(score_table.get_total_score()))
                xls_obj.write(row,4 + i*2,unicode(score_table.get_comments()))
                i += 1
        average_score = average(score_list)
        xls_obj.write(row,3+EXPERT_NUM*2,unicode(average_score))
        _number+= 1
        index += 1

    # write xls file
    if eid==TYPE_ALLOC[0]:
        save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), u"年大连理工大学"+ specialname +u"专题基本科研业务经费科研专题项目结题验收初审结果汇总表"))
    if eid == TYPE_FINAL_ALLOC[0]:
        save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), u"年大连理工大学"+ specialname +u"专题基本科研业务经费科研专题项目结题验收终审结果汇总表"))
    workbook.save(save_path)
    return save_path


def xls_info_collection_gen():
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')
    style = cell_style(horizontal=True,vertical=True)
    # generate header
    worksheet.write_merge(0, 0, 0, 10, '项目基本信息',style)
    worksheet.write_merge(0, 0, 11, 11, '项目概述',style)
    worksheet.write_merge(0, 0, 12, 20, '项目负责人信息',style)
    worksheet.write_merge(0, 0, 21, 24, '课题组其他主要参与人（可填多个）',style)
    worksheet.write_merge(0, 0, 25, 25, '项目建设成效',style)
    # generate body
    worksheet.write_merge(1, 1, 0, 0, '项目名称')
    worksheet.col(0).width = len('项目名称') * 800
    worksheet.write_merge(1, 1, 1, 1, '项目编号')
    worksheet.col(1).width = len('项目编号') * 300
    worksheet.write_merge(1, 1, 2, 2, '科技活动类型')
    worksheet.write_merge(1, 1, 3, 3, '国民行业代码')
    worksheet.write_merge(1, 1, 4, 4, '学科名称')
    worksheet.write_merge(1, 1, 5, 5, '学科代码')
    worksheet.write_merge(1, 1, 6, 6, '研究开始时间')
    worksheet.write_merge(1, 1, 7, 7, '研究结束时间')
    worksheet.write_merge(1, 1, 8, 8, '立项年度')
    worksheet.write_merge(1, 1, 9, 9, '项目状态')
    worksheet.write_merge(1, 1, 10, 10, '项目类型')
    worksheet.write_merge(1, 1, 11, 11, '项目摘要')
    worksheet.col(11).width = len('项目摘要') * 800
    worksheet.write_merge(1, 1, 12, 12, '姓名')
    worksheet.write_merge(1, 1, 13, 13, '性别')
    worksheet.write_merge(1, 1, 14, 14, '出生年月')
    worksheet.write_merge(1, 1, 15, 15, '支持对象')
    worksheet.write_merge(1, 1, 16, 16, '学位')
    worksheet.write_merge(1, 1, 17, 17, '职称')
    worksheet.write_merge(1, 1, 18, 18, '行政职务')
    worksheet.write_merge(1, 1, 19, 19, '所在研发基地类型')
    worksheet.write_merge(1, 1, 20, 20, '所在研究基地名称')
    worksheet.write_merge(1, 1, 21, 21, '姓名')
    worksheet.write_merge(1, 1, 22, 22, '出生年份')
    worksheet.write_merge(1, 1, 23, 23, '职称')
    worksheet.write_merge(1, 1, 24, 24, '行政职务')
    worksheet.write_merge(1, 1, 25, 25, '项目本年取得的成效')
    return worksheet, workbook

def xls_info_collection(request,proj_set,eid):
    """
    """

    xls_obj, workbook = xls_info_collection_gen()

    _number= 1
    for proj_obj in proj_set:
        try:
            teacher = TeacherProfile.objects.get(id = proj_obj.teacher.id)
            manager = teacher.teacherinfosetting
            projectMembers = ProjectMember.objects.filter(project=proj_obj)
            loginfo(p=manager,label="manager")
            row = 1 + _number
            xls_obj.write(row, 0, unicode(proj_obj.title)) 
            xls_obj.write(row, 1, unicode(proj_obj.project_code)) 
            xls_obj.write(row, 2, unicode(proj_obj.science_type)) 
            xls_obj.write(row, 3, unicode(proj_obj.trade_code).split()[0])
            xls_obj.write(row, 4, unicode(proj_obj.subject).split()[1])
            xls_obj.write(row, 5, unicode(proj_obj.subject).split()[0])  
            xls_obj.write(row, 6, unicode(proj_obj.start_time)) 
            xls_obj.write(row, 7, unicode(proj_obj.end_time))
            xls_obj.write(row, 8, unicode(proj_obj.approval_year))
            xls_obj.write(row, 9, proj_obj.project_status.get_export_str()) 
            xls_obj.write(row, 10, unicode(proj_obj.project_special))
            xls_obj.write(row, 11, unicode(BasisContent.objects.get(project=proj_obj).basis))
            xls_obj.write(row, 12, unicode(manager.name)) 
            xls_obj.write(row, 13, unicode(manager.get_sex_display())) 
            xls_obj.write(row, 14, unicode(manager.birth)) 
            xls_obj.write(row, 15, unicode(manager.get_target_type_display())) 
            xls_obj.write(row, 16, unicode(manager.get_degree_display()))
            xls_obj.write(row, 17, unicode(manager.get_title_display()))  
            xls_obj.write(row, 18, unicode(manager.get_position_display())) 
            xls_obj.write(row, 19, unicode(manager.get_base_type_display()))
            xls_obj.write(row, 20, unicode(manager.base_name))
            if proj_obj.project_status.status >= PROJECT_STATUS_FINAL_SCHOOL_OVER:
                xls_obj.write(row, 25, unicode(proj_obj.finalsubmit.project_summary))
            else:
                try:
                    xls_obj.write(row, 25, unicode(ProgressReport.objects.filter(project_id = proj_obj).order_by("-year")[0].summary))
                except:
                    pass
            for i,member in enumerate(projectMembers):
                xls_obj.write(row+i, 21, unicode(member.name))
                xls_obj.write(row+i, 22, unicode(member.birth_year))
                xls_obj.write(row+i, 23, unicode(member.professional_title))
                xls_obj.write(row+i, 24, unicode(member.executive_position))
            pass
        except:
            pass
        _number+= projectMembers.count() if projectMembers.count()!=0 else 1
    # write xls file
    save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年大连理工大学教育部项目信息采集填报表"))
    workbook.save(save_path)
    return save_path


def xls_info_summary_gen():
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')
    style = cell_style(horizontal=True,vertical=True)
    # generate header
    # generate body
    worksheet.write_merge(1, 1, 0, 0, '序号')
    worksheet.write_merge(1, 1, 1, 1, '申请人')
    worksheet.write_merge(1, 1, 2, 2, '所在院系')
    worksheet.write_merge(1, 1, 3, 3, '项目名称')
    worksheet.write_merge(1, 1, 4, 4, '项目类别')
    worksheet.write_merge(1, 1, 5, 5, '申报领域/层次')
    worksheet.write_merge(1, 1, 6, 6, '项目组成员')
    worksheet.write_merge(1, 1, 7, 7, '项目状态')

    worksheet.col(3).width = 15000
    worksheet.col(4).width = 6000
    worksheet.col(5).width = 4000
    worksheet.col(6).width = 6000
    return worksheet, workbook

def xls_info_summary(request,proj_set,eid):
    """
    """

    xls_obj, workbook = xls_info_summary_gen()

    _number=1
    for proj_obj in proj_set:
        try:
            row = _number + 1
            xls_obj.write(row, 0, unicode(_number))
            xls_obj.write(row, 1, unicode(proj_obj.teacher.teacherinfosetting))
            xls_obj.write(row, 2, unicode(proj_obj.teacher.college))
            xls_obj.write(row, 3, unicode(proj_obj.title))
            xls_obj.write(row, 4, unicode(proj_obj.project_special))
            xls_obj.write(row, 5, unicode())
            xls_obj.write(row, 6, ','.join([ item.name for item in proj_obj.projectmember_set.all()]))
            xls_obj.write(row, 7, unicode(proj_obj.project_status))  
        except:
            pass
        _number =_number+1
    # write xls file
    save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年大连理工大学基本科研业务费申报项目汇总表"))
    workbook.save(save_path)
    return save_path


def xls_info_conclusionresult_gen():
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')
    style = cell_style(horizontal=True,vertical=True)
    # generate header
    # generate body
    worksheet.write_merge(1, 1, 0, 0, '序号')
    worksheet.write_merge(1, 1, 1, 1, '项目编号')
    worksheet.write_merge(1, 1, 2, 2, '成果类型')
    worksheet.write_merge(1, 1, 3, 3, '成果或论文名称')
    worksheet.write_merge(1, 1, 4, 4, '主要完成者')
    worksheet.write_merge(1, 1, 5, 5, '成果说明')
    worksheet.write_merge(1, 1, 6, 6, '标注情况')
    
    return worksheet, workbook
def xls_info_conclusionresult(request,proj_set,year):
    """
    """
    xls_obj, workbook = xls_info_conclusionresult_gen()
    achivement_set = ProjectAchivement.objects.filter(project_id__in =proj_set).order_by("project_id__project_code")
    _number=1
    for achivement_obj in achivement_set:
        try:
            row = _number + 1
            xls_obj.write(row, 0, unicode(_number))
            xls_obj.write(row, 1, unicode(achivement_obj.project_id.project_code))
            xls_obj.write(row, 2, unicode(achivement_obj.achivementtype))
            xls_obj.write(row, 3, unicode(achivement_obj.achivementtitle))
            xls_obj.write(row, 4, unicode(achivement_obj.mainmember))
            xls_obj.write(row, 5, unicode(achivement_obj.introduction))
            xls_obj.write(row, 6, unicode(achivement_obj.remarks))
        except:
            pass
        _number =_number+1
    # write xls file
    save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(year), "年大连理工大学基本科研业务费结题成果统计表"))
    workbook.save(save_path)
    return save_path
    
def cell_style(horizontal,vertical):
    """
    为CELL添加水平居中和垂直居中
    """
    alignment = xlwt.Alignment()
    if horizontal:
        alignment.horz = xlwt.Alignment.HORZ_CENTER
    elif vertical:
        alignment.vert = xlwt.Alignment.VERT_CENTER
    style = xlwt.XFStyle() # Create Style
    style.alignment = alignment # Add Alignment to Style
    return style

def get_single_project_average_score(project):
    is_first_round = True
    if project.project_status.status == PROJECT_STATUS_FINAL_REVIEW_OVER:
        is_first_round = False

    scoreTableType = getScoreTable(project)
    scoreFormType = getScoreForm(project)
    
    ave_score = 0
    item_count = 0

    for re_obj in Re_Project_Expert.objects.filter(Q(project = project) & Q(is_first_round = is_first_round)):
        table = scoreTableType.objects.get(re_obj = re_obj)
        score_row = scoreFormType(instance = table)
        ave_score += sum(field.value() for field in score_row)
        item_count += 1

    if item_count:
        ave_score /= 1.0 * item_count
    return ave_score

def average(score_list):
    if len(score_list):
        average_score = set_float(sum(score_list))/len(score_list)
    else:
        average_score = 0
    return set_float(average_score)

def set_float(num):
    return float('%.2f' % num)

def xls_info_duplicatecheck_gen():
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')
    style = cell_style(horizontal=True,vertical=True)
    # generate header
    worksheet.write(0, 0,u"姓名")
    worksheet.write(0, 1,u"所在学院")
    worksheet.write(0, 2,u"项目中邮箱")
    worksheet.write(0, 3,u"项目中出生年月")
    worksheet.write(0, 4,u"项目中参加状态")
    worksheet.write(0, 5,u"项目中职称")
    worksheet.write(0, 6,u"项目负责人")
    worksheet.write(0, 7,u"项目名称")
    worksheet.write(0, 8,u"依托学院")
    worksheet.write(0, 9,u"专题类型")
    worksheet.write(0, 10,u"负责项目数量")
    worksheet.write(0, 11,u"负责项目")
    worksheet.write(0, 12,u"参与项目数量")
    worksheet.write(0, 13,u"参与项目")

    return worksheet, workbook

def xls_info_duplicatecheck(request,proj_set):
    """
    """

    xls_obj, workbook = xls_info_duplicatecheck_gen()

    _number= 1
    for proj_obj in proj_set:
        teacherInfo = TeacherInfoSetting.objects.get(teacher=proj_obj.teacher)
        projectMembers = ProjectMember.objects.filter(project=proj_obj)
        row=_number+1
        try:
            hNum = ProjectSingle.objects.filter(Q(teacher=proj_obj.teacher) & Q(project_status__status__lt =PROJECT_STATUS_OVER) & Q(project_status__status__gte =PROJECT_STATUS_APPLICATION_COLLEGE_OVER))
        except:
            hNum = ProjectSingle.objects.none()
        try:
            pNum = ProjectMember.objects.filter(Q(card=proj_obj.teacher.username) & Q(project__project_status__status__lt =PROJECT_STATUS_OVER) & Q(project__project_status__status__gte =PROJECT_STATUS_APPLICATION_COLLEGE_OVER))
        except:
            pNum = ProjectMember.objects.none()
        xls_obj.write(row, 0 ,unicode(teacherInfo.teacher.userid.first_name))
        xls_obj.write(row, 1 ,unicode(teacherInfo.teacher.college))
        xls_obj.write(row, 2 ,unicode(teacherInfo.teacher.userid.email))
        xls_obj.write(row, 3 ,unicode(teacherInfo.birth))
        xls_obj.write(row, 4 ,u"项目负责人")
        xls_obj.write(row, 5 ,unicode(teacherInfo.title))
        xls_obj.write(row, 6 ,unicode(proj_obj.teacher.userid.first_name))
        xls_obj.write(row, 7 ,unicode(proj_obj.title))
        xls_obj.write(row, 8 ,unicode(proj_obj.teacher.college))
        xls_obj.write(row, 9 ,unicode(proj_obj.project_special))
        xls_obj.write(row, 10,unicode(hNum.count()))
        xls_obj.write(row, 11,",".join([ "%s(%s)" % (item.title,item.project_special)for item in hNum]))
        xls_obj.write(row, 12,unicode(pNum.count()))
        xls_obj.write(row, 13,",".join([ "%s(%s)" % (item.project.title,item.project.project_special)for item in pNum]))
        _number+= 1
        for pMember in projectMembers:
            row=_number+1
            try:
                hNum = ProjectSingle.objects.filter(Q(teacher__userid__username=pMember.card) & Q(project_status__status__lt =PROJECT_STATUS_OVER) & Q(project_status__status__gte =PROJECT_STATUS_APPLICATION_COLLEGE_OVER))
            except:
                hNum = ProjectSingle.objects.none()
            try:
                pNum = ProjectMember.objects.filter(Q(card=pMember.card) & Q(project__project_status__status__lt =PROJECT_STATUS_OVER) & Q(project__project_status__status__gte =PROJECT_STATUS_APPLICATION_COLLEGE_OVER))
            except:
                pNum = ProjectMember.objects.none()
            xls_obj.write(row, 0 ,unicode(pMember.name))
            xls_obj.write(row, 1 ,unicode(""))
            xls_obj.write(row, 2 ,unicode(pMember.mail))
            xls_obj.write(row, 3 ,unicode(pMember.birth_year))
            xls_obj.write(row, 4 ,u"项目参与人")
            xls_obj.write(row, 5 ,unicode(pMember.professional_title))
            xls_obj.write(row, 6 ,unicode(proj_obj.teacher.userid.first_name))
            xls_obj.write(row, 7 ,unicode(proj_obj.title))
            xls_obj.write(row, 8 ,unicode(proj_obj.teacher.college))
            xls_obj.write(row, 9 ,unicode(proj_obj.project_special))
            xls_obj.write(row, 10,unicode(hNum.count()))
            xls_obj.write(row, 11,",".join([ "%s(%s)" % (item.title,item.project_special)for item in hNum]))
            xls_obj.write(row, 12,unicode(pNum.count()))
            xls_obj.write(row, 13,",".join([ "%s(%s)" % (item.project.title,item.project.project_special)for item in pNum]))
            _number+= 1
    # write xls file
    save_path = os.path.join(TMP_FILES_PATH, "%s%s.xls" % (str(datetime.date.today().year), "年大连理工大学项目查重表"))
    workbook.save(save_path)
    return save_path

def xls_info_teacherinfo_gen():
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')
    style = cell_style(horizontal=True,vertical=True)
    # generate header
    # generate body
    worksheet.write_merge(1, 1, 0, 0, '姓名')
    worksheet.write_merge(1, 1, 1, 1, '院系')
    worksheet.write_merge(1, 1, 2, 2, '邮箱')
    # worksheet.write_merge(1, 1, 3, 3, '邮箱')

    return worksheet, workbook

def xls_info_teacherinfo(request,eid):
    """
    """

    xls_obj, workbook = xls_info_teacherinfo_gen()
    teachers = TeacherInfoSetting.objects.all()
    _number=1
    for item in teachers:
        try:
            row = _number + 1
            xls_obj.write(row, 0, unicode(item.teacher.userid.first_name))
            xls_obj.write(row, 1, unicode(item.teacher.college))
            xls_obj.write(row, 2, unicode(item.teacher.userid.email))
        except:
            pass
        _number =_number+1
    # write xls file
    save_path = os.path.join(TMP_FILES_PATH, "%s%s%s.xls" % (str(datetime.date.today().year), "年大连理工大学基本科研业务费教师信息导出表",random.randint(1,1000000)))
    workbook.save(save_path)
    return save_path

def delete_max_and_min(score_list):
    """
        删除最高分和最低分
    """
    max_score = max(score_list)
    min_score = min(score_list)
    score_list.remove(max_score)
    score_list.remove(min_score)
    return score_list

def checkIdcard(idcard):
    Errors=[(0, '验证通过!'),(1, '身份证号码位数不对!'),(2, '身份证号码出生日期超出范围或含有非法字符!'),(3, '身份证号码校验错误!'),(4, '身份证地区非法!')]
    area={"11":"北京","12":"天津","13":"河北","14":"山西","15":"内蒙古","21":"辽宁","22":"吉林","23":"黑龙江","31":"上海","32":"江苏","33":"浙江","34":"安徽","35":"福建","36":"江西","37":"山东","41":"河南","42":"湖北","43":"湖南","44":"广东","45":"广西","46":"海南","50":"重庆","51":"四川","52":"贵州","53":"云南","54":"西藏","61":"陕西","62":"甘肃","63":"青海","64":"宁夏","65":"新疆","71":"台湾","81":"香港","82":"澳门","91":"国外"}
    idcard=str(idcard)
    idcard=idcard.strip()
    idcard_list=list(idcard)
    #地区校验
    if len(idcard) >= 2 and (not area.get(idcard[0:2], None)):
        return Errors[4]

    #15位身份号码检测
    if(len(idcard)==15):
        if((int(idcard[6:8])+1900) % 4 == 0 or((int(idcard[6:8])+1900) % 100 == 0 and (int(idcard[6:8])+1900) % 4 == 0 )):
            erg=re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')#//测试出生日期的合法性
        else:
            ereg=re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')#//测试出生日期的合法性
        if(re.match(ereg,idcard)):
            return Errors[0]
        else:
            return Errors[2]
    #18位身份号码检测
    elif(len(idcard)==18):
        #出生日期的合法性检查
        #闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
        #平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
        if(int(idcard[6:10]) % 4 == 0 or (int(idcard[6:10]) % 100 == 0 and int(idcard[6:10])%4 == 0 )):
            ereg=re.compile('[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')#//闰年出生日期的合法性正则表达式
        else:
            ereg=re.compile('[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')#//平年出生日期的合法性正则表达式
        #//测试出生日期的合法性
        if(re.match(ereg,idcard)):
            #//计算校验位
            S = (int(idcard_list[0]) + int(idcard_list[10])) * 7 + (int(idcard_list[1]) + int(idcard_list[11])) * 9 + (int(idcard_list[2]) + int(idcard_list[12])) * 10 + (int(idcard_list[3]) + int(idcard_list[13])) * 5 + (int(idcard_list[4]) + int(idcard_list[14])) * 8 + (int(idcard_list[5]) + int(idcard_list[15])) * 4 + (int(idcard_list[6]) + int(idcard_list[16])) * 2 + int(idcard_list[7]) * 1 + int(idcard_list[8]) * 6 + int(idcard_list[9]) * 3
            Y = S % 11
            M = "F"
            JYM = "10X98765432"
            M = JYM[Y]#判断校验位
            if(M == idcard_list[17]):#检测ID的校验位
                return Errors[0]
            else:
                return Errors[3]
        else:
            return Errors[2]
    else:
        return Errors[1]
