import io
import random

from flask import Flask, request, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from enum import Enum

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
    id = db.Column(db.Integer, primary_key=True)
    tutorial = db.Column(db.Text, nullable=False)
    kcal = db.Column(db.Float, nullable=False)
    difficulty_level = db.Column(db.Enum(DifficultyLevel), nullable=False)
    health_level = db.Column(db.Enum(HealthLevel), nullable=False)


class MealRepository:
    @staticmethod
    def create_meal(tutorial, kcal, difficulty_level, health_level):
        meal = Meal(tutorial=tutorial, kcal=kcal, difficulty_level=difficulty_level, health_level=health_level)
        db.session.add(meal)
        db.session.commit()
        return meal

    @staticmethod
    def get_meals():
        return Meal.query.all()

    @staticmethod
    def get_meal_by_id(meal_id):
        return Meal.query.get(meal_id)

    @staticmethod
    def update_meal(meal_id, tutorial, kcal, difficulty_level, health_level):
        meal = Meal.query.get(meal_id)
        if meal:
            meal.tutorial = tutorial
            meal.kcal = kcal
            meal.difficulty_level = difficulty_level
            meal.health_level = health_level
            db.session.commit()
            return meal
        return None

    @staticmethod
    def delete_meal(meal_id):
        meal = Meal.query.get(meal_id)
        if meal:
            db.session.delete(meal)
            db.session.commit()
            return meal
        return None


class MealService:
    @staticmethod
    def get_suitable_meal_range(min_kcal, max_kcal, difficulty_level, health_level):
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


class BmiService:
    @staticmethod
    def calculate_bmi(weight, height):
        height_in_meters = height / 100
        bmi = weight / (height_in_meters ** 2)
        return bmi


class BmiController:
    @staticmethod
    @app.route('/bmi/calculate/', methods=['GET', 'POST'])
    def calculate_bmi():
        if request.method == 'POST':
            weight = float(request.form['weight'])
            height = float(request.form['height'])

            bmi = BmiService.calculate_bmi(weight, height)

            return render_template('result_bmi.html', bmi=bmi)

        return render_template('calculate_bmi.html')


class MealController:
    @staticmethod
    @app.route('/get_suitable_meal/', methods=['GET', 'POST'])
    def get_suitable_meal():
        if request.method == 'POST':
            min_kcal = float(request.form['min_kcal'])
            max_kcal = float(request.form['max_kcal'])
            difficulty_level = request.form['difficulty_level']
            health_level = request.form['health_level']

            meal = MealService.get_suitable_meal_range(min_kcal, max_kcal, difficulty_level, health_level)

            if meal:
                response = make_response(generate_pdf(meal))
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = 'inline; filename=suitable_meal.pdf'
                return response
            else:
                return "No suitable meal found."

        return render_template('input_criteria.html')

    @app.route('/populate_db')
    def populate_db(self):
        with app.app_context():
            new_meal = Meal(
                tutorial='Chicken Alfredo',
                kcal=800.0,
                difficulty_level=DifficultyLevel.MEDIUM,
                health_level=HealthLevel.MEDIUM
            )
            db.session.add(new_meal)
            db.session.commit()

        return "Record created successfully!"


# Create tables before running the app
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
