# 负责整个应用的初始化工作
# 主要工作
# 构建flask应用以及各种配置
# 构建SQLAlchemy应用

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

db = SQLAlchemy()



def create_app():
    app = Flask(__name__)
    # 配置启动模式为调试模式
    app.config['DEBUG'] = True
    # 配置数据库的连字字符串
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/blog'
    # 配置数据库内容在更新时自动提交
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    # 配置session所需要的密钥
    app.config['SECRET_KEY'] = 'you guess'
    # 数据库连接对象初始化
    db.init_app(app)

    # 将main蓝图程序与app关联
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # 将user蓝图程序与app关联
    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint)
    return app
