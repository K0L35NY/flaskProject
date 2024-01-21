from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import calendar
import datetime
app = Flask(__name__, static_folder="static")
app.secret_key = "klucz_tajny"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


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

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_name = db.Column(db.String(100), nullable=False)
    goal_days = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('habits', lazy=True))

class HabitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    habit = db.relationship('Habit', backref=db.backref('habit_logs', lazy=True))
    day_index = db.Column(db.Integer, nullable=False)
    log_date = db.Column(db.Date, nullable=False)
    checked = db.Column(db.Boolean, nullable=False)
    progress = db.Column(db.Integer, nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

with app.app_context():
    db.create_all()

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

        # Get habits for the user
        habits = Habit.query.filter_by(user_id=user.id).all()

        # Get habit logs for the current month
        habit_logs = HabitLog.query.filter(
            HabitLog.habit_id.in_([habit.id for habit in habits]),
            db.extract('month', HabitLog.log_date) == datetime.datetime.now().month
        ).all()

        # Create a dictionary to store habit tracking data
        habit_tracking_data = {}
        for habit in habits:
            habit_logs_for_habit = [log for log in habit_logs if log.habit_id == habit.id]
            habit_tracking_data[habit.id] = {
                'habit_name': habit.habit_name,
                'goal_days': habit.goal_days,
                'logs': {log.log_date.day: log.progress for log in habit_logs_for_habit}
            }

        # User is logged in, render relevant page for the user
        now = datetime.datetime.now()
        formatted_date = f"{ordinal(now.day)} {now.strftime('%B')}"
        current_year = f"{now.strftime('%Y')}"
        checkbox_states = get_checkbox_states(user.id)


        # Relevant things
        tasks = Task.query.filter_by(user_id=user.id).all()
        today = datetime.datetime.today().date()
        tasks_today = Task.query.filter_by(user_id=user.id, day=today).all()
        tasks_remaining = Task.query.filter(Task.user_id == user.id, Task.day > today).all()

        return render_template('index.html', user=user, calendar_data=calendar_data,
                               formatted_date=formatted_date, current_year=current_year, username=user.username,
                               habits=habits, habit_tracking_data=habit_tracking_data, checkbox_states=checkbox_states,
                               tasks=tasks, tasks_today=tasks_today, tasks_remaining=tasks_remaining)
    else:
        # Invalid session, redirect to login
        return redirect(url_for('login'))

def get_checkbox_states(user_id):
    checkbox_states = {}
    habit_logs = HabitLog.query.join(Habit).filter(Habit.user_id == user_id).all()

    for log in habit_logs:
        checkbox_states[(log.habit_id, log.day_index)] = log.checked

    return checkbox_states
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

@app.route('/add_habit', methods=['POST'])
def add_habit():
    habit_name = request.form['habit_name']
    goal_days = int(request.form['goal_days'])

    user_id = session['user_id']
    user = User.query.get(user_id)

    new_habit = Habit(habit_name=habit_name, goal_days=goal_days, user=user)
    db.session.add(new_habit)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/update_checkbox_state', methods=['GET'])
def update_checkbox_state():
    habit_id = request.args.get('habit_id', type=int)
    day_index = request.args.get('day_index', type=int)
    checked_str = request.args.get('checked', '').lower()
    checked = str_to_bool(checked_str)

    # Set log_date to the current date and time
    log_date = datetime.datetime.now()

    # Check if a log entry already exists for the habit and day
    habit_log = HabitLog.query.filter_by(habit_id=habit_id, day_index=day_index).first()

    if habit_log:
        # If the log entry exists, update it
        habit_log.checked = checked
        habit_log.log_date = log_date
    else:
        # If the log entry doesn't exist, create a new one
        habit_log = HabitLog(habit_id=habit_id, day_index=day_index, checked=checked, log_date=log_date)

    # Calculate progress based on the number of checkboxes checked and the habit goal
    habit = Habit.query.get(habit_id)
    habit_log.progress = calculate_progress(habit.goal_days, HabitLog.query.filter_by(habit_id=habit_id).count())

    print(f"Habit ID: {habit_id}, Day Index: {day_index}, Checked: {checked}, Progress: {habit_log.progress}")

    # Save the habit_log entry to the database
    db.session.add(habit_log)
    db.session.commit()

    return jsonify({'status': 'success'})

def calculate_progress(goal, checked_count):
    if goal == 0:
        return 0  # Avoid division by zero
    return min(100, (checked_count / goal) * 100)

def str_to_bool(s):
    return s.lower() in ['true', '1', 'yes', 'on']

@app.route('/get_habit_data')
def get_habit_data():
    habit_id = request.args.get('habit_id', type=int)
    habit = Habit.query.get(habit_id)

    if habit:
        progress = calculate_progress(habit.goal_days, HabitLog.query.filter_by(habit_id=habit.id).count())
        return jsonify({'progress': progress})
    else:
        return jsonify({'error': 'Habit not found'}), 404

@app.route('/add_task', methods=['POST'])
def add_task():
    user_id = session['user_id']
    user = User.query.get(user_id)

    task = Task(title=request.form['title'], description=request.form['description'], day=request.form['day'], user=user)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/edit_task/<int:id>', methods=['POST'])
def edit_task(id):
    task = Task.query.get(id)
    task.title = request.form['title']
    task.description = request.form['description']
    task.day = request.form['day']
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete_task/<int:id>')
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete_habit/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    habit = Habit.query.get(habit_id)
    if habit:
        HabitLog.query.filter_by(habit_id=habit.id).delete()
        db.session.delete(habit)
        db.session.commit()
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(port=8000, debug=True)
