from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)
import re
import random
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://bradley121901:ZtVm8nvYOKb4y0uB@cluster0.9vshs1v.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client['Web']
# checkout page,


@app.route('/', methods=['GET', 'POST'])
def signin():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    if db.Users.find_one({'username': username}) is not None:
      data = db.Users.find_one({'username': username})
      print(password)
      print(data)
      if data:
        if password == data.get('password'):
          return redirect(url_for('home', username=username))
  return render_template('signin.html')


@app.route('/sell/<username>', methods=['GET', 'POST'])
def sell(username):
  if request.method == "POST":
    name = request.form['name']
    price = request.form['price']
    description = request.form['description']
    photo = request.files['photo']
    productid = random.randint(1, 100000)
    
    check = db.Products.find_one({"id": productid})
    while check:
      productid = random.randint(1, 100000)
      check = db.Products.find_one({"id": productid})
      
    db.Products.insert_one({
      "id":productid,
      "username": username,
      "name": name,
      "price": price,
      "description": description}
   )
    return redirect(url_for('sell', username=username))
  else:
    return render_template('sell.html', username=username)



@app.route('/home/<username>')
def home(username):
  products = db.Products.find()
  return render_template('home.html', username=username, products=products)


@app.route('/products/<username>', methods=["POST", "GET"])
def products(username):
  
  if request.method == "POST":
    id = int(request.form["productid"])
    check = db.Products.find_one({"id": id, "username":username})
    if check:
      db.Products.delete_one({"id":id, "username":username})
    return redirect(url_for('products', username=username))
  else:
    products = db.Products.find({"username":username})
    return render_template('products.html', username=username, products=products)







def check_password(password):
  if len(password) < 8:
    return False
  isUpper = False
  isSpecial = False
  isNumber = False
  for i in range(len(password)):
    if 65 <= ord(password[i]) and 90 >= ord(password[i]):
      isUpper = True
    elif 33 <= ord(password[i]) and 47 >= ord(password[i]):
      isSpecial = True
    elif 48 <= ord(password[i]) and 57 >= ord(password[i]):
      isNumber = True
  if isUpper == isSpecial == isNumber == True:
    return True
  else:
    return False


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    name = request.form['name']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    repeatpassword = request.form['repeatpassword']
    pattern = r'^\S+@\S+\.\S+'
    if (password == repeatpassword != " " and check_password(password)
        and db.Users.find_one({'username': username}) is None
        and re.match(pattern, email)):
      db.Users.insert_one({
          "username": username,
          "password": password,
          "name": name,
          "email": email
      })
      return redirect(url_for('signin'))
    else:
      return redirect(url_for('register'))

  return render_template('register.html')


@app.route('/about/<username>', methods=['GET', 'POST'])
def about(username):
  if request.method == 'POST':
    chatbot_responses = {
        "hello": "Hello, how can I help you?",
        "how are you": "I'm doing well, thank you for asking.",
        "bye": "Goodbye! Have a good day",
        "rick": "roll",
        "1+1":"11"
    }
    data = request.get_json()
    user_message = data['message']
    m = chatbot_responses.get(user_message)
    return jsonify({'response': str(m)})
  else:
    return render_template('about.html', username=username)

if __name__ == '__main__':
  app.run(debug=True)
