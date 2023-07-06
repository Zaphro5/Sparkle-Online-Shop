from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import json


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(200))
    profile_image = db.Column(db.String(), nullable=True)
    contact = db.relationship('Contact', backref='user', uselist=False)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_name = db.Column(db.String(200), unique=False, nullable=True)
    phone_number = db.Column(db.Integer, unique=False, nullable=False)
    address_macro = db.Column(db.String(1000), unique=False, nullable=False)
    postal_code = db.Column(db.Integer, unique=False, nullable=False)
    address_micro = db.Column(db.String(1000), unique=False, nullable=False)
    label_as = db.Column(db.String(10), unique=False, nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)



class JsonEncodedDict(db.TypeDecorator):
    impl = db.Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)



class CustomerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice = db.Column(db.String(50), unique=True, nullable =False)
    status = db.Column(db.String(50), default='Pending', nullable =False)
    customer_id = db.Column(db.Integer, unique=False, nullable =False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    orders = db.Column(JsonEncodedDict)
    



