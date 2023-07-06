from flask import Flask, Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from flask_login import login_required, current_user
from .products.models import Product, Category, Brand
from . import db
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
import uuid as uuid
import os

UPLOAD_FOLDER = 'website/static/images/product_images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

views = Blueprint('views', __name__)
    

@views.route('/insert/newproduct', methods=['GET', 'POST'])
@login_required
def insertProd():
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('description')
        prod_image = request.files['image2']
        # if user does not select file, return to signup
        if prod_image.filename == '':
            prod_image = 'None'
        elif prod_image and not allowed_file(prod_image.filename):
            flash('Please select an image file', category="error")
            return redirect(url_for('views.insert'))
        elif prod_image and allowed_file(prod_image.filename):
            # Grab Image Name
            prod_filename = secure_filename(prod_image.filename)
            # Set UUID
            prod_name = str(uuid.uuid1()) + "_" + prod_filename
            # Save that Image
            prod_image.save(os.path.join(app.config['UPLOAD_FOLDER'], prod_name))
            # Change it to string to save to db
            prod_image = prod_name
        brand = request.form.get('brand')
        category = request.form.get('category')
        stock = request.form.get('stock')
        discount = request.form.get('discount')
        price = request.form.get('price')


        if len(name) < 1:
            flash('Product name is too short!', category='error')
        else:
            new_product = Product(name=name, description=desc, image=prod_image, brand_id=brand, category_id=category, stock=stock, discount=discount, price=price)
            db.session.add(new_product)
            db.session.commit()
            flash('Product added in Product List!', category='success')

    return redirect(url_for('auth.adminhome'))


@views.route('/insert/newcategory', methods=['GET', 'POST'])
@login_required
def insertCat():
    if request.method == 'POST':
        name = request.form.get('name')

        if len(name) < 1:
            flash('Category name is too short!', category='error')
        else:
            new_category = Category(name=name)
            db.session.add(new_category)
            db.session.commit()
            flash('A new category has been added!', category='success')

    return redirect(url_for('auth.panelCat'))


@views.route('/insert/newbrand', methods=['GET', 'POST'])
@login_required
def insertBrand():
    if request.method == 'POST':
        name = request.form.get('name')

        if len(name) < 1:
            flash('Brand name is too short!', category='error')
        else:
            new_brand = Brand(name=name)
            db.session.add(new_brand)
            db.session.commit()
            flash('A new brand has been added!', category='success')

    return redirect(url_for('auth.panelBrand'))


@views.route('/editProd', methods=['GET', 'POST'])
@login_required
def editProd():
    if request.method == 'POST':
        product = Product.query.get(request.form.get('id'))
        product.name = request.form['name']
        product.description = request.form['description']
        prod_image = request.files['image2']
        # if user does not select file, return to signup
        if prod_image.filename == '':
            product.image = product.image
        if prod_image and not allowed_file(prod_image.filename):
            flash('Please select an image file', category="error")
            return redirect(url_for('views.edit'))
        if prod_image and allowed_file(prod_image.filename):
            # Grab Image Name
            prod_filename = secure_filename(prod_image.filename)
            # Set UUID
            prod_name = str(uuid.uuid1()) + "_" + prod_filename
            if product.image == 'None':
                jsonify()
            else:
                os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
            # Save that Image
            prod_image.save(os.path.join(app.config['UPLOAD_FOLDER'], prod_name))
            # Change it to string to save to db
            product.image = prod_name
        brand = request.form['brand']
        if brand == '':
            product.brand_id = product.brand_id
        else:
            product.brand_id = brand
        category = request.form['category']
        if category == '':
            product.category_id = product.category_id
        else:
            product.category_id = category
        product.stock = request.form['stock']
        product.discount = request.form['discount']
        product.price = request.form['price']
        product.date = func.now()

        db.session.commit()
        flash('Successfully edited product in Product List!', category='success')

        return redirect(url_for('auth.adminhome'))


@views.route('/editCat', methods=['GET', 'POST'])
@login_required
def editCat():
    if request.method == 'POST':
        category = Category.query.get(request.form.get('id'))
        category.name = request.form['name']

        db.session.commit()
        flash('Successfully edited category in Category List!', category='success')

        return redirect(url_for('auth.panelCat'))


@views.route('/editBrand', methods=['GET', 'POST'])
@login_required
def editBrand():
    if request.method == 'POST':
        brand = Brand.query.get(request.form.get('id'))
        brand.name = request.form['name']

        db.session.commit()
        flash('Successfully edited brand in Brand List!', category='success')

        return redirect(url_for('auth.panelBrand'))

        

@views.route('/deleteprod/<id>/', methods=['GET', 'POST'])
@login_required
def deleteProd(id):
    product = Product.query.get(id)
    if product.image == 'None':
        jsonify()
    else:
        os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
    db.session.delete(product)
    db.session.commit()
    flash('Successfully deleted product in Product List!', category='success')

    return redirect(url_for('auth.adminhome'))


@views.route('/deletebrand/<id>/', methods=['GET', 'POST'])
@login_required
def deleteBrand(id):
    brand = Brand.query.get(id)
    db.session.delete(brand)
    db.session.commit()
    flash('Successfully deleted brand in Brand List!', category='success')

    return redirect(url_for('auth.panelBrand'))


@views.route('/deletecat/<id>/', methods=['GET', 'POST'])
@login_required
def deleteCat(id):
    category = Category.query.get(id)
    db.session.delete(category)
    db.session.commit()
    flash('Successfully deleted category in Category List!', category='success')

    return redirect(url_for('auth.panelCat'))


@views.route('/delete-allproducts', methods=['GET','POST'])
@login_required
def deleteAllProducts():
    products = Product.query.all()
    if products:
        for product in products:
            if product.image == 'None':
                jsonify()
            else:
                os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
            db.session.delete(product)
        db.session.commit()
        flash('Successfully cleared the Product List!', category='success')
    else:
        flash('Product List is empty!', category='error')

    return redirect(url_for('auth.adminhome'))


@views.route('/delete-allbrands', methods=['GET','POST'])
@login_required
def deleteAllBrands():
    brands = Brand.query.all()
    if brands:
        for brand in brands:
            db.session.delete(brand)
        db.session.commit()
        flash('Successfully cleared the Brand List!', category='success')
    else:
        flash('Brand List is empty!', category='error')

    return redirect(url_for('auth.panelBrand'))


@views.route('/delete-allcategories', methods=['GET','POST'])
@login_required
def deleteAllCategories():
    categories = Category.query.all()
    if categories:
        for category in categories:
            db.session.delete(category)
        db.session.commit()
        flash('Successfully cleared the Category List!', category='success')
    else:
        flash('Category List is empty!', category='error')

    return redirect(url_for('auth.panelCat'))

@views.route('/addCart', methods=['GET','POST'])
@login_required
def addCart():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        product = Product.query.filter_by(id=product_id).first()
        if request.method == "POST" and product_id and quantity:
            DictItems = {product_id:{"name":product.name, 'price':int(product.price), 'discount':product.discount, 'quantity':int(quantity), 
                        'image':product.image, 'stock':product.stock}}
            if 'shopcart' in session:
                print(session['shopcart'])
                if product_id in session['shopcart']:
                    for key, item in session['shopcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
                    flash("This product is already in your Cart! Adding Quantity +1", category="error")
                else:
                    session['shopcart'] = merge_dict(session['shopcart'], DictItems)
            else:
                session['shopcart'] = DictItems
                return redirect(request.referrer)
                
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


@views.route('/updateOrder/<int:code>', methods=['GET', 'POST'])
@login_required
def updateOrder(code):
    if 'shopcart' not in session or len(session['shopcart']) <= 0:
        return redirect(url_for('auth.home'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        try:
            session.modified = True
            for key, item in session['shopcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    flash('Order successfully updated')
                    return redirect(url_for('auth.getCart', category="success"))
        except Exception as e:
            print(e)
            return redirect(url_for('auth.getCart'))


@views.route('/removeItem/<int:id>', methods=['GET', 'POST'])
@login_required
def removeItem(id):
    if 'shopcart' not in session or len(session['shopcart']) <= 0:
        return redirect(url_for('auth.home'))
    try:
        session.modified = True
        for key, item in session['shopcart'].items():
            if int(key) == id:
                session['shopcart'].pop(key, None)
                return redirect(url_for('auth.getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('auth.getCart'))


@views.route('/clearCart', methods=['GET', 'POST'])
@login_required
def clearCart():
    try:
        session.pop('shopcart', None)
        return redirect(url_for('auth.home'))
    except Exception as e:
        print(e)
    

def allowed_file(filename):     
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def merge_dict(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False