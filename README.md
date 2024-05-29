Video Demo: https://www.youtube.com/watch?v=Q-jixveHlsE
your project’s title; Expense Tracker
your name; Ivica
your GitHub and edX usernames; ivicamt, ivicamt
your city and country; Kumanovo, North Macedonia
and, the date you have recorded this video: 5/27/2024

Description: ## Detailed Explanation of How the Budget and Expense Management Application Works

### Overview

This application is designed to help users manage their personal finances by tracking expenses, incomes, budgets, and alerts. It is built using the Flask framework, a lightweight and versatile web framework for Python. The application integrates several key components including user authentication, database management, weather data retrieval, and scheduled tasks to provide a comprehensive financial management solution.

### Core Components

#### Flask Framework

- **Flask**: The core framework that handles routing, request handling, and rendering templates.
- **Flask-Login**: Manages user sessions and authentication.
- **Flask-SQLAlchemy**: Integrates SQLAlchemy for ORM (Object-Relational Mapping), allowing Python classes to interact with the database.
- **Flask-WTF**: Manages form handling and file uploads.

#### Database

- **SQLite**: A lightweight relational database used to store user data, expenses, incomes, budgets, and alerts.
- **Models**: Defined using SQLAlchemy, models represent database tables.

#### User Authentication

- **User Registration**: Users register with a username and password. Passwords are hashed using Werkzeug's `generate_password_hash` before storing them in the database.
- **User Login**: Users log in with their credentials, which are verified by checking the hashed password stored in the database.

### Data Models

1. **User**: Stores user credentials and relationships to other data (expenses, incomes, budgets, alerts).
2. **Expense**: Tracks individual expenses with fields for amount, description, timestamp, and user association.
3. **Income**: Tracks individual incomes with similar fields as expenses.
4. **Budget**: Defines budget categories and their respective amounts for each user.
5. **Alert**: Stores alerts for users when they exceed their budgets.

### APScheduler

- **Background Scheduler**: Runs tasks at regular intervals. In this app, it checks whether the user's expenses have exceeded their budgets and generates alerts if necessary.

### Weather API

- **OpenWeatherMap API**: Fetches current weather data for a specified city. This is integrated into the home page for user convenience.

### Application Workflow

#### User Interaction

- **Home Page**: If a user is authenticated, the home page displays an overview of their financial data including expenses, incomes, budgets, and alerts. It also shows weather data for a selected city.
- **Registration/Login**: Users can register or log in. If the login is successful, the user is redirected to the home page.

#### Expense and Income Management

- **Add Expense/Income**: Users can add new expenses or incomes via forms. The data is stored in the database with the current timestamp.
- **View Transactions**: Users can view all their expenses and incomes. Each transaction includes details like amount, description, and timestamp.
- **Delete Transactions**: Users can delete specific expenses or incomes if necessary.

#### Budget Management

- **Set Budget**: Users can set budgets for different categories. Each budget is stored with an associated user ID.
- **View Budgets**: Users can view all their set budgets.
- **Delete Budget**: Users can delete specific budgets.

#### Alerts

- **Check Budgets**: A scheduled task runs every hour to check if any user's expenses exceed their set budgets. If an excess is detected, an alert is generated and stored in the database.
- **View Alerts**: Users can view all the alerts generated for them.

#### Weather Data

- **Weather Fetching**: The `get_weather` function uses the OpenWeatherMap API to fetch weather data for a specified city. This data is displayed on the home page.

### Detailed Code Explanation

#### Database Models

```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True)
    incomes = db.relationship('Income', backref='user', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
```

- **User Model**: Stores user credentials and has relationships to expenses and incomes.
- **Expense Model**: Represents an expense with amount, description, user association, and timestamp.

#### User Authentication

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST']:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')
```

- **Registration Route**: Handles user registration, password hashing, and storing user data in the database.
- **Login Route**: Handles user login by verifying hashed passwords and starting user sessions.

#### Budget Check Task

```python
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
```

- **Budget Checking**: Periodically checks each user's expenses against their budgets. If a budget is exceeded, an alert is generated and stored.

### Execution

To run the application, follow these steps:

1. **Set Up Environment**: Ensure you have Python and the necessary libraries installed.
2. **Initialize Database**: Run the `create_tables()` function to set up the database.
3. **Start the Server**: Execute `python app.py` to start the Flask server.
4. **Access the Application**: Open a web browser and navigate to `http://127.0.0.1:5000/`.

This application provides a robust framework for personal financial management with a clear pathway for future enhancements. By integrating responsive design, advanced SQL techniques, and machine learning, it can evolve into a powerful tool for managing personal finances effectively.
TODO
