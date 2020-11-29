from datetime import datetime
from models import Expenditure, Budget
from app import db

########## THIS FILE CONTAINS WIDELY USED FUNCTIONS ###########

def expenditure_total_amount_and_avg(category_id, id, start, end):
    """ Calculate the total amount and avg spent in one particular category """

    # List of expenditure objects
    expenditures = Expenditure.query.filter_by(
        category_id=category_id, expenditure_userid=id).filter(
        Expenditure.date_of_expenditure.between(start, end)).all()

    total_price = 0
    for expenditure in expenditures:
        total_price += expenditure.price

    avg_expenditures = 0
    if len(expenditures) > 0:
        avg_expenditures = total_price/len(expenditures)

    return float(total_price), float(avg_expenditures)

def get_dates_for_budget(category_id, id):
    """ Get the start and end date for a budget """

    # Get budget object
    budget = Budget.query.filter_by(category_id=category_id, budget_userid=id).all()

    if len(budget) > 0:
        start_date = budget[0].budget_start_date
        end_date = budget[0].budget_end_date
    else:
        start_date = datetime.now()
        end_date = start_date

    # Return start and end dates
    return start_date, end_date

def budget_totals(category_id, id, total_price):
    """ Calculate budget minus expenditures made """

    # Get budget object for user and category.
    b = Budget.query.filter_by(category_id=category_id, budget_userid=id).first()

    diff = 0
    if b is not None:
        diff = float(b.budget) - float(total_price)

    return diff

def get_budget_per_category(category_id, id):
    """ Gets budget for particular category """

    # Get budgets for user and category.
    budget = Budget.query.filter_by(budget_userid=id, category_id=category_id).all()

    # If a budget exists, return it, otherwise return 0
    if len(budget) > 0:
        budget = budget[0].budget
    else:
        budget = 0

    return budget


def get_total_for_category(cat, lst):
    """ Gets the total amount per category """

    # Set total to 0
    total = 0
    queries = lst

    # Extract expenditures by id and add the price to the total
    for query in queries:
        if query.category_id == cat:
            total += query.price

    return total


def get_progress(cat_minus_expenses, budget):
    """ Get the progress bar percentage """

    # Get perentage for progress bar and account for possible divide by 0 error
    try:
        progress = (float(cat_minus_expenses)/float(budget))
    except ZeroDivisionError:
        progress = 0

    # Multiply above total by 100 for a percentage between 1 and 100
    cat_progress = str(progress * 100)

    return cat_progress
    
def connect_to_db(app, database):
    """ Connect the database to our Flask app. """
    app.config['SQLALCHEMY_DATABASE_URI'] = database
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.app = app
    db.init_app(app)
