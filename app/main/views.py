# 主业务逻辑处理路由和视图的定义
# 导入蓝图程序，用于构建路由
import datetime
import os
import re

from sqlalchemy import text

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
        return redirect('/')


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
        topic = Topic()
        topic.title = request.form.get('author')
        topic.blogtype_id = request.form.get('list')
        topic.category_id = request.form.get('category')
        topic.user_id = session.get('uid')
        topic.content = request.form.get('content')
        topic.pub_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("%s,%s,%s,%s,%s,%s" % (
        topic.title, topic.blogtype_id, topic.category_id, topic.user_id, topic.content, topic.pub_date))

        topic.images = request.form.get('imgList')
        # 正则匹配出文档内容的图片链接，不一致者，则删除服务已经存在的图片
        patter = r'src="(/static/upload/\d+.\S+)"'
        # reallist真实有引用到的图片列表
        reallist = re.findall(patter ,topic.content)
        # imgL前端上传到服务器的图片列表
        imgList = topic.images.split(',')
        print('reallist:')
        print('imgList:')
        basedir = os.path.dirname(os.path.dirname(__file__))
        for img in imgList:
            if img not in reallist and os.path.exists(basedir+img):
                os.remove(basedir+img)
                print('删除%s成功' % basedir+img)
        topic.images = ';'.join(reallist).replace('/static/','')
        db.session.add(topic)
        return redirect('/')


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

            # resp = {
            #     "errno": 0,
            #     "data": [
            #         file_path
            #     ]
            # }

            resp = {'url': file_path}
            return json.dumps(resp)


# 详情info界面
@main.route('/info', methods=['GET','POST'])
def info():
    if request.method == 'GET':
        # 查询所有categories的信息
        categories = Category.query.all()
        # 获取博客信息
        topic_id = request.args.get('topic_id')
        topic = Topic.query.filter(Topic.id == topic_id).first()
        # 点击后阅读量加1
        topic.read_num = int(topic.read_num) + 1
        # 上一篇：小于topic_id的最后一条记录
        prevTopic = Topic.query.filter(Topic.id < topic_id).order_by(text("id desc")).first()
        # print('上一篇：', prevTopic.title)
        # 下一篇：大于topic_id的第一条记录
        nextTopic = Topic.query.filter(Topic.id > topic_id).first()
        # print('下一篇：', nextTopic.title)
        # 获取登录信息
        if 'uid' in session and 'uname' in session:
            user = User.query.filter(User.id == session['uid']).first()
        db.session.add(topic)

        return render_template('info.html', params=locals())

    elif request.method == 'POST':
        # 提交评论
        reply = Reply()
        referer = request.headers.get('referer', '/')
        reply.topic_id = request.form.get('topic_id')

        reply.content = request.form.get('content')
        if 'uid' in session and 'uname' in session:
            reply.user_id = User.query.filter(User.id == session['uid']).first().id
        reply.reply_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('%s,%s,%s,%s' % (reply.topic_id, reply.content, reply.user_id, reply.reply_time))
        db.session.add(reply)
        return redirect(referer)

# 异步获取详情博客内容
@main.route('/topic')
def topic():
    topic_id = request.args.get('topic_id')
    print('topic_id',topic_id)
    topic = Topic.query.filter(Topic.id == topic_id).first()
    content = topic.content
    if content:
        data = {
            "code": 0,
            "content": content
        }
    else:
        data = {
            "code": 1,
            "content": '出错了'
        }
    return json.dumps(data)

# 子评论接口
@main.route('/creply', methods=['GET', 'POST'])
def creply():

    creply = ChildReply()
    creply.reply_id = request.form.get('freply_id')
    if 'uid' in session and 'uname' in session:
        creply.cuser_id = session['uid']
    creply.reply_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    creply.content = request.form.get('content')
    print('%s,%s,%s,%s' % (creply.reply_id, creply.cuser_id, creply.reply_time, creply.content))
    db.session.add(creply)
    data = {
        "code": 0,
        "msg": '成功'
    }

    return json.dumps(data)

# 留言
@main.route('/gbook')
def gbook():
    categories = Category.query.all()
    return render_template('gbook.html', params=locals())

# 时间轴
@main.route('/time')
def time():
    categories = Category.query.all()
    if 'uid' in session and 'uname' in session:
        user = User.query.filter(User.id == session['uid']).first()
        topics = Topic.query.filter(Topic.user_id == session['uid']).all()
    return render_template('time.html', params=locals())

# 列表
@main.route('/list')
def list():
    categories = Category.query.all()
    cate_id = request.args.get('cate_id')
    topics = Topic.query.filter(Topic.category_id == cate_id).all()
    if 'uid' in session and 'uname' in session:
        user = User.query.filter(User.id == session['uid']).first()
    return render_template('list.html', params=locals())

# 相册
@main.route('/photo')
def photo():
    categories = Category.query.all()
    if 'uid' in session and 'uname' in session:
        user = User.query.filter(User.id == session['uid']).first()
    return render_template('photo.html', params=locals())

# 关于我
@main.route('/about')
def about():
    categories = Category.query.all()
    return render_template('about.html', params=locals())
