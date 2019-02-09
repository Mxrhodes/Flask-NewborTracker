from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from parenthelper import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    child_name = db.Column(db.String(30), nullable=False) 
    email = db.Column(db.String(80),unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    babys_age = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    doctors_email = db.Column(db.String(80),unique=True, default='default@company.com', nullable=False)
    feedings = db.relationship('Feed', backref='parent', lazy=True)
    diaper = db.relationship('Diaper', backref='parent', lazy=True)
    Sleep = db.relationship('Sleep', backref='parent', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
        
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return 'User: {}, {}, {}'.format(self.child_name, self.email, self.image_file)

class Feed(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, default=datetime.today)
    method=db.Column(db.String(10), default="Bottle", nullable=False)
    begin_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    ounces = db.Column(db.Integer, nullable=False)
    spitups = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return 'Feed: {}, {}, {}'.format(self.method, self.ounces, self.day)

# Babies should be producing 6 wet diapers a day
class Diaper(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, default=datetime.today)
    time = db.Column(db.Time, nullable=False)
    info = db.Column(db.Text, nullable=False)    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return 'Diaper: {}, {}'.format(self.time, self.info)

# Babies should be sleep for 16 - 18 hours a day 6 wet diapers a day
class Sleep(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, default=datetime.today)
    begin_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return 'Sleep: {}, {}, {}'.format(self.day, self.end_time, self.reason)

