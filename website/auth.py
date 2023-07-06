import functools
from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for, g, session, jsonify
from .users.models import User, Contact, CustomerOrder
from .products.models import Product, Category, Brand
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, search
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import uuid as uuid
import os, secrets
from sqlalchemy.sql import func
import stripe


stripe_keys = {
  'secret_key': 'sk_test_51LwefbJaasrIB7O4tvbZvw1841Q9yoUKxEmykSaKLqYPJPDoQOaCLLAh0iJrJmplm6NjOwSIIYW9Al8acQ996WDo00NAccCHbP',
  'publishable_key': 'pk_test_51LwefbJaasrIB7O42NsLYWLlOa2gGvM7ehDeTqicqbKoRq2EfYOEo0a42AU4kcITbcshI8RQj2HgZQ7x0w77dkoB00veLeVIYD'
}

stripe.api_key = stripe_keys['secret_key']

UPLOAD_FOLDER = 'website/static/images/profile_images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

auth = Blueprint('auth', __name__)

def brands():
    brands = Brand.query.filter(Brand.id==Product.brand_id)
    return brands


def categories():
    categories = Category.query.filter(Category.id==Product.category_id)
    return categories



@auth.route('/logreg', methods=['GET', 'POST'])
def logreg():
    if current_user.is_authenticated:
        if current_user.id == 1:
            flash("You are still logged in Admin", category="error")
            return redirect(url_for('auth.adminhome'))
        if current_user.id >= 2:
            flash("You are still logged in User", category="error")
            return redirect(url_for('auth.home'))
    else:
        return render_template("logregtemp.html")


@auth.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if current_user.is_authenticated:
        if current_user.id >= 2:
            prods = Product.query.filter(Product.stock>0)
            users = User.query.all()

            return render_template("customers/index.html", user=current_user, users=users, products=prods, categories=categories(), brands=brands())

        else:
            flash("Dear Admin, please refrain from doing unwanted behaviour. Gracias!", category="error")
            return redirect(url_for('auth.adminhome'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/result')
@login_required
def result():
    if current_user.is_authenticated:
        if current_user.id >= 2:
            searchword = request.args.get('q')
            products = Product.query.msearch(searchword, fields=['name', 'description'], limit=4)
            return render_template("customers/result.html", user=current_user, products=products, brands=brands(), categories=categories())
        
        else:
            flash("Dear Admin, please refrain from doing unwanted behaviour. Gracias!", category="error")
            return redirect(url_for('auth.adminhome'))
    else:
        return redirect(url_for('auth.login'))



@auth.route('/adminhome', methods=['GET', 'POST'])
@login_required
def adminhome():
    if current_user.is_authenticated:
        if current_user.id == 1:
            products = Product.query.all()
            brands = Brand.query.all()
            categories = Category.query.all()
            users = User.query.all()
            
            return render_template("admin/panelproducts.html", user=current_user, users=users, products=products, categories=categories, brands=brands)
        else:
            flash("You do not have admin privilege to access this page", category="error")
            return redirect(url_for('auth.home'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/getdesc/<int:id>', methods=['GET', 'POST'])
@login_required
def getDesc(id):
    if current_user.is_authenticated:
        if current_user.id >= 2:
            product = Product.query.get_or_404(id)
            users = User.query.all()
            
            return render_template("customers/prodesc.html", user=current_user, users=users, product=product)
        else:
            flash("Dear Admin, please refrain from doing unwanted behaviour. Gracias!", category="error")
            return redirect(url_for('auth.adminhome'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/brands', methods=['GET', 'POST'])
@login_required
def panelBrand():
    if current_user.is_authenticated:
        if current_user.id == 1:
            products = Product.query.all()
            categories = Category.query.all()
            brands = Brand.query.all()
            users = User.query.all()
            
            return render_template("admin/panelbrands.html", user=current_user, users=users, products=products, categories=categories, brands=brands)
        else:
            flash("You do not have admin privilege to access this page", category="error")
            return redirect(url_for('auth.home'))
    else:
        return redirect(url_for('auth.login'))

 
 
@auth.route('/getbrand/<int:id>', methods=['GET', 'POST'])
@login_required
def getBrand(id):
    if current_user.is_authenticated:
        if current_user.id >= 2:
            brand = Product.query.filter_by(brand_id=id)
            users = User.query.all()
            
            return render_template("customers/index.html", user=current_user, users=users, brands=brands(), brand=brand, categories=categories())
        else:
            flash("Dear Admin, please refrain from doing unwanted behaviour. Gracias!", category="error")
            return redirect(url_for('auth.adminhome'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/getcategory/<int:id>', methods=['GET', 'POST'])
@login_required
def getCategory(id):
    if current_user.is_authenticated:
        if current_user.id >= 2:
            get_catprod = Product.query.filter_by(category_id=id)
            users = User.query.all()
            
            return render_template("customers/index.html", user=current_user, users=users, categories=categories(), get_catprod=get_catprod, brands=brands())
        else:
            flash("Dear Admin, please refrain from doing unwanted behaviour. Gracias!", category="error")
            return redirect(url_for('auth.adminhome'))
    else:
        return redirect(url_for('auth.login'))

@auth.route('/categories', methods=['GET', 'POST'])
@login_required
def panelCat():
    if current_user.is_authenticated:
        if current_user.id == 1:
            products = Product.query.all()
            brands = Brand.query.all()
            categories = Category.query.all()
            users = User.query.all()

            return render_template("admin/panelcategories.html", user=current_user, users=users, products=products, categories=categories, brands=brands)
        
        else:
            flash("You do not have admin privilege to access this page", category="error")
            return redirect(url_for('auth.home'))
    else:
        return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    users = User.query.all()
    contact = Contact.query.all()   
    if current_user.id == 1:
        return render_template("admin/profile.html", user=current_user, users=users)
    if current_user.id >= 2:
        return render_template("customers/profile.html", user=current_user, users=users, categories=categories(), brands=brands(), contact=contact)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                if user.id == 1:
                    flash(f'Welcome Admin { user.name }, you have logged in successfully!', category='success')
                    login_user(user, remember=True)
                    session['id'] = current_user.id
                    return redirect(url_for('auth.adminhome'))
                if user.id >= 2:
                    flash(f'Welcome { user.name }, you have logged in successfully!', category='success')
                    login_user(user, remember=True)
                    session['id'] = current_user.id
                    return redirect(url_for('auth.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return redirect(url_for('auth.logreg', user=current_user))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session['id'] = None
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        profile_image = request.files['image1']
        # if user does not select file, return to signup
        if profile_image.filename == '':
            profile_image = 'None'
        elif profile_image and not allowed_file(profile_image.filename):
            flash('Please select an image file', category="error")
            return redirect(url_for('auth.sign_up'))
        elif profile_image and allowed_file(profile_image.filename):
            # Grab Image Name
            pic_filename = secure_filename(profile_image.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # Save that Image
            profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            # Change it to string to save to db
            profile_image = pic_name

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, name=name, profile_image=profile_image, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            session['id'] = current_user.id
            if current_user.id == 1:
                flash(f'Account created! Welcome aboard Admin { current_user.name }!', category='success') 
                return redirect(url_for('auth.adminhome')) 
            if current_user.id >= 2:
                flash(f'Account created! Welcome aboard { current_user.name }!', category='success')
                return redirect(url_for('auth.home'))

    return redirect(url_for('auth.logreg', user=current_user))


@auth.route('/edituser', methods=['GET', 'POST'])
@login_required
def edituser():
    if request.method == 'POST':
        user = User.query.get(request.form.get('id'))
        name = request.form['user.name']
        email = request.form['user.email']
        if len(name) < 2:
            flash('Name must be greater than 1 character.', category="error")
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category="error")
        else:
            user.name = name
            user.email = email
            profile_image = request.files['user.image']
            # if user does not select file, return to signup
            if profile_image.filename == '':
                user.profile_image = current_user.profile_image
            if profile_image and not allowed_file(profile_image.filename):
                flash('Please select an image file', category="error")
                return redirect(url_for('auth.profile'))
            if profile_image and allowed_file(profile_image.filename):
                if user.profile_image == 'None':
                    jsonify()
                else:
                    os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_image))
                # Grab Image Name
                pic_filename = secure_filename(profile_image.filename)
                # Set UUID
                pic_name = str(uuid.uuid1()) + "_" + pic_filename
                # Save that Image
                profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                # Change it to string to save to db
                user.profile_image = pic_name

            db.session.commit()
            flash('Successfully edited your profile!', category='success')

        return redirect(url_for('auth.profile'))


@auth.route('/cart', methods=['GET','POST'])
@login_required
def getCart():
    if current_user.is_authenticated:
        if current_user.id >= 2:
            if 'shopcart' not in session or len(session['shopcart']) <= 0:
                flash("Please add an item first to access Cart!", category="error")
                return redirect(url_for('auth.home'))
            subtotal = 0
            grandtotal = 0
            for key , product in session['shopcart'].items():
                discount = (product['discount']/100) * float(product['price'])
                subtotal += float(product['price']) * int(product['quantity'])
                subtotal -= discount
                tax = ("%.2f" % (.06 * float(subtotal)))
                grandtotal = float("%.2f" % (1.06 * subtotal))
            return render_template("customers/carts.html", user=current_user, tax=tax, grandtotal=grandtotal, brands=brands(), categories=categories())
        
        else:
            flash("Dear Admin, please refrain from doing unwanted behaviour. Gracias!", category="error")
            return redirect(url_for('auth.adminhome'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/addContact', methods=['GET', 'POST'])
@login_required
def addContact():
    if current_user.is_authenticated:
        if current_user.id >= 2:
            if request.method == 'POST':
                rec_name = request.form.get('name')
                phone_num = request.form.get('phoneNum')
                add_mac = request.form.get('add1')
                postcode = request.form.get('postcode')
                add_mic = request.form.get('add2')
                label = request.form.get('label')

                if rec_name == '':
                    recip_name = current_user.name
                elif len(rec_name) < 2:
                    flash('Recipient\'s name must be greater than 1 character.', category="error")
                    return redirect(url_for('auth.profile'))
                else:
                    recip_name = rec_name
                
                if len(add_mac) < 10:
                    flash('Too short address name, be more specific for accurate shipping.', category='error')
                elif len(add_mic) < 10:
                    flash('Too short address name, be more specific for accurate shipping.', category='error')
                else:
                    new_contact = Contact(recipient_name=recip_name, phone_number=phone_num, address_macro=add_mac,
                    postal_code=postcode, address_micro=add_mic, label_as=label, user_id=current_user.id)
                    db.session.add(new_contact)
                    db.session.commit()
                    flash('Your contact information has been successfully established!', category='success')

            return redirect(url_for('auth.profile'))
        
        else:
            flash("Dear Admin, please refrain from doing unwanted behaviour. Gracias!", category="error")
            return redirect(url_for('auth.adminhome'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/editContact', methods=['GET', 'POST'])
@login_required
def editContact():
    if current_user.is_authenticated:
        if current_user.id >= 2:
            if request.method == 'POST':
                contact = Contact.query.get(request.form.get('id'))
                rec_name = request.form['name']
                contact.phone_number = request.form['phone_num']
                add_mac = request.form['add1']
                contact.postal_code = request.form['postcode']
                add_mic = request.form['add2'] 
                label = request.form['label']
                if rec_name == '':
                    contact.recipient_name = contact.recipient_name
                elif len(rec_name) < 2:
                    flash('Recipient\'s name must be greater than 1 character.', category="error")
                    return redirect(url_for('auth.profile'))
                else:
                    contact.recipient_name = rec_name

                if label == '':
                    contact.label_as = contact.label_as
                else:
                    contact.label_as = label

                if len(add_mac) < 10:
                    flash('Too short address name, be more specific for accurate shipping.', category='error')
                    return redirect(url_for('auth.profile'))
                else:
                    contact.address_macro = add_mac

                if len(add_mic) < 10:
                    flash('Too short address name, be more specific for accurate shipping.', category='error')
                    return redirect(url_for('auth.profile'))
                else:
                    contact.address_micro = add_mic
                
                contact.date = func.now()

                db.session.commit()
                flash('Successfully edited Contact Information!', category='success')

                return redirect(url_for('auth.profile'))
        else:
            flash("Dear Admin, please refrain from doing unwanted behaviour. Gracias!", category="error")
            return redirect(url_for('auth.adminhome'))
    else:
        return redirect(url_for('auth.login'))


# Remove unwanted details from shopping cart
def updateshopcart():
    for key, product in session['shopcart'].items():
        session.modified = True
        del product['image']
    return updateshopcart


    
@auth.route('/getOrder')
@login_required
def getOrder():
    if current_user.is_authenticated:
        if current_user.id >= 2:
            if current_user.is_authenticated:
                customer_id = current_user.id
                invoice = secrets.token_hex(5)
                updateshopcart()
                try:
                    order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['shopcart'])
                    db.session.add(order)
                    db.session.commit()
                    session.pop('shopcart')
                    flash('Your order has been successfully sent!', category='success')
                    return redirect(url_for('auth.orders', invoice=invoice))
                except Exception as e:
                    print(e)
                    flash('Something went wrong while getting order!', category='error')
                    return redirect(url_for('auth.getCart'))
        else:
            flash("Dear Admin, please refrain from doing unwanted behaviour. Gracias!", category="error")
            return redirect(url_for('auth.adminhome'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        if current_user.id >= 2:
            grandTotal = 0
            subTotal = 0
            customer_id = current_user.id
            customer = User.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.description).first()
            for key , product in orders.orders.items():
                discount = (product['discount']/100) * float(product['price'])
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount
                tax = ("%.2f" % (.06 * float(subTotal)))
                grandTotal = ("%.2f" % (1.06 * float(subTotal)))
                usd_amount = ("%.2f" % (float(grandTotal)/55.94))
            
            return render_template('customers/order.html', user=current_user, invoice=invoice, tax=tax, subTotal=subTotal, grandTotal=grandTotal, customer=customer, orders=orders, key=stripe_keys['publishable_key'], usd_amount=usd_amount)

        else:
            flash("Dear Admin, please refrain from doing unwanted behaviour. Gracias!", category="error")
            return redirect(url_for('auth.adminhome'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/charge', methods=['POST'])
@login_required
def charge():
    invoice = request.form.get('invoice')
    # Amount in cents
    amount = request.form.get('amount')

    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Sparkle Shop'
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id).order_by(CustomerOrder.id.description).first()
    orders.status = 'Paid'
    db.session.commit()
    return render_template('customers/thanks.html', amount=amount)



def allowed_file(filename):     
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view