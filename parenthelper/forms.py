from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField, DateField, TimeField
from wtforms_html5 import AutoAttrMeta
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from parenthelper.models import User

# Registration form
class RegistrationForm(FlaskForm):
    class Meta(AutoAttrMeta):
        pass
    email = EmailField('Email', validators=[DataRequired(), Email()])
    child_name = StringField("Child's Name", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm', validators=[DataRequired(), EqualTo('password') ])

    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("That email is already in use. Please register with a different one.")

# LOGIN FORM 
class LoginForm(FlaskForm):
    class Meta(AutoAttrMeta):
        pass
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')

# UPDATE ACCOUNT FORM
class UpdateAccountForm(FlaskForm):
    class Meta(AutoAttrMeta):
        pass
    email = EmailField('Email', validators=[DataRequired(), Email()])
    child_name = StringField("Child's Name", validators=[DataRequired()])
    picture = FileField("Update Child's Photo",  validators=[FileAllowed(['jpg','png'])])
    babys_age = DateField('DatePicker', format='%Y-%m-%d', validators=[DataRequired()])
    doctors_email = EmailField("Doctor's Email Address", validators=[DataRequired(), Email()])

    submit = SubmitField('Update')

    # QUERY THE DATABSE TO SEE IF THE USERNAME AND EMAIL ARE TAKEN.
    def validate_email(self, email): 
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already in use. Please choose a different one')

class DoctorEmailForm(FlaskForm):
    class Meta(AutoAttrMeta):
        pass
    email = EmailField('Email', validators=[DataRequired(), Email()])
    child_name = StringField("Child's Name", validators=[DataRequired()])
    document = FileField("Newborn Info File",  validators=[FileAllowed(['txt','doc'])])
    doctors_email = EmailField("Doctor's Email Address", validators=[DataRequired(), Email()])

    submit = SubmitField('Send Email')

    # QUERY THE DATABSE TO SEE IF THE USERNAME AND EMAIL ARE TAKEN.
    def validate_email(self, email): 
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already in use. Please choose a different one')

class FeedForm(FlaskForm):
    method = StringField("Method", validators=[DataRequired()])
    begin = TimeField('Begin Time', validators=[DataRequired()])
    end = TimeField('End Time', validators=[DataRequired()])
    ounces = StringField("Amount(oz)", validators=[DataRequired()])
    spitups = StringField("Spit-ups", validators=[DataRequired()])

    submit = SubmitField('Add')

class DiaperForm(FlaskForm):
    time = TimeField('Time', validators=[DataRequired()])
    info = StringField("Info", validators=[DataRequired()])

    submit = SubmitField('Add')

class SleepForm(FlaskForm):
    begin = TimeField('Begin Time', validators=[DataRequired()])
    end = TimeField('End Time', validators=[DataRequired()])
    reason = StringField("Reason", validators=[DataRequired()])

    submit = SubmitField('Add')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. Please register first')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm', validators=[DataRequired(), EqualTo('password') ])
    submit = SubmitField('Reset Password')