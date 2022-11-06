from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, LoginManager, UserMixin, logout_user, login_required
import os
from datetime import datetime


base_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir,'users.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = '4d4c18d8d33c8c704705'

db = SQLAlchemy(app)
login_manager = LoginManager(app)

@app.before_first_request
def create_tables():
    db.create_all()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable =False)
    last_name = db.Column(db.String(50), nullable =False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash =  db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return f'User<{self.username}>'

class Blogpost(db.Model):
    __tablename__ = 'blogposts'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default= datetime.utcnow)

@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))

#route to home page
@app.route('/')
def index():
    blogposts = Blogpost.query.all()

    context = {
        'blogposts': blogposts
    }
    
    return render_template ("index.html", **context)

#to login an already existing user
@app.route('/login', methods = ['GET', 'POST'])
def login():
    #check if user has created an account
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username = username).first()

    #checking if the username and the password are the same
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return redirect(url_for('index'))

    return render_template('login.html')

#function to logout a user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#route for creating a new account page
@app.route('/signup', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST' :
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        #if it is the first time the user in doing this
        user =  User.query.filter_by(username= username).first()
        if user :
            return redirect(url_for('register'))

        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            return redirect(url_for('register'))
        
        #generate password from password passed by user and generate a password and then save it inside password_hash
        password_hash = generate_password_hash(password)

        new_user = User(first_name = first_name, last_name = last_name, username = username, email = email, password_hash= password_hash)
        
        db.session.add(new_user) #add user to db
        db.session.commit() #save user to db

        #redirect to login page after user has been saved to the db
        return redirect(url_for('login'))
        
    return render_template('signup.html')

#route for contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

#route for profile page
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

#route for creating a new blog post page
@app.route ('/create_blog')
@login_required
def create_blog():
    return render_template('create_blog.html')

#function handling the addiion of a new blog post
@app.route('/create_blog', methods = ['GET', 'POST'])
@login_required
def post():
    if request.method == 'POST':        
        title = request.form.get('title')
        author = current_user.username
        content = request.form.get('content')

        post = Blogpost( title = title, author = author, content = content, created_at = datetime.utcnow())

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('index'))

#route for editing a blog
@app.route('/update/<int:id>/', methods = ['GET', 'POST'])
@login_required
def update(id):
    blogposts_to_update = Blogpost.query.get_or_404(id)

    if request.method == 'POST' :
        blogposts_to_update.title = request.form.get('title')
        blogposts_to_update.content = request.form.get('content')

        db.session.commit()
        
        return redirect(url_for("index"))

    context = {
        'blogposts': blogposts_to_update
    }

    return render_template('update.html', **context)

#route for deleting a blog
@app.route('/delete/<int:id>/', methods = ['GET'])
@login_required
def delete(id):
    blogposts_to_delete = Blogpost.query.get_or_404(id)

    db.session.delete(blogposts_to_delete)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/view_blog/<int:id>/', methods = ['GET'])
def view_blog(id):
    
    blogposts_to_view = Blogpost.query.get_or_404(id)
    
    context = {
        'blogposts': blogposts_to_view
    }

    return render_template('view_blog.html', **context)

if __name__ == "__main__":
    app.run(debug=True)