# 主业务逻辑处理路由和视图的定义
# 导入蓝图程序，用于构建路由
import datetime
import os

from . import main
# 导入db，用于操作数据库
from app import db
# 导入实体类，用于操作数据库
from ..models import *
from flask import render_template, make_response
from flask import request
from flask import redirect
from flask import session
import json


# 首页面
@main.route('/')
def index():
    # 查询所有Category的信息
    categories = Category.query.all()
    # 查询所有Topic的信息
    topics = Topic.query.all()
    # 获取登陆信息
    if 'uid' in session and 'uname' in session:
        user = User.query.filter(User.id == session['uid']).first()
    return render_template('index.html', params=locals())


# 登陆页面
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # 获取跳转至登陆页面前的网页地址，以供提交表单时获取
        referer = request.headers.get('referer', '/')
        if 'uid' in session and 'uname' in session:
            return redirect(referer)
        else:
            return render_template('login.html', params=locals())
    elif request.method == 'POST':
        loginname = request.form.get('username')
        upwd = request.form.get('password')
        user = User.query.filter(User.loginname == loginname, User.upwd == upwd).first()
        # 获取跳转网页源地址
        referer = request.form.get('source_url')
        if user:
            # 用户名密码正确，完成登陆操作
            session['uid'] = user.id
            session['uname'] = user.uname
            resp = make_response(redirect(referer))
            return resp
        else:
            errMsg = '登录名或密码错误'
            return render_template('login.html', params=locals())


# 注册页面
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # 获取跳转至注册页面前的网页地址，以供提交表单时获取
        referer = request.headers.get('referer', '/')
        return render_template('register.html', params=locals())
    elif request.method == 'POST':
        # 获取提交表单的值并赋值给user实体对象
        loginname = request.form.get('loginname')
        uname = request.form.get('username')
        upwd = request.form.get('password')
        email = request.form.get('email')
        url = request.form.get('url')
        user = User(loginname, uname, upwd, email, url)
        # 将数据保存进数据库  --注册
        db.session.add(user)
        # 手动提交，目的是获取提交后的user的id
        # 当user成功插入到数据库后，程序会自动将所有信息提取出来再赋给user
        db.session.commit()
        # 完成登陆操作
        session['uid'] = user.id
        session['uname'] = user.uname
        referer = request.form.get('source_url')
        # 重定向到跳转到注册页面前的网页地址
        if referer:
            return redirect(referer)
        else:
            return redirect('/')


# 注销页面
@main.route('/logout')
def logout():
    if 'uid' in session and 'uname' in session:
        del session['uid']
        del session['uname']
        return redirect('/')
    else:
        return redirect('/index')


# 异步ajax验证注册按钮
@main.route('/check', methods=['GET', 'POST'])
def check():
    loginname = request.args.get('loginname')
    user = User.query.filter(User.loginname == loginname).first()
    if user:
        data = {
            "code": 0,
            "msg": "登录名已经注册"
        }
    else:
        data = {
            "code": 1,
            "msg": "校验通过"
        }
    return json.dumps(data)


# 发表博客
@main.route('/release', methods=['GET', 'POST'])
def release():
    if request.method == 'GET':
        # 权限验证：验证用户是否具有发表博客的权限即必须是登陆用户而且is_author值为1
        if 'uid' not in session or 'uname' not in session:
            return redirect('/login')
        else:
            user = User.query.filter(User.id == session.get('uid')).first()
            if user.is_author != 1:
                referer = request.args.get('referer', '/')
                return redirect(referer)
            # 查询所有Category的信息
            categories = Category.query.all()
            # 查询所有Blogtype的信息
            blogTypes = Blogtype.query.all()
            return render_template('release.html', params=locals())
    # 处理发表博客提交
    elif request.method == 'POST':
        return '提交成功'


@main.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if request.files:
            print('有文件上传')
            # 取出文件
            f = request.files['myFile']
            # 处理文件名称,将名称赋值给topic.images
            # 获取当前时间，作为文件名
            ftime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            # 获取文件的扩展名
            ext = f.filename.split('.')[1]
            filename = ftime + "." + ext
            # topic.images = 'upload/' + filename
            # 将文件保存至服务器
            file_path = '/static/upload/' + filename
            basedir = os.path.dirname(os.path.dirname(__file__))
            upload_path = os.path.join(basedir, 'static/upload', filename)
            print(upload_path)
            f.save(upload_path)

            resp = {
                "errno": 0,
                "data": [
                    file_path
                ]
            }
            return json.dumps(resp)
