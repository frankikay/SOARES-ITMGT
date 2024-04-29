from flask import Flask,redirect
from flask import render_template
from flask import request
from flask import session
from bson.json_util import loads, dumps
from flask import make_response
import database as db
import authentication
import logging
import ordermanagement as om

app = Flask(__name__)

# Set the secret key to some random bytes. 
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branches = db.get_branches()
    return render_template('branches.html', branches=branches)

@app.route('/branchdetails/<branch_code>')
def branchdetails(branch_code):
    print(branch_code)
    branch = db.get_branch(branch_code)
    print(branch)

    return render_template('branchdetails.html', branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods = ['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        error = "Invalid username or password. Please try again."
        return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')

@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()

    try:
        item["qty"] = cart[code]["qty"] + 1
    except:
        item["qty"] = 1
        
    item["qty"] = 1
    item["name"] = product["name"]
    item["price"] = product["price"]
    item["subtotal"] = product["price"]*item["qty"]

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/updatecart', methods=['POST'])
def update_cart():
    cart = session.get("cart", {})
    for code, item in cart.items():
        new_qty = int(request.form.get(f"{code}-qty"))
        cart[code]["qty"] = new_qty
        cart[code]["subtotal"] = cart[code]["price"] * new_qty
    session["cart"] = cart
    return redirect('/cart')

@app.route('/removefromcart')
def remove_from_cart():
    cart = session.get("cart", {})
    code = request.args.get('code', '')
    cart.pop(code)
    session["cart"] = cart
    return redirect('/cart')

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete', page="order complete")

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if "user" not in session or "username" not in session["user"]:
            return redirect('/login') 

        user = users_collection.find_one({"username": session["user"]["username"]})
        if user and user["password"] == old_password:
            if new_password == confirm_password:
                
                users_collection.update_one(
                    {"username": session["user"]["username"]},
                    {"$set": {"password": new_password}}
                )
                return redirect('/')
            else:
                error = "New password and confirm password do not match."
                return render_template('change_password.html', error=error)
        else:
            error = "Old password is incorrect."
            return render_template('change_password.html', error=error)

    return render_template('change_password.html')

@app.route('/api/products',methods=['GET'])
def api_get_products():
    resp = make_response( dumps(db.get_products()) )
    resp.mimetype = 'application/json'
    return resp

@app.route('/api/products/<int:code>',methods=['GET'])
def api_get_product(code):
    resp = make_response(dumps(db.get_product(code)))
    resp.mimetype = 'application/json'
    return resp


