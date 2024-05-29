# EXPENSE TRACKER
#### Video Demo: https://www.youtube.com/watch?v=S2XiAC4jNEw
#### Description: Overview
This application is designed to help users manage their personal finances by tracking expenses, incomes, budgets, and alerts. It is built using the Flask framework, which is a lightweight and versatile web framework for Python. The application integrates several key components including user authentication, database management, weather data retrieval, and scheduled tasks to provide a comprehensive financial management solution.

Application Workflow
User Interaction:

Home Page: If a user is authenticated, the home page displays an overview of their financial data including expenses, incomes, budgets, and alerts. It also shows weather data for a selected city.
Registration/Login: Users can register or log in. If the login is successful, the user is redirected to the home page.
Expense and Income Management:

Add Expense/Income: Users can add new expenses or incomes via forms. The data is stored in the database with the current timestamp.
View Transactions: Users can view all their expenses and incomes. Each transaction includes details like amount, description, and timestamp.
Delete Transactions: Users can delete specific expenses or incomes if necessary.
Budget Management:

Set Budget: Users can set budgets for different categories. Each budget is stored with an associated user ID.
View Budgets: Users can view all their set budgets.
Delete Budget: Users can delete specific budgets.
Alerts:

Check Budgets: A scheduled task runs every hour to check if any user's expenses exceed their set budgets. If an excess is detected, an alert is generated and stored in the database.
View Alerts: Users can view all the alerts generated for them.
Weather Data:

Weather Fetching: The get_weather function uses the OpenWeatherMap API to fetch weather data for a specified city. This data is displayed on the home page.
TODO
