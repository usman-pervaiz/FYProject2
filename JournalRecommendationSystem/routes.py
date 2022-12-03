from flask import render_template,url_for,flash,redirect,request
from wtforms.validators import Email
from JournalRecommendationSystem.models import User, UserDetails
from JournalRecommendationSystem import app, db, bcrypt, mail
from JournalRecommendationSystem.forms import LoginForm, RegistrationForm, UserDetailsEditForm, RequestResetForm, ResetPasswordForm, AddArticlesManuallyForm, SearchForm
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image
from flask_mail import Message

from rank_bm25 import BM25Okapi
import pandas as pd

from whoosh.qparser import QueryParser
from whoosh.query import *
from whoosh import index 
import os

from whoosh.qparser import MultifieldParser,OrGroup
from whoosh.fields import *
import time


class search_query_BM25():
    def __init__(self,title_new='',abstract_new='',keywords_new=''):
        
        self.title_new = title_new
        self.abstract_new = abstract_new
        self.keywords_new = keywords_new
    
        self.tokenized_query = self.title_new+self.abstract_new+self.keywords_new

    def Search(self):
        a=time.time()
        ix = index.open_dir(os.getcwd()+"\\JournalRecommendationSystem\\indexdir")
        searcher = ix.searcher()
        lst = []
        new_lst = []
        check =[]
        with ix.searcher() as searcher:
            query = MultifieldParser(["Title","Abstract"], ix.schema, group=OrGroup).parse(u(self.tokenized_query))
            results = searcher.search(query, terms=True, limit=24)
            #print(len(results))
            
            for r in results:
                lst.append([r["Source_title"], r['Publisher'],r['Queue_Ranking'], r.score])
        #print(len(lst))
        for i in range(len(lst)):
            if lst[i][0] not in check:
                if lst[i][1] not in check:
                    new_lst.append(lst[i])
                    check.append(lst[i][0])
                    check.append(lst[i][1])

        b= time.time()
        c = b-a
        #print(len(new_lst))
        new_lst.append(round(c,3))
        return new_lst


@app.route("/", methods=['GET', 'POST'])
@app.route("/home/", methods=['GET', 'POST'])
def home():
    form = SearchForm()
    if form.validate_on_submit():
        bm25 = search_query_BM25(form.Search.data)
        data=bm25.Search()
        if len(data)==1:
            flash('In valid Input', 'danger')
            return redirect(url_for('home'))
        return render_template('Recommendation.html',data=data)
    return render_template('home.html',form=form)

@app.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
            return redirect(url_for("home.html"))
    form=RegistrationForm()
    if form.validate_on_submit():
        
        if request.method == 'POST':
            user = form.username.data
            email = form.email.data
            name = form.name.data

            password = form.password.data
            confirm_password = form.confirm_password.data
            
            finding_user = User.objects(username= form.username.data).first()
            finding_email =  User.objects(email=form.email.data).first()
            #print(user)
            if finding_user:
                message = 'User Already Exist!'
                return render_template('registration.html', message=message, form=form)
            if finding_email:
                message = 'Email is already taken!'
                return render_template('registration.html', message=message, form=form)
            if password != confirm_password:
                message = 'Passwords not match!'
                return render_template('registration.html', message=message, form=form)
            else:
                hashed = bcrypt.generate_password_hash(confirm_password).decode('utf-8')
                user_input = User(username=user,name=name,email=email,password=hashed).save()
                flash('Your Account has been created!.','success')
                return redirect(url_for('login'))
    return render_template('registration.html',form=form)
        


@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = form.username.data
        password = form.password.data

        userfind = User.objects(username=user).first()
        #print(userfind)
        
        if userfind and  bcrypt.check_password_hash(userfind.password,form.password.data):
            loginuser = userfind
            login_user(loginuser,form.remember.data)
            return redirect(url_for('home'))
        else:
            flash("Login Unsuccessful! Please check email or password.","danger")
    return render_template('login.html',form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics',picture_fn)
    
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/userprofile",methods=['GET','POST'])
@login_required
def userprofile():
    form = UserDetailsEditForm()
    finding_user = UserDetails.objects(User_id=current_user.get_id()).first()
    #print(current_user.image_file)
    if form.validate_on_submit():
        if form.picture.data:
            if current_user.image_file != 'default.jpg':
                os.unlink(os.path.join(app.root_path,'static/profile_pics/'+current_user.image_file)) 
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            
            User.objects(id=current_user.get_id()).update(image_file=picture_file)

        finding_email =  User.objects(email=form.email.data).first()
        
        image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
        if finding_email and (finding_email.email != current_user.email):
                flash('Email is already taken!', 'danger')
                return render_template('Profile.html', form=form, image_file=image_file,myuser=finding_user)
        
        current_user.name = form.name.data 
        current_user.email = form.email.data
        User.objects(id=current_user.get_id()).update(name=form.name.data,email=form.email.data)
        
        
        if finding_user:
            UserDetails.objects(User_id=current_user.get_id()).update(affiliation=form.affiliation.data,area_of_interest=form.area_of_interest.data)
            finding_user = UserDetails.objects(User_id=current_user.get_id()).first()
            return redirect(url_for('userprofile'))
        else:
            UserDetails(affiliation=form.affiliation.data,area_of_interest=form.area_of_interest.data,User_id=current_user.get_id()).save()
            finding_user = UserDetails.objects(User_id=current_user.get_id()).first()
            return redirect(url_for('userprofile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        if finding_user:
            form.affiliation.data = finding_user.affiliation
            form.area_of_interest.data = finding_user.area_of_interest
    image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('Profile.html', form=form, image_file=image_file, myuser=finding_user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    print(user)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #print(user.objects())
        User.objects(email=user.email).update_one(password=hashed_password)
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/AddArticlesManually/", methods=['GET', 'POST'])
@login_required
def AddArticlesManually():
    form = AddArticlesManuallyForm()
    if form.validate_on_submit():
        bm25 = search_query_BM25(str(form.Papertitle.data),str(form.Abstract.data),str(form.Keywords.data))
        data=bm25.Search()
        if len(data)==1:
            flash('In valid Input', 'danger')
            return redirect(url_for('AddArticlesManually'))
        #print(data)
        return render_template('Recommendation.html',data=data)
    return render_template('AddArticlesManually.html',form=form)
    

@app.route("/Recommendation/")
@login_required
def Recommendation():
    return render_template('Recommendation.html')