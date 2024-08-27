from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeField, TextAreaField, EmailField, DateField
from wtforms.validators import DataRequired, URL


class UserRegistration(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Sign Up')


class UserLoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class PostCreationForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired()])
    subtitle = StringField('Event subtitle', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    details = TextAreaField('Details of the Event', validators=[DataRequired()])
    contact = StringField('Contact (optional)')
    join_url = StringField('Joining Url', validators=[URL(), DataRequired()])
    submit = SubmitField('Create Event')






