# user目录：包含处理用户业务逻辑的路由和视图
# __init__.py：用户模块初始化工作
from flask import Blueprint
user = Blueprint('user',__name__)
from .views import *