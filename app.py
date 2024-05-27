from flask import Flask, render_template, request, redirect, url_for, session, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from datetime import datetime
from flask_login import current_user
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

#API
def get_weather(city):
    api_key = '0097838102276931d1338798d4f3ed5a'  # Replace with your actual API key
    base_url = 'http://api.openweathermap.org/data/2.5/weather?'
    complete_url = base_url + 'appid=' + api_key + '&q=' + city
    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()
        if 'weather' in data and 'main' in data:
            return data
        else:
            print('Invalid weather data received')
            return None
    except requests.RequestException as e:
        print(f'Error fetching weather data: {e}')
        return None


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True)
    incomes = db.relationship('Income', backref='user', lazy=True)

# Define Expense model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def formatted_timestamp(self):
        return self.timestamp.strftime('%Y-%m-%d %H:%M')

    def __repr__(self):
        return f"Expense(amount={self.amount}, description={self.description}, user_id={self.user_id}, timestamp={self.formatted_timestamp()})"

# Define Income model
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def formatted_timestamp(self):
        return self.timestamp.strftime('%Y-%m-%d %H:%M')

    def __repr__(self):
        return f"Income(amount={self.amount}, description={self.description}, user_id={self.user_id}, timestamp={self.formatted_timestamp()})"

# Create tables function
def create_tables():
    with app.app_context():
        db.create_all()

#budget
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Budget(category={self.category}, amount={self.amount}, user_id={self.user_id})"


#alert
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Create tables
create_tables()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    selected_city = request.args.get('city', 'London')  # Default city is London if not specified
    weather_data = get_weather(selected_city)
    current_date = datetime.now().strftime('%Y-%m-%d')
    thirty_days_ago = datetime.now() - timedelta(days=30)

    if current_user.is_authenticated:
        expenses = Expense.query.filter(Expense.user_id == current_user.id, Expense.timestamp >= thirty_days_ago).all()
        incomes = Income.query.filter(Income.user_id == current_user.id, Income.timestamp >= thirty_days_ago).all()
        total_expenses = sum(expense.amount for expense in expenses)
        total_incomes = sum(income.amount for income in incomes)
        balance = total_incomes - total_expenses

        budgets = Budget.query.filter_by(user_id=current_user.id).all()
        alerts = Alert.query.filter_by(user_id=current_user.id).all()

        expense_data = [{'amount': expense.amount, 'description': expense.description, 'timestamp': expense.timestamp} for expense in expenses]
        income_data = [{'amount': income.amount, 'description': income.description, 'timestamp': income.timestamp} for income in incomes]

        return render_template('home.html', expenses=expenses, incomes=incomes, total_expenses=total_expenses, total_incomes=total_incomes, balance=balance, weather=weather_data, date=current_date, budgets=budgets, alerts=alerts, selected_city=selected_city, expense_data=expense_data, income_data=income_data)
    else:
        return redirect(url_for('welcome'))




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return 'Username already exists!'
        # Hash the password
        hashed_password = generate_password_hash(password)
        # Create new user
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


#add expenses
@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            description = request.form['description']
            new_expense = Expense(amount=amount, description=description, user_id=current_user.id)
            db.session.add(new_expense)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Error adding expense: {e}")
            return render_template('error.html', message="An error occurred while adding the expense.")
    return render_template('add_expense.html')


#add income
@app.route('/add_income', methods=['GET', 'POST'])
@login_required
def add_income():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            description = request.form['description']
            new_income = Income(amount=amount, description=description, user_id=current_user.id)
            db.session.add(new_income)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Error adding income: {e}")
            return render_template('error.html', message="An error occurred while adding the income.")
    return render_template('add_income.html')

@app.route('/view_transactions')
@login_required
def view_transactions():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    incomes = Income.query.filter_by(user_id=current_user.id).all()
    return render_template('view_transactions.html', expenses=expenses, incomes=incomes)

@app.route('/view_by_month', methods=['GET', 'POST'])
@login_required
def view_by_month():
    if request.method == 'POST':
        month = int(request.form['month'])
        year = int(request.form['year'])
        expenses = Expense.query.filter(db.extract('month', Expense.timestamp) == month,
                                        db.extract('year', Expense.timestamp) == year,
                                        Expense.user_id == current_user.id).all()
        incomes = Income.query.filter(db.extract('month', Income.timestamp) == month,
                                      db.extract('year', Income.timestamp) == year,
                                      Income.user_id == current_user.id).all()
        total_expenses = sum(expense.amount for expense in expenses)
        total_incomes = sum(income.amount for income in incomes)
        return render_template('view_by_month.html', expenses=expenses, incomes=incomes, total_expenses=total_expenses, total_incomes=total_incomes, month=month, year=year)
    return render_template('select_month.html')


@app.route('/set_budget', methods=['GET', 'POST'])
@login_required
def set_budget():
    if request.method == 'POST':
        try:
            category = request.form['category']
            amount = float(request.form['amount'])
            new_budget = Budget(category=category, amount=amount, user_id=current_user.id)
            db.session.add(new_budget)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Error setting budget: {e}")
            return render_template('error.html', message="An error occurred while setting the budget.")
    return render_template('set_budget.html')

@app.route('/view_budgets')
@login_required
def view_budgets():
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    return render_template('view_budgets.html', budgets=budgets)



def check_budget():
    with app.app_context():
        users = User.query.all()
        for user in users:
            budgets = Budget.query.filter_by(user_id=user.id).all()
            for budget in budgets:
                total_expenses = db.session.query(db.func.sum(Expense.amount)).filter_by(user_id=user.id, category=budget.category).scalar() or 0
                if total_expenses > budget.amount:
                    new_alert = Alert(message=f"Budget exceeded for {budget.category}", user_id=user.id)
                    db.session.add(new_alert)
                    db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_budget, trigger="interval", minutes=60)
scheduler.start()

@app.route('/view_alerts')
@login_required
def view_alerts():
    alerts = Alert.query.filter_by(user_id=current_user.id).all()
    return render_template('view_alerts.html', alerts=alerts)


#delete BUDGET input
@app.route('/delete_budget/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    try:
        budget = Budget.query.get(budget_id)
        if budget and budget.user_id == current_user.id:
            db.session.delete(budget)
            db.session.commit()
            return redirect(url_for('view_budgets'))
        else:
            return render_template('error.html', message="Budget not found or not authorized.")
    except Exception as e:
        print(f"Error deleting budget: {e}")
        return render_template('error.html', message="An error occurred while deleting the budget.")



# Route to delete an expense
@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if expense and expense.user_id == current_user.id:
        db.session.delete(expense)
        db.session.commit()
    return redirect(url_for('view_transactions'))


# Route to delete an income
@app.route('/delete_income/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    income = Income.query.get(income_id)
    if income and income.user_id == current_user.id:
        db.session.delete(income)
        db.session.commit()
    return redirect(url_for('view_transactions'))


#Visual representation

@app.route('/visualize')
@login_required
def visualize():
    thirty_days_ago = datetime.now() - timedelta(days=30)

    expenses = Expense.query.filter(Expense.user_id == current_user.id, Expense.timestamp >= thirty_days_ago).all()
    incomes = Income.query.filter(Income.user_id == current_user.id, Income.timestamp >= thirty_days_ago).all()

    expense_data = [{'amount': expense.amount, 'description': expense.description} for expense in expenses]
    income_data = [{'amount': income.amount, 'description': income.description} for income in incomes]

    return render_template('visualize.html', expenses=expense_data, incomes=income_data)



@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('welcome.html')


if __name__ == '__main__':
    app.run(debug=True)
