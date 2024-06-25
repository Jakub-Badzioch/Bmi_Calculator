from enum import Enum
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import math
import random

#Test pull requests

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class MealType(Enum):
    BREAKFAST = 'BREAKFAST'
    DINNER = 'DINNER'
    SUPPER = 'SUPPER'

@app.route("/", methods=['POST', 'GET'])
def index():
    clear_user_data()  # Clear the table before rendering the index.html page for the current user
    if request.method == 'POST':

#         print(request.form)
        gender = request.form['gender']
        age = request.form['age']
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        activity = request.form['activity']
        bfat = float(request.form['bodyfat']) if request.form['bodyfat'] else None

        # Creating a new record to the user_data table in the site.db
        new_row = User_data(
            gender=gender,
            age=age,
            weight=weight,
            height=height,
            activity=activity,
            bfat=bfat
        )

        try:
            db.session.add(new_row)
            db.session.commit()
            return redirect(url_for('result_bmi'))

        except Exception as e:
            print(f"Error: {e}")
            return 'There was an issue with calculating.'
    else:

        return render_template('index.html')

@app.route('/result_bmi')
def result_bmi():
    try:
        # fetching data from the db about the current user
        user_data = User_data.query.order_by(User_data.id.desc()).first()
#         print("Retrieved User Data:", user_data)
    except Exception as e:
        print("Error fetching data:", e)

    return render_template(
            'result_bmi.html',
            user_data=user_data,
            calculate_bmi=calculate_bmi,
            classify_bmi=classify_bmi,
            get_gender_label=get_gender_label,
            get_activity_label=get_activity_label,
            calculate_calories=calculate_calories,
            calculate_calories_bfat=calculate_calories_bfat
        )

@app.route("/meals", methods=['GET', 'POST'])
def meals_route():
    selected_meals = None

    if request.method == 'POST':
        max_kcal = float(request.form['max_kcal'])
        selected_meals = get_meals_by_criteria(max_kcal)
        return render_template(
                'meals.html',
                selected_meals = selected_meals,
            )

    return render_template('meals.html')


def clear_user_data():
# Delete all records from the User_data table
    with app.app_context():
        db.session.query(User_data).delete()
        db.session.commit()

def get_gender_label(gender):
    # Define a mapping between integer values and labels for gender
    gender_mapping = {1: 'Male', 2: 'Female'}
    return gender_mapping.get(gender, 'Unknown')

def get_activity_label(activity):
    # Define a mapping between integer values and labels for activity
    activity_mapping = {
        1.2: 'Sedentary',
        1.375: 'Light Exercise',
        1.55: 'Moderate Exercise',
        1.725: 'Heavy Exercise',
        1.9: 'Athlete'
    }
    return activity_mapping.get(activity, 'Unknown')

def calculate_bmi(weight, height):
    bmi_result = (weight/pow(height, 2))*10000
    bmi_result = round(bmi_result, 1)
    return bmi_result

def classify_bmi(bmi_result):
        # define a mapping between bmi_result and labels for it
        bmi_mapping = {
            bmi_result <= 18.5: 'Underweight',
            18.5 < bmi_result <= 24.99: 'Normal Weight',
            24.99 < bmi_result <= 29.99: 'Overweight',
            bmi_result >= 30: 'Obese'
        }
        return bmi_mapping.get(True, 'Unknown')

def calculate_calories(weight, height, age, gender, activity):
    # calculate calories when body fat isn't included
    n = 0
    if gender == 1:
        n = 5
    elif gender == 2:
        n = (-161)
    BMR = 10*weight+6.25*height-5*age+n
    calories = BMR * activity
    return calories

def calculate_calories_bfat(weight, bfat, activity):
    # calculate calories when body fat is included
    BMR = 370+21.6*(1-(bfat/100))*weight
    calories = BMR * activity
    calories = round(calories, 0)
    calories = int(calories)
    return calories

def get_meals_by_criteria(max_kcal):
    selected_meals = {}

    for meal_type in MealType:
        meal = get_meal_by_criteria(max_kcal, meal_type.value)
#         print(f"Meal Type: {meal_type.value}, Meal: {meal}") # Debug print
        selected_meals[meal_type.value] = meal
#     print(f"Selected Meals: {selected_meals}") # Debug print
    return selected_meals

def get_meal_by_criteria(max_kcal, meal_type):
    '''
    Retrieves a meal based on filter criteria.
    returns: A random meal matching the criteria or None if no suitable meal is found.
    '''
    meals = Meals.query.filter(
            Meals.kcal <= max_kcal/3,
            Meals.meal_type == meal_type
        ).all()

#     print(f"Meals for {meal_type}: {meals}") # Debug print
    if meals:
        selected_meal = random.choice(meals)
#         print(f"2 Selected Meal for {meal_type}: {selected_meal}") # Debug print
        return selected_meal
    else:
#         print(f"2 No suitable meal found for {meal_type}") # Debug print
        return None


meals_details = [["Scrambled Eggs", "https://www.bbcgoodfood.com/recipes/perfect-scrambled-eggs-recipe", 405, MealType.BREAKFAST],
                 ["Avocado Toast", "https://cookieandkate.com/avocado-toast-recipe/", 330, MealType.BREAKFAST],
                 ["English Breakfast", 'https://iamafoodblog.com/a-breakdown-of-the-full-english-breakfast/', 780, MealType.BREAKFAST],
                 ["Fried Chicken", "https://cooking.nytimes.com/guides/25-how-to-make-fried-chicken", 600, MealType.DINNER],
                 ["Sphagetti Bolognese", "https://www.bbcgoodfood.com/recipes/best-spaghetti-bolognese-recipe", 550, MealType.DINNER],
                 ["Sushi", "https://www.justonecookbook.com/ultimate-sushi-guide/", 400, MealType.DINNER],
                 ["Curry", "https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjqjMj3n4eEAxUpVPEDHYD1CDMQFnoECBgQAQ&url=https%3A%2F%2Fcurryculture.co.uk%2Ftypes-of-curry%2F&usg=AOvVaw0H8_y_U8V5lvOUE3uTnUa5&opi=89978449", 630, MealType.DINNER],
                 ["Salmon salad", "https://www.wyseguide.com/roasted-vegetable-salmon-salad/", 340, MealType.SUPPER],
                 ["Cereal", "https://www.allrecipes.com/recipe/44162/homemade-cereal/", 440, MealType.SUPPER],
                 ["Prawn Soup", "https://en.wikipedia.org/wiki/Prawn_soup", 470, MealType.SUPPER]
                 ]



def create_meal_records():
    with app.app_context():
        # Clear existing meal records
        db.session.query(Meals).delete()

        # Add 50 random meal records
        for _ in range(len(meals_details)):
            name = meals_details[_][0]
            instructions = meals_details[_][1]
            kcal = meals_details[_][2]
            meal_type = meals_details[_][3]
            new_meal = Meals(
                        name=name,
                        instructions=instructions,
                        kcal=kcal,
                        meal_type=meal_type
                        )
            db.session.add(new_meal)
            db.session.commit()

class User_data(db.Model):
    '''
    Database model/entity for representing current user's information.
    Redundant and could be user differently but doesn't hurt anybody by doing it this way
    '''
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    activity = db.Column(db.Float)
    bfat = db.Column(db.Float, nullable=True)

class Meals(db.Model):
    '''
    Database model/entity for representing meal information.
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    kcal = db.Column(db.Float, nullable=False)
    meal_type = db.Column(db.Enum(MealType), nullable=False)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    create_meal_records()

    app.run(debug=True, host='localhost', port=9874)
