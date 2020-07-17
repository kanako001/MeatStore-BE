from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_heroku import Heroku
import io

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://ymmwlgmljxcqsy:ccf5208d8533ffefa0c52369221917e1c26bcd826438b9f9eaf1f96b90fc8c20@ec2-54-146-4-66.compute-1.amazonaws.com:5432/d3et0i60qnm811"

db = SQLAlchemy(app)
ma = Marshmallow(app)

heroku = Heroku(app)
CORS(app)

statusKeep = ["NOT_LOGGED_IN"]

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(), nullable=False, unique=True)
  password = db.Column(db.String(), nullable=False) 

  def __init__(self, email, password):
    self.email = email
    self.password = password

class UserSchema(ma.Schema):
  class Meta:
    fields = ("id", "email", "password")

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


@app.route("/user/create", methods=["POST"])
def create_user():
  if request.content_type != "application/json":
    return jsonify("Error creating user: Data must be sent as JSON")

  post_data = request.get_json()
  email = post_data.get("email")
  password = post_data.get("password")

  record = User(email, password)
  db.session.add(record)
  db.session.commit()

  return jsonify("User created successfully")

class UserVerification:
  currentStatus = ""

  def __init__(self, status="NOT_LOGGED_IN"):
    self.currentStatus = status

  def changeLoginStatus(self):
    return self.currentStatus

@app.route("/user/verification", methods=["POST"])
def verify_user():
  if request.content_type != "application/json":
    return jsonify("Error verifying user: Data must be sent as JSON")

  post_data = request.get_json()
  email = post_data.get("email")
  password = post_data.get("password")
  
  stored_password = db.session.query(User.password).filter(User.email == email).first()

  if stored_password is None:
    user = UserVerification("NOT_LOGGED_IN")
    statusKeep.append(user.changeLoginStatus())
    return jsonify("User not verified")

  if password != stored_password[0]:
    user = UserVerification("NOT_LOGGED_IN")
    statusKeep.append(user.changeLoginStatus())
    return jsonify("User not verified")
    
  if password == stored_password[0]:
    user = UserVerification("LOGGED_IN")
    statusKeep.append(user.changeLoginStatus())
    return jsonify("User verified")

@app.route("/user/logged_in", methods=["GET"])
def get_current_status():
  # return jsonify(statusKeep[-1])
  if(statusKeep[-1] != "LOGGED_IN"):
    status = "NOT_LOGGED_IN"
    statusKeep[:] = []
    return jsonify(status)

  if(statusKeep[-1] == "LOGGED_IN"):
    status = "LOGGED_IN"
    statusKeep[:] = []
    return jsonify(status)
  
    
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



if __name__ == "__main__":
  app.run(debug=True)