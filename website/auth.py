from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, data_sources
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from sqlalchemy.inspection import inspect
from .search import *
from .searchwiththumb import *
import time
import asyncio
import threading

auth = Blueprint('auth',__name__)

inspector = inspect(User)

headings = inspector.mapper.column_attrs.keys()


@auth.route('/auth',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                flash('Logged in successfully!',category='success')
                login_user(user,remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Unsuccessfull, try again',category='error')
        else:
            flash('No account existed under this email! Try again or Sign up...',category='error')

    return render_template("login.html")

@auth.route('/logout')
@login_required #can only access log out option if logged in
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('User already existed', category='error')
        elif len(email) <4 :
            flash('Email must be at least 4 characters.',category='error')
        elif len(firstName) < 2:
            flash('First name must be at least 2 characters',category='error')
        elif password1!=password2:
            flash('Passwords do NOT match, try again!',category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.',category='error')
        else:
            new_user = User(email=email,first_name=firstName,password=generate_password_hash(password1,method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!',category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html")

@auth.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'POST' and request.form.get('email')!= '':
        search_key_email = '%'+request.form.get('email')+'%'
        users = User.query.filter(User.email.like(search_key_email)).all()
        return render_template("admin.html",headings=headings,users=users)
    return render_template("admin.html",headings=headings,users='')

@auth.route('/search',methods=['POST'])
async def search():
    result_sources=''
    dis_as_list = []
    if 'btn3' in request.form and request.form.get('confirm_action')=='confirmed':
        line = 'heehee'
    elif 'btn4' in request.form and request.form.get('confirm_action')=='confirmed':
        start_time = time.time()   
        no_of_entries = await memify()
        line = 'Dictionary updated!'
        flash(f'The dictionary has {no_of_entries} entries. ({time.time()-start_time} seconds)',category='info')
    elif 'search' in request.form and request.form.get('keyword')!='':
        start_time = time.time()
        keywords = f"%{request.form.get('keyword')}%"
        result_sources = data_sources.query.filter(data_sources.name.like(keywords)).all()
        for dis in result_sources:
            dis = dis.display
            dis_as_list.append(convert_to_list(dis))
        line = f"{str(len(result_sources))} results found ({round(time.time()-start_time,3)} seconds.)"
    else:
        line=''
    return render_template("search.html",output=line,results=result_sources,dis_as_list=dis_as_list)


@auth.route('/search',methods=['GET'])
def newsearch():
    return render_template("search.html",output='')

@auth.route('/test',methods=['GET'])
def test():
    return render_template("test.html")

@auth.route('/searchthumb',methods=['POST'])
async def searchThumb():
    result_sources=''
    dis_as_list = []

    if 'search' in request.form and request.form.get('keyword')!='':
        start_time = time.time()
        keywords = f"%{request.form.get('keyword')}%"
        result_sources = data_sources.query.filter(data_sources.name.like(keywords)).all()
        for elem in result_sources:
            dis = elem.display
            dis_as_list.append(convert_to_list(dis))


        line = f"{str(len(result_sources))} results found ({round(time.time()-start_time,3)} seconds.)"
    else:
        line=''
    return render_template("searchwiththumb.html",output=line,results=result_sources,dis_as_list=dis_as_list)

@auth.route('/searchthumb',methods=['GET'])
def newsearchThumb():
    return render_template("searchwiththumb.html",output='')