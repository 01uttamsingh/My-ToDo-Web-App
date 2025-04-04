from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = "noEntryinTheDatabase"  # Secret key for session management

# MongoDB Atlas Configuration for your existing tododb
app.config["MONGO_URI"] = "mongodb+srv://main_user:mainUser@maincluster.nokixau.mongodb.net/tododb?retryWrites=true&w=majority&appName=mainCluster"
mongo = PyMongo(app)

# Redirect root to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Dashboard: Only accessible after login
@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    todos = mongo.db.todo  # Accessing 'todo' collection
    if request.method == "POST":
        title = request.form.get('title')
        desc = request.form.get('desc')
        if title and desc:
            todos.insert_one({
                "title": title,
                "desc": desc,
                "user_id": session['user_id'],
                "date_created": datetime.utcnow()
            })
    allTodo = list(todos.find({"user_id": session['user_id']}))
    return render_template('index.html', allTodo=allTodo, name=session.get('name'))

# Delete To-Do
@app.route('/delete/<id>')
def delete(id):
    todos = mongo.db.todo
    todos.delete_one({"_id": ObjectId(id), "user_id": session['user_id']})
    return redirect(url_for('dashboard'))

# Update To-Do
@app.route('/update/<id>', methods=["GET", "POST"])
def update(id):
    todos = mongo.db.todo
    todo = todos.find_one({"_id": ObjectId(id), "user_id": session['user_id']})
    if request.method == "POST":
        updated_title = request.form.get('title')
        updated_desc = request.form.get('desc')
        todos.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"title": updated_title, "desc": updated_desc}}
        )
        return redirect(url_for('dashboard'))
    return render_template('update.html', todo=todo)

# User Registration
@app.route('/register', methods=["GET", "POST"])
def register():
    users = mongo.db.users  # Accessing 'users' collection
    if request.method == "POST":
        name = request.form.get('name')
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        existing_user = users.find_one({"user_id": user_id})
        if existing_user:
            flash("User ID already exists. Please choose a different one.", "warning")
            return redirect(url_for('register'))
        users.insert_one({"name": name, "user_id": user_id, "password": password})
        flash("Registration successful. Please login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# User Login
@app.route('/login', methods=["GET", "POST"])
def login():
    users = mongo.db.users
    if request.method == "POST":
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        user = users.find_one({"user_id": user_id, "password": password})
        if user:
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Feedback redirect
@app.route('/feedback')
def feedback():
    return redirect("https://forms.gle/pGmo4KAVS3YLvdKQ8")

if __name__ == '__main__':
    app.run(debug=True)
