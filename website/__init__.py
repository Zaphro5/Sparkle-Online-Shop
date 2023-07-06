from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_msearch import Search

db = SQLAlchemy()
DB_NAME = "alola_sparkle.sqlite"

search = Search()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'IOSFUW9840923U30FH09F2334F'
    #My old sqlite database
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    #My new sql database
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:''@localhost/alola_sparkle'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    search.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .users.models import User, Contact, CustomerOrder
    from .products.models import Product, Category

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')