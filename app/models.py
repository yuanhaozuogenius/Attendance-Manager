from django.db import models
from django.utils import timezone


# Create your models here.
class UserType(models.Model):
    # 用户类型表  字段：用户类型
    caption = models.CharField(max_length=10)

    def __str__(self):
        return self.caption


class ClassInfo(models.Model):
    # 班级信息表  字段:班级名称
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class MajorInfo(models.Model):
    # 专业信息表 字段：专业名称
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class UserInfo(models.Model):
    # 工号,密码，姓名,电话, 邮件, 部门, 打卡方式, 打卡详情,打卡备注
    # id = models.BigAutoField(primary_key=True)
    studentNum = models.BigIntegerField(max_length=15)
    username = models.CharField(max_length=15)
    password = models.CharField(max_length=64)
    phone = models.CharField(max_length=11)
    email = models.EmailField(null=False)

    department = models.CharField(max_length=20, null=True)

    clocking_in_time = models.DateTimeField(null=True, blank=True)
    duration = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    clocking_in_method = models.CharField(max_length=20, null=True)
    clocking_in_detail = models.CharField(max_length=20, null=True)
    remark = models.TextField(null=True)

    user_type = models.ForeignKey(to='UserType', default=2, on_delete=models.CASCADE)
    cid = models.ForeignKey('ClassInfo', null=True, on_delete=models.CASCADE)
    major = models.ForeignKey('MajorInfo', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


# 签到表设计
class Attendence(models.Model):
    # 签到表   字段：用户，签到时间，签退时间，描述   其他是为了方便操作加的字段可不写
    stu = models.ForeignKey('UserInfo', on_delete=models.CASCADE)
    # cur_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    date = models.DateField(default=timezone.now)
    # state=models.BooleanField(default=False)
    is_leave = models.BooleanField(default=False)
    detail = models.TextField(default='无')
    leave_count = models.IntegerField(default=0)

    def __str__(self):
        return self.stu.username


# 公告表设计
class Notice(models.Model):
    # 公告表  字段：发布人,发布日期，发布标题，发布内容，发布级别
    author = models.ForeignKey('UserInfo', on_delete=models.CASCADE)
    post_date = models.DateTimeField(auto_now=True)
    head = models.TextField(max_length=200)
    content = models.TextField(max_length=500)
    level = models.IntegerField(default=0)


# 请假表设计
class Leave(models.Model):
    # 请假表 字段：用户，开始时间，结束时间，请假原因
    user = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    start_time = models.DateField(null=True, blank=True)
    end_time = models.DateField(null=True, blank=True)
    explain = models.TextField(default='无', max_length=500)


# 考核内容
# 考核内容表：标题，名称，批阅状态
class ExamContent(models.Model):
    title = models.TextField(max_length=200)
    date = models.DateField(auto_now=True)
    state = models.BooleanField(default=False)

    def __str__(self):
        return self.title


#  考核成绩表设计
class Exam(models.Model):
    # 考核成绩表  字段： 用户，考核内容，分数，备注
    user = models.ForeignKey('UserInfo', on_delete=models.CASCADE)
    content = models.ForeignKey(to='ExamContent', on_delete=models.CASCADE)
    point = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    detail = models.TextField(max_length=200, default="无")
