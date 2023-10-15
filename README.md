# Attendance-Manager

1. 创建并激活虚拟环境

   注意 Pycharm interpreter, terminal中Win PowerShell二者环境需要保持一致

`conda create --prefix=F:\Tools\anaconda3\envs\attendance_manager python=3.11`

`conda activate F:\Tools\anaconda3\envs\attendance_manager`

<img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016011117489.png" alt="image-20231016011117489" style="zoom:67%;" />

2. pycharm 设置python virtual environment

   ![image-20231016011741039](C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016011741039.png)
3. 部署Django(if needed)

   `pip show Django`

   `django-admin startproject projectname`

   `python manage.py`
4. 安装环境包(空项目第一次需要手动装，后续可以依赖requirements.txt, Pipfile等管理工具)

   安装requirements.txt的所有依赖项

   `pip install -r requirements.txt`

   安错了也没关系，还可以卸载

   `pip uninstall -y -r requirements.txt`

也可以通过manage.py快速检查安装包

<img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016012202551.png" alt="image-20231016012202551" style="zoom:67%;" />

5. 创建数据库

`mysql -u root -p`

`create database empdb DEFAULT CHARSET utf8 COLLATE utf8_general_ci;`

`show databases;`
`use empdb;`
`show tables;`

<img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016013706665.png" alt="image-20231016013706665" style="zoom:67%;" />

<img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016013749851.png" alt="image-20231016013749851" style="zoom:66%;" />

<img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016014136456.png" alt="image-20231016014136456" style="zoom:50%;" />

<img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016014948704.png" alt="image-20231016014948704" style="zoom:67%;" />

6. 运行manage.py ，可以在工具栏中创建快捷指令栏

   `python manage.py createsuperuser`

   `python manage.py makemigrations`

   `python manage.py migrate`

   `python manage.py runserver`

<img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016012244947.png" alt="image-20231016012244947" style="zoom:60%;" />

<img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016012353702.png" alt="image-20231016012353702" style="zoom:80%;" />

<img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016013608436.png" alt="image-20231016013608436" style="zoom:67%;" />

<img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016015044747.png" alt="image-20231016015044747" style="zoom:67%;" />

7. 注册用户(首次载入)

<img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016015230868.png" alt="image-20231016015230868" style="zoom: 42%;" />

8. 登录

   主要是这两个页面 其他功能暂时用不到

   <img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016015340652.png" alt="image-20231016015340652" style="zoom:80%;" />

   <img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016021533696.png" alt="image-20231016021533696" style="zoom:67%;" />
9. 代码简要说明

   这两个函数主要用来实现从excel文件导入数据到db，从db读取数据

   <img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016021206805.png" alt="image-20231016021206805" style="zoom:67%;" />

   excel数据存储在UserInfo表

   <img src="C:\Users\yuanh\AppData\Roaming\Typora\typora-user-images\image-20231016021422336.png" alt="image-20231016021422336" style="zoom:67%;" />
10. 导出环境依赖

`pip freeze > requirements.txt`

申明编码格式

因为里面安装的包有中文注释。文件开头加 ：

```python
# -*- coding:utf-8 -*-
```



Reference 

https://github.com/xp1993/Attendance-Management-System
