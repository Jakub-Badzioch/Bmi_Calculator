# Meal Planner / Bmi Calculator Web App

This is a simple web application built with Flask that helps users calculate their BMI and find a suitable meal/menu
based on specified criteria. The application uses SQLite for database storage.

## Features

1. **BMI Calculator:**
   - Users can input their weight and height to calculate their Body Mass Index (BMI).
   - Results are displayed on an HTML page.

2. **Meal Finder:**
   - Users can input criteria for maximum kcal to find a suitable meal.
   - If a meal is found, it is generated with meal details (Instructions, kcal, meal type) and presented to the user.

3. **Database Population:**
   - An endpoint `/populate_db` populates the SQLite database with a sample meal records for testing purposes.

## Project Structure

- **`app.py`:** Main file containing the Flask application, database models, and routes.
- **`templates/`:** HTML templates for rendering pages.
- **`static/`:** JS and CSS files

## Usage

1. Access the application in your browser at `http://127.0.0.1:5000/`.

2. Calculate BMI:
   - Enter your weight and height.
   - View the calculated BMI on the result page.

3. Find Suitable Meal:
   - Navigate to `/meal`.
   - Enter criteria such as max kcal.
   - Receive a report with details of suitable meals or a message indicating no suitable meal was found.

4. Populate Database:
   - Visit `/populate_db` to add a sample meal records to the database.
