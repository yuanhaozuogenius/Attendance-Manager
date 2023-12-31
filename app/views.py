import csv
import datetime
import hashlib
import json
import re

import pandas as pd
from django.db.models import F, Sum
from django.shortcuts import HttpResponse
from django.shortcuts import render, redirect
# django自带加密解密库
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models
from .api import check_cookie, check_login, DecimalEncoder, is_login
from .models import MajorInfo, UserType, UserInfo, ClassInfo, Attendence, Notice, Leave, ExamContent, Exam


# Create your views here.

# 检查是否登录的装饰器
# def check_login(func):
#     def inner(request,*args,**kwargs):
#         (flag, rank) = check_cookie(request)
#         if flag:
#             func(request,*args,**kwargs)
#         else:
#             return render(request, 'page-login.html', {'error_msg': ''})
#
#     return inner

# 首页
def index(request):
    return redirect('/check/')
    # (flag, rank) = check_cookie(request)
    # print('flag', flag)
    #
    # if flag:
    #     return render(request, 'check.html',locals())
    #
    # return render(request, 'page-login.html', {'error_msg': ''})


# 签到统计
@is_login
def total(request):
    (flag, user) = check_cookie(request)
    # if flag:
    if request.method == 'POST':
        nowdate = datetime.datetime.now()
        weekDay = datetime.datetime.weekday(nowdate)
        firstDay = nowdate - datetime.timedelta(days=weekDay)
        lastDay = nowdate + datetime.timedelta(days=6 - weekDay)
        # print(firstDay,lastDay)
        # info_list=Attendence.objects.filter(date__gte=firstDay,date__lte=lastDay).values('stu','stu__username','stu__cid__name').annotate(total_time=Sum('duration'),leave_count=Sum('is_leave')).order_by()
        info_list = Attendence.objects.filter(date__gte=firstDay, date__lte=lastDay).values('stu', 'stu__username',
                                                                                            'stu__cid__name',
                                                                                            'leave_count') \
            .annotate(total_time=Sum('duration')).order_by()
        info_list = json.dumps(list(info_list), cls=DecimalEncoder)

        return HttpResponse(info_list)
    else:
        nowdate = datetime.datetime.now()
        weekDay = datetime.datetime.weekday(nowdate)
        firstDay = nowdate - datetime.timedelta(days=weekDay)
        lastDay = nowdate + datetime.timedelta(days=6 - weekDay)
        # print(firstDay,lastDay)
        leave_list = Leave.objects.filter().values('user', 'start_time', 'end_time')
        # print(leave_list)
        info_list = Attendence.objects.filter(date__gte=firstDay, date__lte=lastDay).values('stu', 'stu__username',
                                                                                            'stu__cid__name',
                                                                                            'leave_count') \
            .annotate(total_time=Sum('duration')).order_by()

        # info_list=Attendence.objects.filter(date__gte=firstDay,date__lte=lastDay).values('stu','stu__username','stu__cid__name')\
        #     .annotate(total_time=Sum('duration'),leave_count=Sum('is_leave'))\
        #     .extra(
        #     select={'starttime':"select start_time from app_leave where %s BETWEEN start_time AND end_time"},
        #     select_params=[nowdate]
        # )\
        #     .order_by()

        # info_list=json.dumps(list(info_list),cls=DecimalEncoder)
        print(info_list)

        return render(request, 'total.html', locals())
    # else:
    #     return render(request, 'page-login.html', {'error_msg': ''})


# 登录页面
@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        # email = request.POST['email']
        password = request.POST['password']

        m1 = hashlib.sha1()
        m1.update(password.encode('utf8'))
        password = m1.hexdigest()
        print('密码:', password)
        if check_login(username, password):
            response = redirect('/index/')
            response.set_cookie('qwer', username, 3600)
            response.set_cookie('asdf', password, 3600)
            return response
            # return HttpResponse('登录成功')
        else:
            return render(request, 'page-login.html', {'error_msg': '账号或密码错误请重新输入'})
    else:
        (flag, rank) = check_cookie(request)
        print('flag', flag)
        if flag:
            return redirect('/index/')
        return render(request, 'page-login.html', {'error_msg': ''})


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


# 注册页面
@csrf_exempt
def register(request):
    if request.method == 'POST':
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':

            stu_num_v = request.POST.get('stu_num_verify')
            if UserInfo.objects.filter(studentNum=stu_num_v):
                ret = {'valid': False}
            else:
                ret = {'valid': True}

            return HttpResponse(json.dumps(ret))

    else:
        return render(request, 'register.html')


def check(request):
    (flag, rank) = check_cookie(request)
    # print('flag', flag)
    user = rank

    if flag:
        if request.method == 'POST':
            sign_flag = request.POST.get('sign')
            print('sign_flag', type(sign_flag), sign_flag)
            if sign_flag == 'True':
                Attendence.objects.create(stu=user, start_time=datetime.datetime.now())
            # 如果已签到，则签退
            elif sign_flag == 'False':
                cur_attendent = Attendence.objects.filter(stu=user, end_time=None)
                tmp_time = datetime.datetime.now()
                duration = round((tmp_time - cur_attendent.last().start_time).seconds / 3600, 1)

                cur_attendent.update(end_time=tmp_time, duration=duration)
            return HttpResponse(request, '操作成功')
        else:
            # 查询上一个签到的状态
            pre_att = Attendence.objects.filter(stu=user).order_by('id').last()
            # print(pre_att.end_time)
            if pre_att:
                # 如果当前时间距上次签到时间超过六小时，并且上次签退时间等于签到时间
                if (datetime.datetime.now() - pre_att.start_time.replace(
                        tzinfo=None)).seconds / 3600 > 6 and pre_att.end_time == None:
                    # Attendence.objects.filter(stu=user, end_time=None).update(end_time=pre_att.start_time+datetime.timedelta(hours=2),duration=2,detail="自动签退")
                    pre_att.delete()
                    sign_flag = True

                elif (datetime.datetime.now() - pre_att.start_time.replace(
                        tzinfo=None)).seconds / 3600 < 6 and pre_att.end_time == None:
                    sign_flag = False
                else:
                    sign_flag = True
            else:
                sign_flag = True
            att_list = Attendence.objects.all().order_by('-id')

            return render(request, 'check.html', locals())

    return render(request, 'page-login.html', {'error_msg': ''})


# 注销登录
def logout(request):
    req = redirect('/login/')
    req.delete_cookie('asdf')
    req.delete_cookie('qwer')
    return req


# 注册验证
def register_verify(request):
    if request.method == 'POST':
        print('验证成功')
        username = request.POST.get('username')
        email = request.POST.get('email')
        stu_num = request.POST.get('stu_num')
        pwd = request.POST.get('password')
        m1 = hashlib.sha1()
        m1.update(pwd.encode('utf8'))
        pwd = m1.hexdigest()
        phone = request.POST.get('phone')
        a = UserInfo.objects.create(username=username, email=email, studentNum=stu_num, password=pwd,
                                    phone=phone, user_type_id=2)

        a.save()
        return HttpResponse('OK')


# 班级管理
def classManage(request):
    (flag, rank) = check_cookie(request)
    print('flag', flag)
    if flag:
        if rank.username == 'admin':
            class_list = ClassInfo.objects.all()

            return render(request, 'classManage.html', {'class_list': class_list})
        else:
            return render(request, 'class_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 编辑班级
@csrf_exempt
def edit_class(request):
    (flag, rank) = check_cookie(request)
    print('flag', flag)
    if flag:
        if rank.username == 'admin':
            if request.method == 'POST':
                pre_edit_id = request.POST.get('edit_id')
                class_name = request.POST.get('edit_class_name')
                temp_flag = ClassInfo.objects.filter(name=class_name)
                print('pre_edit_id1', pre_edit_id)
                pre_obj = ClassInfo.objects.get(id=pre_edit_id)
                if not temp_flag and class_name:
                    pre_obj.name = class_name
                    pre_obj.save()
                return HttpResponse('班级修改成功')
            class_list = ClassInfo.objects.all()
            return render(request, 'classManage.html', {'class_list': class_list})
            # return HttpResponse('编辑班级')
        else:
            return render(request, 'class_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 添加班级
@csrf_exempt
def add_class(request):
    # print('进来了')
    if request.method == 'POST':
        # print('这是post')
        add_class_name = request.POST.get('add_class_name')
        flag = ClassInfo.objects.filter(name=add_class_name)
        if flag:
            pass
            # print('已有数据，不处理')
        else:
            if add_class_name:
                ClassInfo.objects.create(name=add_class_name).save()

        return HttpResponse('添加班级成功')


# 删除班级
def delete_class(request):
    (flag, rank) = check_cookie(request)
    print('flag', flag)
    if flag:
        if rank.username == 'admin':
            # class_list=ClassInfo.objects.all()
            delete_id = request.GET.get('delete_id')
            ClassInfo.objects.filter(id=delete_id).delete()
            return redirect('/classManage/')
        else:
            return render(request, 'class_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 专业管理
def majorManage(request):
    (flag, rank) = check_cookie(request)
    if flag:
        if rank.username == 'admin':
            major_list = MajorInfo.objects.all()

            return render(request, 'major_manage.html', {'major_list': major_list})
        else:
            return render(request, 'major_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 添加专业
@csrf_exempt
def add_major(request):
    (flag, rank) = check_cookie(request)
    if flag:
        if rank.username == 'admin':
            major_list = MajorInfo.objects.all()
            if request.method == 'POST':

                add_major_name = request.POST.get('add_major_name')
                print(add_major_name)
                if not MajorInfo.objects.filter(name=add_major_name):
                    new_major = MajorInfo.objects.create(name=add_major_name)
                return HttpResponse('专业添加成功')

            return render(request, 'major_manage.html', {'major_list': major_list})
        else:
            return render(request, 'major_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 删除专业
def delete_major(request):
    (flag, rank) = check_cookie(request)
    if flag:
        if rank.username == 'admin':

            delete_major_id = request.GET.get('delete_id')
            MajorInfo.objects.get(id=delete_major_id).delete()
            major_list = MajorInfo.objects.all()
            return render(request, 'major_manage.html', {'major_list': major_list})
        else:
            return render(request, 'major_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 编辑专业
@csrf_exempt
def edit_major(request):
    (flag, rank) = check_cookie(request)
    if flag:
        if rank.username == 'admin':
            major_list = MajorInfo.objects.all()
            edit_major_id = request.POST.get('edit_major_id')
            edit_major_name = request.POST.get('edit_major_name')
            print(edit_major_id)
            print(edit_major_name)
            if not MajorInfo.objects.filter(name=edit_major_name):
                change_obj = MajorInfo.objects.get(id=edit_major_id)
                change_obj.name = edit_major_name
                change_obj.save()
            return HttpResponse('专业修改成功')

        else:
            return render(request, 'major_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 成员管理
def member_manage(request):
    (flag, rank) = check_cookie(request)
    if flag:
        if rank.username == 'admin':
            member_list = UserInfo.objects.all()

            return render(request, 'member_manage.html', {'member_list': member_list})
        else:
            return render(request, 'member_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 删除成员
def delete_member(request):
    (flag, rank) = check_cookie(request)
    if flag:
        if rank.username == 'admin':
            delete_sno = request.GET.get('delete_sno')
            UserInfo.objects.get(studentNum=delete_sno).delete()
            member_list = UserInfo.objects.all()
            return render(request, 'member_manage.html', {'member_list': member_list})
        else:
            return render(request, 'member_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


#   编辑成员
def edit_member(request):
    (flag, rank) = check_cookie(request)
    if flag:
        if rank.username == 'admin':

            if request.method == 'POST':
                student_num = request.POST.get('student_num')
                username = request.POST.get('username')
                email = request.POST.get('email')
                age = request.POST.get('age')
                if age:
                    age = int(age)
                else:
                    age = 0

                gender = int(request.POST.get('gender'))
                cls = ClassInfo.objects.get(name=request.POST.get('cls'))
                nickname = request.POST.get('nickname')
                usertype = UserType.objects.get(caption=request.POST.get('user_type'))
                phone = request.POST.get('phone')
                motto = request.POST.get('motto')
                edit_obj = UserInfo.objects.filter(studentNum=student_num)
                edit_obj.update(studentNum=student_num, username=username, email=email, cid=cls, nickname=nickname,
                                user_type=usertype, motto=motto,
                                gender=gender, phone=phone,
                                age=age
                                )
                member_list = UserInfo.objects.all()

                return redirect('/memberManage/', {'member_list': member_list})
            else:
                edit_member_id = request.GET.get('edit_sno')
                # 所有用户类型列表
                stu_type_list = UserType.objects.all()
                # 所有的班级
                cls_list = ClassInfo.objects.all()
                # 所有的专业
                major_list = MajorInfo.objects.all()
                # 当前编辑的用户对象
                edit_stu_obj = UserInfo.objects.get(studentNum=edit_member_id)
                return render(request, 'edit_member.html', locals())
        else:
            return render(request, 'member_manage_denied.html')
    else:
        return render(request, 'page-login.html', {'error_msg': ''})


# 公告墙展示
@is_login
def notice(request):
    info_list = Notice.objects.all().order_by('-post_date')
    return render(request, 'notice.html', locals())


# 公告墙发布
@is_login
def noticeManage(request):
    (flag, user) = check_cookie(request)
    if user.username == 'admin':
        if request.method == 'POST':
            title = request.POST.get('title')
            content = request.POST.get('content')
            level = request.POST.get('selectLevel')
            Notice.objects.create(head=title, content=content, level=level, author=user)
            return render(request, 'notice_manage.html')
        else:
            return render(request, 'notice_manage.html')
    else:
        return render(request, 'notice_manage_denied.html')


# 请假管理
@is_login
def leave(request):
    (flag, user) = check_cookie(request)
    leave_list = Leave.objects.all()
    if request.method == 'POST':
        starttime = request.POST.get('starttime')
        endtime = request.POST.get('endtime')
        print(starttime)
        a = int(datetime.datetime.strptime(starttime, '%Y-%m-%d').day - datetime.datetime.strptime(endtime,
                                                                                                   '%Y-%m-%d').day) + 1
        explain = request.POST.get('explain')
        Leave.objects.create(start_time=starttime, end_time=endtime, user=user, explain=explain)
        Attendence.objects.filter(date__gte=starttime, date__lte=endtime, stu=user).update(
            leave_count=F('leave_count') + a)
    return render(request, 'leave.html', locals())


# 考核记录
@is_login
def exam(request):
    exam_list = ExamContent.objects.all()
    exam_id = request.GET.get('exam_id')
    if exam_id:
        user_list = Exam.objects.filter(content_id=exam_id).all()
    return render(request, 'exam.html', locals())


# 考核管理
@is_login
def exam_manage(request):
    (flag, user) = check_cookie(request)
    if user.username == 'admin':
        if request.method == 'POST':
            title = request.POST.get('title')

            if title:
                ExamContent.objects.create(title=title)
            else:
                count = UserInfo.objects.all().count()
                content_id = request.POST.get('exam_id')
                for i in range(count):
                    point = request.POST.get('point{}'.format(i))

                    stuID = request.POST.get('stu{}'.format(i))
                    detail = request.POST.get('detail{}'.format(i))
                    Exam.objects.create(point=point, content_id=content_id, user_id=stuID, detail=detail)
                # print(request.body)
                ExamContent.objects.filter(id=content_id).update(state=True)
        check_list = ExamContent.objects.filter(state=False)
        user_list = UserInfo.objects.all()
        return render(request, 'exam_manage.html', locals())
    else:
        return render(request, 'exam_manage_denied.html')


def re_clocking_in_time(str):
    return str.replace(" (", " ").replace(")", "")


# 获取打卡详情中文字段
def re_clocking_in_detail(str):
    return re.search(r'([\u4e00-\u9fa5]+)', str).group(1)


def re_remark(str):
    return str.replace("-", " ")


@api_view(['POST'])
def load_data(request):
    attendance_list = []
    response = {
        'code': 0
    }
    file_path = r"data/原始记录表_20230901_20230930.xlsx"
    path = file_path

    # excel to csv
    csv_path = path.replace(".xlsx", ".csv")
    # index_col=0如果不设置，转换后csv文件第一列就会是索引0，1，2...
    data = pd.read_excel(path, index_col=0)
    data.to_csv(csv_path, encoding='utf-8')
    with open(csv_path, 'r', newline='', encoding='utf-8') as file:
        readlines = csv.DictReader(file)
        for i, line in enumerate(readlines):
            if i != 0:
                attendance_dict = {key: value for key, value in line.items()}
                attendance_list.append(attendance_dict)
                print("line['姓名']:", line['姓名'])

                UserInfo.objects.create(
                    username=line['姓名'],
                    studentNum=int(float(line['工号'])),
                    department=line['部门'],
                    clocking_in_time=re_clocking_in_time(line['打卡时间']),
                    clocking_in_method=line['打卡方式'],
                    clocking_in_detail=re_clocking_in_detail(line['打卡详情']),
                    remark=re_remark(line['打卡备注']),
                )
                print("Index", i, ":", line)
            if i != 0:
                print("Data imported successfully")
    response['code'] = 200
    response['data'] = attendance_list
    return Response(response)


@api_view(['GET'])
def query_data(request):
    """
        返回表中所有elements

    """
    features = models.UserInfo.objects.all()  # 获取表中所有实例
    response = {'data': [],
                'code': 0}
    print("features:", features)
    for i, item in enumerate(features):
        # print(i, ":", item.username, item.clocking_in_time, item.password)
        response['data'].append({
            'username': item.username,
            'studentNum': item.studentNum,
            'department': item.department,
            'clocking_in_time': item.clocking_in_time,
            'clocking_in_method': item.clocking_in_method,
            'clocking_in_detail': item.clocking_in_detail,
            'remark': item.remark,
        })
        # response['data']['item'+str(i+1)].append(str(item.feature_name))
    # print(response['data'])
    response['code'] = 200
    # response['equipments'] = equipments
    return Response(response)


@api_view(['GET'])
def delete_all_data(request):
    UserInfo.objects.filter().delete()
    response = {
        'code': 200
    }
    return Response(response)
