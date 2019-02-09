import os, random, re
from datetime import date, datetime
from PIL import Image
from flask import render_template, redirect, abort, url_for, flash, request
from parenthelper import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from parenthelper.models import User, Feed, Diaper, Sleep
from parenthelper.forms import RegistrationForm, LoginForm, UpdateAccountForm, FeedForm, SleepForm, DiaperForm, RequestResetForm, ResetPasswordForm, DoctorEmailForm
from flask_mail import Message

import csv

@app.route('/')
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data.lower(), child_name=form.child_name.data, password=hashed_password)
        db.session.add(user) # Adding created user into the database
        db.session.commit()  # Saving the user
        print ("User has been added to database")
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
    
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('homepage', user_id=user.id))
        else:
            flash("Log in unsuccessful. Please check email and password.", "danger")
    return render_template('login.html', title='Login', form=form)

def calculate_age(born):
    today = date.today()
    age_in_years = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    months = (today.month - born.month - (today.day < born.day)) %12
    age = today - born
    age_in_days = age.days
    if age_in_years >= 1:
        return '{} years old'.format(age_in_years)
    elif months >= 1:
        return '{} months old'.format(months)
    elif age_in_days <= 30:
        return '{} days old'.format(age_in_days)
 
@app.route('/home')
@login_required
def homepage():
    user = User.query.get(current_user.id)
    birth = calculate_age(current_user.babys_age)
    feedEntries = Feed.query.filter_by(user_id=user.id)
    diaperEntries = Diaper.query.filter_by(user_id=user.id)
    sleepEntries = Sleep.query.filter_by(user_id=user.id)

    return render_template('schedules.html', user=user, birth=birth, feedEntries=feedEntries, diaperEntries=diaperEntries, sleepEntries=sleepEntries, title="Homepage")

@app.route('/home/feedpage', methods=['GET','POST'])
@login_required
def feedpage():
    user = User.query.filter_by(email=current_user.email)
    birth = calculate_age(current_user.babys_age)
    form = FeedForm()
    if form.validate_on_submit():
        entry = Feed(method=form.method.data, begin_time=form.begin.data, end_time=form.end.data, ounces=form.method.data, spitups=form.spitups.data, user_id=current_user.id)
        db.session.add(entry)
        db.session.commit()
        flash('Your feeding entry has been created!', 'success')
        return redirect(url_for('homepage'))
    return render_template('feed.html', user=user, birth=birth, form=form, title="Feedpage")

@app.route('/home/diaperpage', methods=['GET','POST'])
@login_required
def diaperpage():
    user = User.query.filter_by(email=current_user.email)
    birth = calculate_age(current_user.babys_age)
    form = DiaperForm()
    if form.validate_on_submit():
        entry = Diaper(time=form.time.data, info=form.info.data, user_id=current_user.id)
        db.session.add(entry)
        db.session.commit()
        flash('Your diaper change entry has been created!', 'success')
        return redirect(url_for('homepage'))
    return render_template('diaper.html', user=user, birth=birth, form=form, title="Diaperpage")

@app.route('/home/sleeppage', methods=['GET','POST'])
@login_required
def sleeppage():
    user = User.query.filter_by(email=current_user.email)
    birth = calculate_age(current_user.babys_age)
    form = SleepForm()
    if form.validate_on_submit():
        entry = Sleep(begin_time=form.begin.data, end_time=form.end.data, reason=form.reason.data, user_id=current_user.id)
        db.session.add(entry)
        db.session.commit()
        flash('Your sleep entry has been created!', 'success')
        return redirect(url_for('homepage'))
    return render_template('sleep.html', user=user, birth=birth, form=form, title="Sleeppage")

def randomFilename():  # WAY TO GET AROUND CONSTANT ERROR FROM USING OS.URANDOM()
    random_hex = 'p_'
    for i in range(1,9):
        random_hex += random.choice('abcdefghijklmnopqrstuvwxyz123456789')
    return random_hex

def save_picture(form_picture):
    random_fn = randomFilename()
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_fn + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.child_name = form.child_name.data
        current_user.email = form.email.data
        current_user.babys_age = form.babys_age.data
        current_user.doctors_email = form.doctors_email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET': 
        form.child_name.data = current_user.child_name
        form.email.data = current_user.email
        form.babys_age.data = current_user.babys_age
        form.doctors_email.data = current_user.doctors_email
        
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    print os.getenv("GMAIL_USER")
    msg = Message('Password Reset Request', sender='coderrhodes@gmail.com', recipients=[user.email])
    msg.body = '''To reset your password, visit the following link:
{}
If you did not make this request then simply ignore this email and no changes will be made.
'''.format(url_for('reset_token', token=token, _external=True))
    print "Email sent"
    mail.send(msg)

@app.route('/reset_password', methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

#  THIS CODE IS USED TO COVERT THE CURRENT USERS DATA INTO AN EXCEL FILE TO BE EMAILED TO YOUR DOCTOR
@app.route('/home/feed_csv')
def convert_feed_file(): 
    with open('Feed.csv', 'wb') as csvfile:
        fieldnames = ['id', 'Date', 'Method', 'Begin', 'End', 'Ounces', 'Spitups']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        data = db.session.query(Feed).filter_by(user_id=current_user.id).all()
        rows = []
        for row in data:
            rows.append(
                {
                    'id': row.id,
                    'Date': row.day,
                    'Method': row.method,
                    'Begin': row.begin_time,
                    'End': row.end_time,
                    'ounces': row.ounces,
                    'spitups': row.spitups
                }
            )
        print rows
        for row in rows:
            print row
            writer.writerow(dict(
            (k, v.encode('utf-8') if type(v) is unicode else v) for k, v in row.iteritems() ))
            flash('Your file has been downloaded', 'success')
        return redirect(url_for('homepage'))

@app.route('/home/diaper_csv')
def convert_diaper_file(): 
    with open('Diaper.csv', 'wb') as csvfile:
        fieldnames = ['id', 'Date', 'Time', 'Info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        data = db.session.query(Diaper).filter_by(user_id=current_user.id).all()
        rows = []
        for row in data:
            rows.append(
                {
                    'id': row.id,
                    'Date': row.day,
                    'Time': row.time,
                    'Info': row.info
                }
            )
        print rows
        for row in rows:
            print row
            writer.writerow(dict(
            (k, v.encode('utf-8') if type(v) is unicode else v) for k, v in row.iteritems() ))
            flash('Your file has been downloaded', 'success')
        return redirect(url_for('homepage'))

@app.route('/home/sleep_csv')
def convert_sleep_file(): 
    with open('Sleep.csv', 'wb') as csvfile:
        fieldnames = ['id', 'Date', 'Begin', 'End', 'Reason']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        data = db.session.query(Sleep).filter_by(user_id=current_user.id).all()
        rows = []
        for row in data:
            rows.append(
                {
                    'id': row.id,
                    'Date': row.day,
                    'Begin': row.begin_time,
                    'End': row.end_time,
                    'Reason': row.reason
                }
            )
        print rows
        for row in rows:
            print row
            writer.writerow(dict(
            (k, v.encode('utf-8') if type(v) is unicode else v) for k, v in row.iteritems() ))
            flash('Your file has been downloaded', 'success')
        return redirect(url_for('homepage'))

#======== CONVERTING COMPLETE ============================================================================

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))