from typing import Text
from PIL.Image import NONE
from flask_wtf import FlaskForm
from pyparsing import Keyword
from wtforms import StringField, PasswordField, SubmitField, BooleanField, EmailField,SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.widgets.core import TextArea
from JournalRecommendationSystem.models import User
import wtforms

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=6,max=22)])
    name = StringField('Name',validators=[DataRequired()])
    email = EmailField("Email",validators=[DataRequired(),Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired()])#,EqualTo('password')])
    submit = SubmitField('Create Free Account')
    
class LoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=6,max=22)])
    password = PasswordField("Password",validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class UserDetailsEditForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    affiliation = StringField('Affiliation',validators=[DataRequired()])
    email = EmailField('Email',validators=[DataRequired(),Email()])
    picture = FileField('Update Profile Picture ',validators=[FileAllowed(['png','jpg'])])
    area_of_interest = StringField('Areas of Interest',validators=[DataRequired()])
    submit = SubmitField('Update')


    
class RequestResetForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    submit = SubmitField('Send')

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class AddArticlesManuallyForm(FlaskForm):
    Papertitle = StringField('Paper title:',validators=[DataRequired()])
    Abstract = TextAreaField('Abstract:',validators=[DataRequired()])
    Keywords = StringField('Keywords:',validators=[DataRequired()])
    submit = SubmitField('Recommend')
    

class SearchForm(FlaskForm):
    Search = StringField('',validators=[DataRequired()])
    submit = SubmitField('Recommend')