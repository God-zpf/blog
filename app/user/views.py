from . import user
from ..models import *
from flask import render_template

@user.route('/user')
def user_index():
    return '这是user应用的首页'