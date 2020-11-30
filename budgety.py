from jinja2 import StrictUndefined
from datetime import datetime, timedelta
import requests
from flask import Flask, request, render_template, session, url_for, flash, redirect, jsonify, json, abort
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.sql import and_
import os
import hashlib
import hmac
import base64
from password_verification import hash_pw, check_pw

##########################################
# APP SETUP
##########################################

app                     = Flask(__name__)
app.jinja_env.undefined = StrictUndefined
app                     = Flask(__name__, instance_relative_config=True)
app.secret_key          = os.getenv('SECRET_KEY', '9a9fa6aec622fdcaddc3a53c3311da7a5a3d30d5efc6c7a7')

db     = SQLAlchemy(app)
db.app = app

database = 'sqlite:////tmp/budget-tracking.db'
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.app = app
db.init_app(app)

##########################################
# AUTHENTICATION
##########################################

@app.route('/sign-up', methods=["POST"])
def sign_up():
    """ Sign up form consumption """
    from models import User

    name     = request.form.get("name")
    email    = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    # User doesn't exist so create an account.
    if user is None:
        new_user          = User()
        new_user.name     = name
        new_user.email    = email
        new_user.password = hash_pw(password)
        db.session.add(new_user)
        db.session.commit()
        flash('You have successfully signed up.')
        return redirect(url_for('index'))
    else:
        flash('Email already in use.')
        return redirect(url_for("index"))

@app.route('/login-form', methods=["POST"])
def login_form():
    """ Login form """

    from models import User

    email    = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()
    password_login_query = User.query.filter_by(password=password).first()

    #if email_login_query is None or password_login_query is None:
    if user is None:
        flash('Wrong email.')
        return redirect(url_for("index"))
    else:
        if check_pw(user.password, password):
            session['id'] = user.id
            return redirect(url_for('dashboard', id=session['id']))
        else:
            flash('Wrong password.')
            return redirect(url_for("index"))

@app.route('/logout', methods=["GET"])
def logout():
    """ Logs the user out """
    session.pop('id', None)
    return redirect(url_for('index'))

###############################
# HOMEPAGE AND DASHBOARD
###############################

@app.route('/')
def index():
    """ Homepage """
    APP_ID = os.getenv('APP_ID')    
    return render_template("homepage.html", user_session_info=session, app_id=APP_ID)

@app.route('/profile-edit', methods=["POST"])
def profile_edit():
    from models import User
    """ Edit profile information """
    id        = session.get('id')
    user_info = User.query.filter_by(id=id).first()
    name      = request.form.get("profile-name")
    email     = request.form.get("profile-email")
    password  = request.form.get("new-password")
    if name:
        user_info.name = name
        db.session.commit()
    if password:
        user_info.password = password
        db.session.commit()
    if email:
        user_info.email = email
        db.session.commit()

    # Return jsonified budget info to submit-new-account-info.js
    name_info = { 'name': name, 'email': email }
    return jsonify(name_info)

@app.route('/dashboard/<int:id>')
def dashboard(id):
    """ This is the user dashboard """
    from models import User, Expenditure, Budget
    from utils import expenditure_total_amount_and_avg, budget_totals, get_dates_for_budget, get_progress, get_budget_per_category, connect_to_db 

    logged_in = 'id' in session
    if logged_in:
        user   = User.query.filter_by(id=id).first()
        ### GENERATE THE USER HASH ###
        APP_ID = os.getenv('APP_ID')
        KEY = os.getenv('SECURE_MODE_KEY')
        KEY = b'e179017a-62b0-4996-8a38-e91aa9f1'
        MESSAGE = str(user.id)
        hash_result = hmac.new(KEY, MESSAGE.encode('utf-8'), hashlib.sha256).hexdigest() 

        ####### GET THE USER'S BUDGETS FOR EACH CATEGORY
        cat_1_budget = get_budget_per_category(1, id)
        cat_2_budget = get_budget_per_category(2, id)
        cat_3_budget = get_budget_per_category(3, id)
        cat_4_budget = get_budget_per_category(4, id)
        cat_5_budget = get_budget_per_category(5, id)

        # Get all expenditures for logged-in user.
        expenditures = Expenditure.query.filter_by(expenditure_userid=id).all()


        # Get the dates for each budget.
        cat_1_start, cat_1_end = get_dates_for_budget(1, id)
        cat_2_start, cat_2_end = get_dates_for_budget(2, id)
        cat_3_start, cat_3_end = get_dates_for_budget(3, id)
        cat_4_start, cat_4_end = get_dates_for_budget(4, id)
        cat_5_start, cat_5_end = get_dates_for_budget(5, id)

        # format datetime objects into "YYYY-MM-DD".
        cat_1_start_date = cat_1_start.strftime('%Y-%m-%d')
        cat_2_start_date = cat_2_start.strftime('%Y-%m-%d')
        cat_3_start_date = cat_3_start.strftime('%Y-%m-%d')
        cat_4_start_date = cat_4_start.strftime('%Y-%m-%d')
        cat_5_start_date = cat_5_start.strftime('%Y-%m-%d')

        cat_1_end_date = cat_1_end.strftime('%Y-%m-%d')
        cat_2_end_date = cat_2_end.strftime('%Y-%m-%d')
        cat_3_end_date = cat_3_end.strftime('%Y-%m-%d')
        cat_4_end_date = cat_4_end.strftime('%Y-%m-%d')
        cat_5_end_date = cat_5_end.strftime('%Y-%m-%d')

        ########### TOTAL PRICE AND AVERAGE SPENT ###########

        # Unpacking the total price and average spent
        total_online_purchase_price, avg_online_expenditures      = expenditure_total_amount_and_avg(1, id, cat_1_start_date, cat_1_end_date)
        total_travel_price, avg_travel_expenditures               = expenditure_total_amount_and_avg(2, id, cat_2_start_date, cat_2_end_date)
        total_food_price, avg_food_expenditures                   = expenditure_total_amount_and_avg(3, id, cat_3_start_date, cat_3_end_date)
        total_clothing_price, avg_clothing_expenditures           = expenditure_total_amount_and_avg(4, id, cat_4_start_date, cat_4_end_date)
        total_entertainment_price, avg_entertainment_expenditures = expenditure_total_amount_and_avg(5, id, cat_5_start_date, cat_5_end_date)

        total_price = (
            total_food_price + total_clothing_price +
            total_entertainment_price + total_travel_price +
            total_online_purchase_price
        )

        ########### BUDGET ###########

        # Get diff of (budget's total - amount spent).
        online_budget_minus_expenses        = budget_totals(1, id, total_online_purchase_price)
        travel_budget_minus_expenses        = budget_totals(2, id, total_travel_price)
        food_budget_minus_expenses          = budget_totals(3, id, total_food_price)
        clothing_budget_minus_expenses      = budget_totals(4, id, total_clothing_price)
        entertainment_budget_minus_expenses = budget_totals(5, id, total_entertainment_price)

        ############# PROGRESS BAR ##############

        # Calculate the progress bar totals
        online_progress        = get_progress(online_budget_minus_expenses, cat_1_budget)
        travel_progress        = get_progress(travel_budget_minus_expenses, cat_2_budget)
        food_progress          = get_progress(food_budget_minus_expenses, cat_3_budget)
        clothing_progress      = get_progress(clothing_budget_minus_expenses, cat_4_budget)
        entertainment_progress = get_progress(entertainment_budget_minus_expenses, cat_5_budget)

        # Renders the dashboard, which displays the following info
        return render_template(
            "dashboard.html",
            name         = user.name,
            password     = user.password,
            email        = user.email,
            expenditures = expenditures,
            id           = id,
            total_food_price                    = total_food_price,
            total_travel_price                  = total_travel_price,
            total_clothing_price                = total_clothing_price,
            total_entertainment_price           = total_entertainment_price,
            total_online_purchase_price         = total_online_purchase_price,

            avg_online_expenditures             = avg_online_expenditures,
            avg_entertainment_expenditures      = avg_entertainment_expenditures,
            avg_clothing_expenditures           = avg_clothing_expenditures,
            avg_travel_expenditures             = avg_travel_expenditures,
            avg_food_expenditures               = avg_food_expenditures,

            clothing_budget_minus_expenses      = clothing_budget_minus_expenses,
            travel_budget_minus_expenses        = travel_budget_minus_expenses,
            food_budget_minus_expenses          = food_budget_minus_expenses,
            online_budget_minus_expenses        = online_budget_minus_expenses,
            entertainment_budget_minus_expenses = entertainment_budget_minus_expenses,

            cat_1_budget     = cat_1_budget,
            cat_2_budget     = cat_2_budget,
            cat_3_budget     = cat_3_budget,
            cat_4_budget     = cat_4_budget,
            cat_5_budget     = cat_5_budget,

            cat_1_start_date = cat_1_start_date,
            cat_2_start_date = cat_2_start_date,
            cat_3_start_date = cat_3_start_date,
            cat_4_start_date = cat_4_start_date,
            cat_5_start_date = cat_5_start_date,

            cat_1_end_date   = cat_1_end_date,
            cat_2_end_date   = cat_2_end_date,
            cat_3_end_date   = cat_3_end_date,
            cat_4_end_date   = cat_4_end_date,
            cat_5_end_date   = cat_5_end_date,

            clothing_progress      = clothing_progress,
            entertainment_progress = entertainment_progress,
            online_progress        = online_progress,
            food_progress          = food_progress,
            travel_progress        = travel_progress,

            total_price            = total_price,
            user_hash              = hash_result,
            app_id                 = APP_ID
        )

@app.route('/webhook', methods=['POST'])
def intercom_webhook():
    x_signature_header = request.headers['X-Hub-Signature']
    json_blob          = request.data
    KEY                = os.getenv('MARSH_SECRET')
    hash_result        = hmac.new(KEY, json_blob, hashlib.sha1).hexdigest()
    if "sha1=" + hash_result == x_signature_header:
        return 'OK'
    else:
        return abort (400)

@app.route('/total-spent.json')
def budget_types_data():
    """ Bar chart shows totals for last 30 days """

    from utils import expenditure_total_amount_and_avg, budget_totals, get_dates_for_budget, get_progress, get_budget_per_category, connect_to_db 

    id               = session.get('id')
    today            = datetime.today().strftime('%Y-%m-%d')
    thirty_days_past = (datetime.today() + timedelta(-30)).strftime('%Y-%m-%d')

    logged_in = 'id' in session
    if logged_in:
        total_food_price, avg_food_expenditures                   = expenditure_total_amount_and_avg(3, id, thirty_days_past, today)
        total_clothing_price, avg_clothing_expenditures           = expenditure_total_amount_and_avg(4, id, thirty_days_past, today)
        total_entertainment_price, avg_entertainment_expenditures = expenditure_total_amount_and_avg(5, id, thirty_days_past, today)
        total_travel_price, avg_travel_expenditures               = expenditure_total_amount_and_avg(2, id, thirty_days_past, today)
        total_online_purchase_price, avg_online_expenditures      = expenditure_total_amount_and_avg(1, id, thirty_days_past, today)

    return jsonify({
        "labels": ["Food", "Clothing", "Entertainment", "Travel", "Online Purchases"],
        "datasets": [
            {
                "label": "Total Spent",
                "fillColor": "#6886C5",
                "strokeColor": "#6886C5",
                "pointColor": "#6886C5",
                "pointStrokeColor": "#fff",
                "pointHighlightFill": "#fff",
                "pointHighlightStroke": "#6886C5",
                "data": [total_food_price, total_clothing_price, total_entertainment_price, total_travel_price, total_online_purchase_price]
            },
            {
                "label": "Average",
                "fillColor": "#FFE0AC",
                "strokeColor": "#FFE0AC",
                "pointColor": "#FFE0AC",
                "pointStrokeColor": "#fff",
                "pointHighlightFill": "#fff",
                "pointHighlightStroke": "#FFE0AC",
                "data": [avg_food_expenditures, avg_clothing_expenditures, avg_entertainment_expenditures, avg_travel_expenditures, avg_online_expenditures]
            }
        ]
    })

@app.route('/expenditure-types.json')
def expenditure_types_data():
    """ Return data about expenditures to the pie chart """

    from utils import expenditure_total_amount_and_avg, budget_totals, get_dates_for_budget, get_progress, get_budget_per_category, connect_to_db 

    id               = session.get('id')
    today            = datetime.today().strftime('%Y-%m-%d')
    thirty_days_past = (datetime.today() + timedelta(-30)).strftime('%Y-%m-%d')

    travel_expenditures, avg_travel               = expenditure_total_amount_and_avg(2, id, thirty_days_past, today)
    entertainment_expenditures, avg_entertainment = expenditure_total_amount_and_avg(5, id, thirty_days_past, today)
    clothing_expenditures, avg_clothing           = expenditure_total_amount_and_avg(4, id, thirty_days_past, today)
    food_expenditures, avg_food                   = expenditure_total_amount_and_avg(3, id, thirty_days_past, today)
    online_purchase_expenditures, avg_online      = expenditure_total_amount_and_avg(1, id, thirty_days_past, today)

    return jsonify({
        'expenditures': [
            {
                "value": travel_expenditures,
                "color": "#385170",
                "highlight": "#2E425C",
                "label": "Travel"
            },
            {
                "value": entertainment_expenditures,
                "color": "#E2C275",
                "highlight": "#BEA362",
                "label": "Entertainment"
            },
            {
                "value": clothing_expenditures,
                "color": "#F0B7A4",
                "highlight": "#BE9182",
                "label": "Clothing"
            },
            {
                "value": food_expenditures,
                "color": "#A4D4AE",
                "highlight": "#8AB293",
                "label": "Food"
            },
            {
                "value": online_purchase_expenditures,
                "color": "#BE97DC",
                "highlight": "#9576AC",
                "label": "Online Purchase"
            }
        ]
    })

@app.route('/remove-budget/<int:id>', methods=["POST"])
def remove_budget(id):
    """ Remove a budget from the database """

    from models import User, Expenditure, Budget

    budget_at_hand = Budget.query.filter_by(id=id).first()
    user_id        = session.get('id')

    if user_id == budget_at_hand.budget_userid:
        db.session.delete(budget_at_hand)
        db.session.commit()
    return redirect(url_for('dashboard', id=user_id))

@app.route('/add-budget', methods=["POST"])
def add_budget():
    """ Add a budget """
    from models import Budget, Expenditure, User, Category
    from utils import expenditure_total_amount_and_avg, budget_totals, get_dates_for_budget, get_progress, get_budget_per_category, connect_to_db 

    id = session.get('id')
    budget = request.form.get("budget")
    category_id = int(request.form.get("category"))
    start_date = request.form.get("start-date")
    end_date = request.form.get("end-date")

    user_budget_query = Budget.query.filter_by(budget_userid=id).all()

    # Check for budgets in the database under the user ID in particular categories;
    # delete budgets that exist to override them
    # Check to see if you can modify it instead
    for query in user_budget_query:
        if query.category_id == category_id:
            db.session.delete(query)
            db.session.commit()

    # Add the budget to the database. It will be the only budget for that
    # category in the database for the user
    new_budget = Budget(budget=budget,
                        category_id=category_id,
                        budget_userid=id,
                        budget_start_date=start_date,
                        budget_end_date=end_date)

    # Insert the new budget into the budget table and commit the insert
    db.session.add(new_budget)
    db.session.commit()

    # Call functions in utils.py
    total_cat_price, avg_cat_expenditures = expenditure_total_amount_and_avg(category_id, id, start_date, end_date)
    cat_budget_minus_expenses = budget_totals(category_id, id, total_cat_price)

    # Call get_progress in utils.py to calculate the progress bar totals
    category_progress = get_progress(cat_budget_minus_expenses, budget)

    # Return jsonified budget info to submit-budget.js
    return jsonify({
        'id': new_budget.id,
        'category': new_budget.category.category,
        'category_id': category_id,
        'budget': budget,
        'cat_budget_minus_expenses': cat_budget_minus_expenses,
        'category_progress': category_progress
    })


@app.route('/add-expenditure-to-db', methods=["POST"])
def add_expenditure():
    """ Add new expenditure to the database """

    from models import Budget, Expenditure, User, Category
    from utils import expenditure_total_amount_and_avg, budget_totals, get_dates_for_budget, get_progress, get_budget_per_category, connect_to_db 

    # Set the value of the user id of the user in the session
    id = session.get('id')

    # Get values from the form
    category_id          = int(request.form.get("category"))
    price                = request.form.get("price")
    date_of_expenditure  = request.form.get("date")
    where_bought         = request.form.get("wherebought")
    description          = request.form.get("description")

    start_date, end_date = get_dates_for_budget(category_id, id)

    # Create a new expenditure object to insert into the expenditures table
    new_expenditure = Expenditure(
        category_id         = category_id,
        price               = price,
        date_of_expenditure = date_of_expenditure,
        where_bought        = where_bought,
        description         = description,
        expenditure_userid  = id
    )

    # Insert the new expenditure into the expenditures table and commit the insert
    db.session.add(new_expenditure)
    db.session.commit()

    # Unpacking the function call
    total_cat_price, avg_cat_expenditures = expenditure_total_amount_and_avg(category_id, id, start_date, end_date)
    budget_minus_expenses                 = budget_totals(category_id, id, total_cat_price)
    cat_budget                            = get_budget_per_category(category_id, id)
    category_progress                     = get_progress(budget_minus_expenses, cat_budget)

    expenditure_info = {
        'total_cat_price': total_cat_price,
        'avg_cat_expenditures': avg_cat_expenditures,
        'category_id': category_id,
        'expenditure_id': new_expenditure.id,
        'date_of_expenditure': new_expenditure.date_of_expenditure.strftime('%Y-%m-%d'),
        'where_bought': new_expenditure.where_bought,
        'description': new_expenditure.description,
        'price': str(new_expenditure.price),
        'category': new_expenditure.category.category,
        'cat_budget_minus_expenses': budget_minus_expenses,
        'category_progress': category_progress
    }

    return jsonify(expenditure_info)

@app.route('/remove-expenditure/<int:id>', methods=["POST"])
def remove_expenditure(id):
    """ Remove an expenditure from the database """

    from models import Budget, Expenditure, User, Category
    from utils import expenditure_total_amount_and_avg, budget_totals, get_dates_for_budget, get_progress, get_budget_per_category, connect_to_db 

    expenditure_at_hand = Expenditure.query.filter_by(id=id).first()
    db.session.delete(expenditure_at_hand)
    db.session.commit()
    return jsonify({"expenditure_id": id})

###############################
# MAIN
###############################

if __name__ == "__main__":

    #connect_to_db(app, spent_database)
    app.config['SQLALCHEMY_DATABASE_URI'] = database
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.app = app
    db.init_app(app)

    app.run()

