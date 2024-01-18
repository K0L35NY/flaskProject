from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "klucz_tajny"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@app.route('/')
def home():
    if 'user_id' not in session:
        # User is not logged in, redirect to login page
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    if user:
        # User is logged in, render relevant page for the user
        return render_template('index.html', user=user)
    else:
        # Invalid session, redirect to login
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # Store user_id in session to indicate user is logged in
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            # If no matching user found, show an error message
            error = 'Invalid username or password.'
            flash(error)

    # If it's a GET request or login failed, render the login form
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    # Clear user session data to log out
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        try:
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()  # Commit the changes to the database
            flash('Your account has been created successfully!', 'success')
            return redirect(url_for('login'))
        except IntegrityError as e:
            db.session.rollback()
            flash('Error: This username is already used.')
    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)
