import io
import random
from enum import Enum

from flask import Flask, request, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class DifficultyLevel(Enum):
    EASY = 'Easy'
    MEDIUM = 'Medium'
    HARD = 'Hard'


class HealthLevel(Enum):
    UNHEALTHY = 'Unhealthy'
    MEDIUM = 'Medium'
    HEALTHY = 'Healthy'


class Meal(db.Model):
    """
    Database model/entity for representing meal information.
    """
    id = db.Column(db.Integer, primary_key=True)
    tutorial = db.Column(db.Text, nullable=False)
    kcal = db.Column(db.Float, nullable=False)
    difficulty_level = db.Column(db.Enum(DifficultyLevel), nullable=False)
    health_level = db.Column(db.Enum(HealthLevel), nullable=False)


def get_meal_by_filter_criteria(min_kcal, max_kcal, difficulty_level, health_level):
    """
        Retrieves a meal based on filter criteria.

        Args:
            min_kcal (float): Minimum kcal value.
            max_kcal (float): Maximum kcal value.
            difficulty_level (DifficultyLevel): Difficulty level of the meal.
            health_level (HealthLevel): Health level of the meal.

        Returns:
            Meal: A random meal that matches the criteria, or None if no suitable meal is found.
    """
    meals = Meal.query.filter(
        Meal.kcal.between(min_kcal, max_kcal),
        Meal.difficulty_level == difficulty_level,
        Meal.health_level == health_level
    ).all()

    if meals:
        return random.choice(meals)
    else:
        return None


def generate_pdf(meal):
    """
        Generates a PDF document for the given meal.

        Args:
            meal (Meal): The meal for which the PDF is generated.

        Returns:
            bytes: The generated PDF content.
    """
    buffer = io.BytesIO()

    # Create a PDF document
    pdf = canvas.Canvas(buffer)

    # Write content to the PDF
    pdf.drawString(100, 750, f"Suitable Meal: {meal.tutorial}")
    pdf.drawString(100, 730, f"Kcal: {meal.kcal}")
    pdf.drawString(100, 710, f"Difficulty: {meal.difficulty_level}")
    pdf.drawString(100, 690, f"Health: {meal.health_level}")

    # Save the PDF to the buffer
    pdf.showPage()
    pdf.save()

    # Move the buffer cursor to the beginning
    buffer.seek(0)
    return buffer.read()


@app.route('/bmi/calculate/', methods=['GET', 'POST'])
def calculate_bmi():
    """
        Calculates BMI based on user input.

        Returns:
            str: Rendered HTML template with the BMI result.
    """
    if request.method == 'POST':
        weight = float(request.form['weight'])
        height = float(request.form['height'])

        bmi = weight / (height / 100 ** 2)

        return render_template('result_bmi.html', bmi=bmi)

    return render_template('calculate_bmi.html')


@app.route('/get_suitable_meal/', methods=['GET', 'POST'])
def get_suitable_meal():
    """
        Retrieves a suitable meal based on user input criteria.

        Returns:
            Either a rendered HTML template or a PDF response.
    """
    if request.method == 'POST':
        min_kcal = float(request.form['min_kcal'])
        max_kcal = float(request.form['max_kcal'])
        difficulty_level = request.form['difficulty_level']
        health_level = request.form['health_level']

        meal = get_meal_by_filter_criteria(min_kcal, max_kcal, difficulty_level, health_level)

        if meal:
            response = make_response(generate_pdf(meal))
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=suitable_meal.pdf'
            return response
        else:
            return "No suitable meal found."

    return render_template('input_criteria.html')


@app.route('/populate_db')
def populate_db():
    """
    Populates the database with 1 meal record.

    Returns:
        str: Confirmation message.
    """
    # todo zapelnij baze mati

    tutorial_data = "sth"
    kcal_data = 3000
    difficulty_level_data = DifficultyLevel.MEDIUM
    health_level_data = HealthLevel.MEDIUM

    new_meal = Meal(
        tutorial=tutorial_data,
        kcal=kcal_data,
        difficulty_level=difficulty_level_data,
        health_level=health_level_data
    )

    db.session.add(new_meal)
    db.session.commit()

    return "Record created successfully!"


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
