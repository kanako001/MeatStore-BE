from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_heroku import Heroku
from flask_bcrypt import Bcrypt
import io

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://mgmnrckxllwthb:3febec993418d7c10b3f03b134d7c9c7f05f8e7b79b888ea8d5db550deba7850@ec2-3-229-210-93.compute-1.amazonaws.com:5432/d2g8m05t9qlmtc"

db = SQLAlchemy(app)
ma = Marshmallow(app)

heroku = Heroku(app)
CORS(app)
bcrypt = Bcrypt(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(), nullable=False, unique=True)
  password = db.Column(db.String(), nullable=False)

  def __init__(self, username, password):
    self.username = username
    self.password = password

class UserSchema(ma.Schema):
  class Meta:
    fields = ("id", "username", "password")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  product_name = db.Column(db.String(), nullable=False)
  product_price = db.Column(db.Integer, nullable=False)
  product_description = db.Column(db.String(), nullable=False)
  data = db.Column(db.String(), nullable=False)

  def __init__(self, product_name, product_price, product_description, data):
    self.product_name = product_name
    self.product_price = product_price
    self.product_description = product_description
    self.data = data

class ProductSchema(ma.Schema):
  class Meta:
    fields = ("id", "product_name", "product_price", "product_description", "data")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class CartItems(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  cart = db.Column(db.PickleType())

  def __init__(self, cart):
    self.cart = cart

class CartSchema(ma.Schema):
  class Meta:
    fields = ("id", "cart")

cart_schema = CartSchema()
carts_Schema = CartSchema(many=True)


@app.route("/user/create", methods=["POST"])
def create_user():
  if request.content_type != "application/json":
    return jsonify("Error creating user: Data must be sent as JSON")

  post_data = request.get_json()
  username = post_data.get("username")
  password = post_data.get("password")

  username_check = db.session.query(User.username).filter(User.username == username).first()
  if username_check is not None:
    return jsonify("Username taken")

  hashed_password = bcrypt.generate_password_hash(password).decode("utf8")

  record = User(username, hashed_password)
  db.session.add(record)
  db.session.commit()

  return jsonify("User created successfully")


@app.route("/user/verification", methods=["POST"])
def verify_user():
  if request.content_type != "application/json":
    return jsonify("Error verifying user: Data must be sent as JSON")

  post_data = request.get_json()
  username = post_data.get("username")
  password = post_data.get("password")
  
  stored_password = db.session.query(User.password).filter(User.username == username).first()

  if stored_password is None:
    return jsonify("User not verified")

  valid_password_check = bcrypt.check_password_hash(stored_password[0], password)
  if valid_password_check == False:
    return jsonify("User not verified")
    
  return jsonify("User verified")  
    
@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User).all()
    return jsonify(users_schema.dump(all_users))

@app.route("/user/get/<id>", methods=["GET"])
def get_user_by_id(id):
  user = db.session.query(User).filter(User.id == id).first()
  return jsonify(user_schema.dump(user))

@app.route("/user/delete/<id>", methods=["DELETE"])
def delete_user(id):
  user_data = db.session.query(User).filter(User.id == id).first()
  db.session.delete(user_data)
  db.session.commit()
  return jsonify("User deleted successfully")

@app.route("/product/add", methods=["POST"])
def add_product():
  if request.content_type != "application/json":
    return jsonify("Error verifying user: Data must be sent as JSON")
  post_data = request.get_json()
  product_name = post_data.get("name")
  product_price = post_data.get("price")
  product_description = post_data.get("description")
  data = post_data.get("data")

  new_product = Product(product_name, product_price, product_description, data)
  db.session.add(new_product)
  db.session.commit()

  return jsonify("Product added successfully")

@app.route("/product/get", methods=["GET"])
def get_product():
  all_products = db.session.query(Product).all()
  return jsonify(products_schema.dump(all_products))

@app.route("/product/get/<id>", methods=["GET"])
def get_product_by_id(id):
  product_data = db.session.query(Product).filter(Product.id == id).first()
  return jsonify(product_schema.dump(product_data))


@app.route("/product/delete/<id>", methods=["DELETE"])
def delete_product(id):
  product_data = db.session.query(Product).filter(Product.id == id).first()
  db.session.delete(product_data)
  db.session.commit()
  return jsonify("product deleted successfully")


@app.route("/item/add", methods=["POST"])
def add_cart_items():
  if request.content_type != "application/json":
    return jsonify("Error verifying cart item: Data must be sent as JSON")
  post_data = request.get_json()
  cart = post_data.get("cart")

  new_item = CartItems(cart)
  db.session.add(new_item)
  db.session.commit()

  return jsonify("Item added successfully")

@app.route("/items/get", methods=["GET"])
def get_cart_items():
  all_items = db.session.query(CartItems).all()
  return jsonify(carts_Schema.dump(all_items))

@app.route("/items/delete", methods=["DELETE"])
def delete_cart_items():
  all_cart_items = db.session.query(CartItems).\
  delete()
  db.session.commit()

  return jsonify("items deleted")





if __name__ == "__main__":
  app.run(debug=True)