import base64
import pymongo
import sys
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from bson.json_util import dumps
from werkzeug.security import generate_password_hash, check_password_hash
import gridfs
import certifi
ca = certifi.where()


app = Flask(__name__)
app.secret_key = 'your_secret_key'

uri = "mongodb+srv://nicholasong:password1234@cluster0.3dsnomm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, tlsCAFile=ca)
db = client.GiftGenie
users_collection = db.users
items_collection = db.items
recipients_collection = db.recipients
orders_collection = db.orders
cart_collection = db.carts
grid_fs = gridfs.GridFS(db)


COMMON_COLORS = ['Red', 'Green', 'Blue', 'Yellow', 'Black', 'White', 'Orange']

ALLOWED_CATEGORIES = ['Technology', 'Accessories', 'Fragrance', 'Lifestyle', 'Beauty']

@app.route('/')
def index():
    if 'user_id' in session:
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
        if user:
            return render_template('homepage.html', user=user)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            
            session['user_id'] = str(user['_id'])
            return redirect(url_for('index'))
        else:
            return "Invalid email or password. Please try again."
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        birthday = request.form['birthday']

        if password != confirm_password:
            return "Passwords do not match. Please try again."

        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return "Email already exists. Please log in."

        hashed_password = generate_password_hash(password)
        user_data = {
            'name': name,
            'surname': surname,
            'email': email,
            'password': hashed_password,
            'birthday': birthday
        }
        print ('sending')
        res = users_collection.insert_one(user_data)
        print (res)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/recipients')
def recipients():
    if 'user_id' in session:
        user_id = session['user_id']
        user_recipients = recipients_collection.find({'user_id': user_id})
        return render_template('recipients.html', recipients=user_recipients, categories=ALLOWED_CATEGORIES,colors=COMMON_COLORS)
    return redirect(url_for('login'))

@app.route('/create_recipient', methods=['POST'])
def create_recipient():
    if 'user_id' in session:
        user_id = session['user_id']
        name = request.form['name']
        birthday = request.form['birthday']
        gender = request.form['gender']
        likes = request.form.getlist('likes')
        category = request.form['category']
        budget = float(request.form['budget'])

        recipient_data = {
            'user_id': user_id,
            'name': name,
            'birthday': birthday,
            'gender': gender,
            'likes': likes,
            'category': category,
            'budget': budget
        }
        recipients_collection.insert_one(recipient_data)
        return redirect(url_for('recipients'))
    return redirect(url_for('login'))

@app.route('/discover', methods=['GET', 'POST'])
def discover():
    if 'user_id' in session:
        user_id = session['user_id']
        user_recipients = recipients_collection.find({'user_id': user_id})
        if request.method == 'POST':
            recipient_id = request.form['recipient_id']
            recipient = recipients_collection.find_one({'_id': ObjectId(recipient_id)})
            recipient_likes = recipient['likes']
            recipient_category = recipient['category']
            recipient_budget = recipient['budget']


            pipeline = [{ "$addFields": {"priority": {"$cond": {"if": { "$in": ["$color", recipient_likes] },"then": 1,"else": 2}},"budget": recipient_budget,"category": recipient_category}},{ "$sort": {"priority": 1,"price": 1,  "category": 1,"color": 1}},{ "$project": { "priority": 0 }}  ]
            
            
            items = items_collection.aggregate(pipeline)

            new_items = []

        
            for item in items:
                print('ayo!\n\n\n', item, file=sys.stderr)
                image_id = item['image_id']
                image_data = grid_fs.get(image_id).read()
                item['image_data'] = base64.b64encode(image_data).decode('utf-8')
                new_items.append(item)
            return render_template('discover.html', recipients=user_recipients, items=new_items)
        
        return render_template('discover.html', recipients=user_recipients)
    return redirect(url_for('login'))

@app.route('/cart')
def cart():
    if 'user_id' in session:
        user_id = session['user_id']
        
        cart_data = cart_collection.find_one({'user_id': user_id})
        if cart_data:
            cart_items = []
            for item_id in cart_data['items']:
                item = items_collection.find_one({'_id': ObjectId(item_id)})
                if item:
                    cart_items.append(item)
            
            return render_template('cart.html', cart_items=cart_items)
        else:
            return render_template('cart.html', cart_items=[])
    else:
        
        return redirect(url_for('login'))


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' in session:
        user_id = session['user_id']
        item_id = request.form['item_id']
        
        existing_cart = cart_collection.find_one({'user_id': user_id})
        if existing_cart:
            cart_items = existing_cart.get('items', [])
            if item_id not in cart_items:
                cart_items.append(item_id)
            cart_collection.update_one({'_id': existing_cart['_id']}, {'$set': {'items': cart_items}})
        else:
            cart_collection.insert_one({'user_id': user_id, 'items': [item_id]})
        
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/remove_item', methods=['POST'])
def remove_item():
    if 'user_id' in session:
        user_id = session['user_id']
        item_id = request.form['item_id']
        
        user_cart = cart_collection.find_one({'user_id': user_id})
        
        if user_cart:
            cart_items = user_cart.get('items', [])
            
            if item_id in cart_items:
                cart_items.remove(item_id)
                
                cart_collection.update_one({'_id': user_cart['_id']}, {'$set': {'items': cart_items}})
                return jsonify({'success': True})
        
    return jsonify({'success': False})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' in session:
        user_id = session['user_id']
        
        user_cart = cart_collection.find_one({'user_id': user_id})
        if user_cart:
            cart_items = []
            total_price = 0  
            for item_id in user_cart.get('items', []):
                item = items_collection.find_one({'_id': ObjectId(item_id)})
                if item:
                    cart_items.append(item)
                    total_price += item['price']  
                    
            if request.method == 'POST':
                full_name = request.form['full_name']
                recipient_address = request.form['recipient_address']
                contact_number = request.form['contact_number']
                
 
                order = {
                    'user_id': user_id,
                    'items': user_cart['items'],
                    'total_price': total_price,
                    'full_name': full_name,
                    'recipient_address': recipient_address,
                    'contact_number': contact_number
                }
                
                orders_collection.insert_one(order)
                
                cart_collection.update_one({'_id': user_cart['_id']}, {'$set': {'items': []}})
                
                return "Order confirmed!"
            new_items = []

            for item in cart_items:
                print('ayo!\n\n\n', item, file=sys.stderr)
                image_id = item['image_id']
                image_data = grid_fs.get(image_id).read()
                item['image_data'] = base64.b64encode(image_data).decode('utf-8')
                new_items.append(item)
            
            return render_template('checkout.html', cart_items=new_items, total_price=total_price)
        
        return redirect(url_for('cart'))
    
    return redirect(url_for('login'))

from bson.objectid import ObjectId

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        
        user_orders = orders_collection.find({'user_id': user_id})

        orders_with_items = []
        for order in user_orders:
            items_ordered = []
            for item_id in order['items']:
                item = items_collection.find_one({'_id': ObjectId(item_id)})
                if item:
                    items_ordered.append(item)
            order['items_ordered'] = items_ordered
            orders_with_items.append(order)
        
        return render_template('profile.html', user=user, orders=orders_with_items)
    
    return redirect(url_for('login'))



@app.route('/item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        specification = request.form['specification']
        price = float(request.form['price'])
        category = request.form['category']
        print('Hello world!', request.files, file=sys.stderr)
        
        if 'image' not in request.files:
            return "No image provided. Please upload an image."
        
        image = request.files['image']
        if image.filename == '':
            return "No selected image. Please choose an image."
        
        if image:
       
            image_id = grid_fs.put(image)
        else:
            return "Invalid image format. Please upload a valid image."
        
        if category not in ALLOWED_CATEGORIES:
            return "Invalid category. Please select from allowed categories."

        item_data = {
            'name': name,
            'specification': specification,
            'price': price,
            'category': category,
            'image_id': image_id
        }
        items_collection.insert_one(item_data)
        return redirect(url_for('index'))

    return render_template('item.html', colors=COMMON_COLORS, categories=ALLOWED_CATEGORIES)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
