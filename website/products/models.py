from website import db
from sqlalchemy.sql import func

class Product(db.Model):
    __searchable__ = ['name', 'description']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.String(1000), nullable=False, unique=False)
    image = db.Column(db.String(), nullable=True, unique=False)
    stock = db.Column(db.Integer, default=0, unique=False)
    discount = db.Column(db.Integer, default=0, unique=False) 
    price = db.Column(db.Numeric(10,2), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())

    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    brand = db.relationship('Brand', backref=db.backref('brands', lazy=True))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('categories', lazy=True))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)