import io
import random
from enum import Enum

from flask import Flask, request, make_response, render_template, url_for
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


class MealType(Enum):
    BREAKFAST = 'Breakfast'
    DINNER = 'Dinner'
    SUPPER = 'Supper'


class Meal(db.Model):
    """
    Database model/entity for representing meal information.
    """
    id = db.Column(db.Integer, primary_key=True)
    tutorial = db.Column(db.Text, nullable=False)
    kcal = db.Column(db.Float, nullable=False)
    difficulty_level = db.Column(db.Enum(DifficultyLevel), nullable=False)
    health_level = db.Column(db.Enum(HealthLevel), nullable=False)
    meal_type = db.Column(db.Enum(MealType), nullable=False)



def get_meal_by_filter_criteria(min_kcal, max_kcal, difficulty_level, health_level, meal_type):
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
        Meal.health_level == health_level,
        Meal.meal_type == meal_type
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
    # pdf.drawString(100, 670, f"Health: {meal.meal_type}")

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
        meal_type = request.form['meal_type']

        meal = get_meal_by_filter_criteria(min_kcal, max_kcal, difficulty_level, health_level, meal_type)

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

    tutorial_data = "sdasath"
    kcal_data = 3111
    difficulty_level_data = DifficultyLevel.EASY
    health_level_data = HealthLevel.MEDIUM
    meal_type_test = MealType.SUPPER

    new_meal = Meal(
        tutorial=tutorial_data,
        kcal=kcal_data,
        difficulty_level=difficulty_level_data,
        health_level=health_level_data,
        meal_type=meal_type_test
    )

    #Meal Type - Supper

    ThaiShrimpSoup = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/easy-thai-shrimp-soup,906963/',
        kcal=466,
        difficulty_level=DifficultyLevel.MEDIUM,
        health_level=HealthLevel.HEALTHY,
        meal_type=MealType.SUPPER
    )

    SalmonSalad = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/salmon-salad,949284/',
        kcal=568,
        difficulty_level=DifficultyLevel.EASY,
        health_level=HealthLevel.HEALTHY,
        meal_type=MealType.SUPPER
    )

    AppleSliceSandwich = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/apple-slice-sandwich,921836/',
        kcal=442,
        difficulty_level=DifficultyLevel.EASY,
        health_level=HealthLevel.MEDIUM,
        meal_type=MealType.SUPPER
    )

    ClassicBLT = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/classic-blt,905829//',
        kcal=914,
        difficulty_level=DifficultyLevel.EASY,
        health_level=HealthLevel.MEDIUM,
        meal_type=MealType.SUPPER
    )




    #Meal Type - Breakfast

    CranberryBananaOatmeal = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/cranberry-banana-oatmeal,906966/',
        kcal=355,
        difficulty_level=DifficultyLevel.EASY,
        health_level=HealthLevel.HEALTHY,
        meal_type=MealType.BREAKFAST
    )

    AlmondButterSmoothie = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/almond-butter-smoothie,939598/',
        kcal=460,
        difficulty_level=DifficultyLevel.MEDIUM,
        health_level=HealthLevel.HEALTHY,
        meal_type=MealType.BREAKFAST
    )

    BaconAndCheddarGrilledCheese = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/bacon-and-cheddar-grilled-cheese,927340/',
        kcal=411,
        difficulty_level=DifficultyLevel.EASY,
        health_level=HealthLevel.UNHEALTHY,
        meal_type=MealType.BREAKFAST
    )

    PestoPastaWithGrilledChicken = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/pesto-pasta-with-grilled-chicken,3218180/',
        kcal=852,
        difficulty_level=DifficultyLevel.MEDIUM,
        health_level=HealthLevel.MEDIUM,
        meal_type=MealType.BREAKFAST
    )


    #Meal Type - Dinner

    GarlicMacNCheese = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/garlic-mac-n-cheese,925249/',
        kcal=587,
        difficulty_level=DifficultyLevel.MEDIUM,
        health_level=HealthLevel.UNHEALTHY,
        meal_type=MealType.DINNER
    )

    WhiteSphagetti = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/white-spaghetti,920498/',
        kcal=587,
        difficulty_level=DifficultyLevel.MEDIUM,
        health_level=HealthLevel.MEDIUM,
        meal_type=MealType.DINNER
    )

    BakedParmesanChickenNuggets = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/baked-parmesan-chicken-nuggets,3222233/',
        kcal=1732,
        difficulty_level=DifficultyLevel.MEDIUM,
        health_level=HealthLevel.MEDIUM,
        meal_type=MealType.DINNER
    )

    MediTerraneanQuinoaSalad = Meal(
        tutorial='https://www.eatthismuch.com/recipe/nutrition/mediterranean-quinoa-salad,34389/',
        kcal=532,
        difficulty_level=DifficultyLevel.MEDIUM,
        health_level=HealthLevel.HEALTHY,
        meal_type=MealType.DINNER
    )

    db.session.add(ThaiShrimpSoup)
    db.session.add(CranberryBananaOatmeal)
    db.session.add(WhiteSphagetti)
    db.session.add(ClassicBLT)
    db.session.add(SalmonSalad)
    db.session.add(AppleSliceSandwich)
    db.session.add(BakedParmesanChickenNuggets)
    db.session.add(PestoPastaWithGrilledChicken)
    db.session.add(GarlicMacNCheese)
    db.session.add(AlmondButterSmoothie)
    db.session.add(BaconAndCheddarGrilledCheese)
    db.session.add(MediTerraneanQuinoaSalad)
    db.session.commit()

    return "Record created successfully!"

# populate_db()

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
