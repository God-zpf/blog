# main目录：包含主业务逻辑的路由和视图
# __init__.py：主业务模块的初始化

from flask import Blueprint
main = Blueprint('main',__name__)
from .views import *
