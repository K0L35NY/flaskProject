from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import calendar
import datetime
app = Flask(__name__)
app.secret_key = "klucz_tajny"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


def generate_calendar_data(year=None, month=None):
    # Get the current year and month if not provided
    now = datetime.datetime.now()
    current_year = year or now.year
    current_month = month or now.month

    # Get the number of days in the month and the day of the week for the first day
    _, days_in_month = calendar.monthrange(current_year, current_month)
    first_day_of_month = datetime.date(current_year, current_month, 1)
    first_day_of_week = first_day_of_month.weekday()

    # Determine the number of leading empty cells in the calendar grid
    leading_empty_cells = first_day_of_week

    # Create a list representing the calendar grid, including leading empty cells
    calendar_grid = [None] * leading_empty_cells + list(range(1, days_in_month + 1))

    # Determine the number of trailing empty cells in the calendar grid
    trailing_empty_cells = (7 - (len(calendar_grid) % 7)) % 7

    # Add trailing empty cells to the calendar grid
    calendar_grid += [None] * trailing_empty_cells

    # Reshape the calendar grid into a 2D list with 7 columns
    calendar_grid_2d = [calendar_grid[i:i+7] for i in range(0, len(calendar_grid), 7)]

    # Create a dictionary with relevant calendar data
    calendar_data = {
        'current_date': now.strftime("%B %Y"),
        'days_in_month': calendar_grid_2d,
        'current_day': now.day,
    }

    return calendar_data


def ordinal(number):
    if 10 <= number % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
    return f"{number}{suffix}"


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
        # Generate calendar data
        calendar_data = generate_calendar_data()
        # User is logged in, render relevant page for the user
        now = datetime.datetime.now()
        formatted_date = f"{ordinal(now.day)} {now.strftime('%B')}"
        current_year = f"{now.strftime('%Y')}"
        return render_template('index.html', user=user, calendar_data=calendar_data, formatted_date=formatted_date, current_year=current_year, username=user.username)
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
            return redirect(url_for('home', username=user.username))
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
        except IntegrityError:
            db.session.rollback()
            flash('Error: This username is already used.')
    return render_template('register.html')


if __name__ == "__main__":
    app.run(debug=True)
