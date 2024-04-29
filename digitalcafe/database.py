import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

products_db = myclient["products"]

order_management_db = myclient["order_management"]

branches_db = myclient["branches"]

def get_product(code):
    products_coll = products_db["products"]

    product = products_coll.find_one({"code":code},{"_id":0})

    return product

def get_products():
    product_list = []

    products_coll = products_db["products"]

    for p in products_coll.find({},{"_id":0}):
        product_list.append(p)

    return product_list

def get_branch(code):
    products_coll = products_db["branches"]
    print(products_coll)
    branches = products_coll.find_one({"code":code})
    print(branches)
    return branches
    

def get_branches():
    branches_list = []

    products_coll = products_db["branches"]

    for p in products_coll.find({}):
        branches_list.append(p)

    return branches_list

def get_user(username):
    customers_coll = order_management_db['customers']
    user=customers_coll.find_one({"username":username})
    return user

def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert(order)

def update_password(username, new_password):
    customers_collection.update_one({"username": username}, {"$set": {"password": new_password}})

    

