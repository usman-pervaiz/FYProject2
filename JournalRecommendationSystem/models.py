from JournalRecommendationSystem import db, login_manager, app#, Document
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from flask_login import current_user
class User(UserMixin,db.Document):
    meta = {'collection':'Userdata'}
    username = db.StringField()
    name = db.StringField()
    email = db.StringField()
    image_file = db.StringField(default="default.jpg")
    password = db.StringField()

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)        
        return s.dumps({'email': self.email}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            email = s.loads(token)['email']
            print(email)
        except:
            return None
        return User.objects(email=email).first()
    
class UserDetails(db.Document):
    meta = {'collection':'UserDetailsData'}
    affiliation = db.StringField()
    area_of_interest = db.StringField()
    User_id = db.StringField()


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()