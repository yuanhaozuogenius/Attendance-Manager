from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from app02 import models
from app02.utils.bootstrap import BootStrapModelForm


# ################################# ModelForm 示例 #################################
class PrettyModelForm(BootStrapModelForm):
    # 验证：方式1 字段+正则
    mobile = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')]
    )

    # 验证：方式2 钩子方法, ModelForm会自动调用函数名为 clean_字段名，在函数体内自己写验证方法
    def clean_mobile(self):
        txt_mobile = self.cleaned_data["mobile"]

        exists = models.PrettyNum.objects.filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError("手机号已存在")

        # 验证通过，用户输入的值返回
        return txt_mobile

    # 设置字段灰显，不可编辑
    level = forms.IntegerField(label="级别", disabled=True)

    class Meta:
        model = models.PrettyNum
        # fields = ["mobile", "price", "level", "status"]
        # exclude = ["level"]
        fields = "__all__"

    '''方法二：改源码，通过循环找到所有的插件，设置插件的属性field.widget.attrs = class ": "form-control" '''


"""由于编辑和新增时业务逻辑不一样 需要分开写一个类来定义规则"""
"""添加：【正则表达式】【手机号不能存在】"""
"""编辑：【正则表达式】【除了自己以外，手机号不能存在】"""


class PrettyEditModelForm(BootStrapModelForm):
    # 验证：方式1 字段+正则
    mobile = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')]
    )

    # 验证：方式2 钩子方法, ModelForm会自动调用函数名为 clean_字段名，在函数体内自己写验证方法
    def clean_mobile(self):
        txt_mobile = self.cleaned_data["mobile"]
        # 获取当前编辑的哪一行的ID
        nid = self.instance.pk
        exists = models.PrettyNum.objects.filter(mobile=txt_mobile).exclude(pk=nid).exists()
        if exists:
            raise ValidationError("手机号已存在")

        # 验证通过，用户输入的值返回
        return txt_mobile

    # 设置字段灰显，不可编辑
    level = forms.IntegerField(label="级别", disabled=True)

    class Meta:
        model = models.PrettyNum
        # fields = ["mobile", "price", "level", "status"]
        # exclude = ["level"]
        fields = "__all__"

    '''方法二：改源码，通过循环找到所有的插件，设置插件的属性field.widget.attrs = class ": "form-control" '''


class UserModelForm(BootStrapModelForm):
    name = forms.CharField(
        min_length=3,
        label="用户名",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = models.UserInfo
        fields = ["name", "password", "age", 'account', 'create_time', "gender", "depart"]

        '''需要给ModelForm自动生成的form添加样式'''

        '''方法一： 通过插件widgets给生成的各类Input框添加 class ": "form-control"样式'''
        # widgets = {
        #     "name": forms.TextInput(attrs={"class": "form-control"}),
        #     "password": forms.PasswordInput(attrs={"class": "form-control"}),
        #     "age": forms.TextInput(attrs={"class": "form-control"}),
        # }

    '''方法二：改源码，通过循环找到所有的插件，设置插件的属性field.widget.attrs = class ": "form-control" '''
