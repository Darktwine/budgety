""" Utility file to seed spending database in seed_data/ """

from sqlalchemy import func
from datetime import datetime
from models import User, Expenditure, Budget, Category
from budgety import db, app
import os

user_file        = "data/users.csv"
category_file    = "data/categories.csv"
budget_file      = "data/budgets.csv"
expenditure_file = "data/expenditures.csv"

def get_datetime(dt):
    return datetime(int(dt[:4]), int(dt[5:7]), int(dt[8:10]))

def load_users():
    """ Load users from users.csv into database """

    # delete table if already exist to prevent user duplication.
    User.query.delete()

    # Read users.csv file and insert data into the session
    with open(user_file) as f:
        for _ in range(1):
            next(f)
        
        for row in f:
            row       = row.rstrip()
            user_data = row.split(",")
            id        = int(user_data[0])
            name      = user_data[1]
            email     = user_data[2]
            password  = user_data[3]
            
            # add user to session
            user = User(id=id, name=name, email=email, password=password)
            db.session.add(user)

        # save session
        db.session.commit()

def load_categories():
    """ Load categories from categories.csv into database """

    Category.query.delete()

    with open(category_file) as f:
        for _ in range(1):
            next(f)
        
        for row in f:
            row             = row.rstrip()
            categories_data = row.split(",")

            id       = int(categories_data[0])
            category = categories_data[1]

            category_model = Category(id=id, category=category)
            db.session.add(category_model)
        db.session.commit()

def load_budgets():
    """ Load budget from budget.csv into database """

    Budget.query.delete()

    with open(budget_file) as f:
        for _ in range(1):
            next(f)
        
        for row in f:
            row         = row.rstrip()
            budget_data = row.split(",")
            id                = int(budget_data[0])
            budget            = budget_data[1]
            category_id       = budget_data[2]
            budget_userid     = budget_data[3]
            budget_start_date = budget_data[4]
            budget_end_date   = budget_data[5]

            budget = Budget(
                id                = id,
                budget            = budget,
                category_id       = category_id,
                budget_userid     = budget_userid,
                budget_start_date = get_datetime(budget_start_date),
                budget_end_date   = get_datetime(budget_end_date)
            )

            db.session.add(budget)

        db.session.commit()

def load_expenditures():
    """ Load expenditures from expenditures.csv into database """

    Expenditure.query.delete()

    with open(expenditure_file) as f:
        for _ in range(1):
            next(f)
        
        for row in f:
            row = row.rstrip()
            expenditure_data = row.split(",")
            print(expenditure_data)

            id                   = expenditure_data[0]
            category_id          = expenditure_data[1]
            price                = expenditure_data[2]
            date_of_expenditure  = expenditure_data[3]
            expenditure_userid   = expenditure_data[4]
            where_bought         = expenditure_data[5]
            description          = expenditure_data[6]

            expenditure = Expenditure(
                id                   = id,
                category_id          = category_id,
                price                = price,
                date_of_expenditure  = get_datetime(date_of_expenditure),
                expenditure_userid   = expenditure_userid,
                where_bought         = where_bought,
                description          = description
            )

            db.session.add(expenditure)

        db.session.commit()

#def set_val_user_id():
#    """ Set value for the next user id after seeding database """
#
#    # Get the Max user id in the database
#    result = db.session.query(func.max(User.id)).one()
#
#    max_id = int(result[0])
#
#    # Set the value for the next user_id to be max_id + 1
#    # Note to self: the 'users_id_seq' variable is based on the Users table
#    query = "SELECT setval('users_id_seq', :new_id)"
#
#    db.session.execute(query, {'new_id': max_id + 1})
#    db.session.commit()
#
#
#def set_val_expenditure_id():
#    """ Set value for the next expenditure id after seeding database """
#
#    # Get the Max expenditure id in the database
#    result = db.session.query(func.max(Expenditure.id)).one()
#
#    max_id = int(result[0])
#
#    # Set the value for the next expenditure id to be max_id + 1
#    query = "SELECT setval('expenditures_id_seq', :new_id)"
#
#    db.session.execute(query, {'new_id': max_id + 1})
#    db.session.commit()
#
#
#def set_val_budget_id():
#    """ Set value for the next budget id after seeding database """
#
#    # Get the Max user id in the database
#    result = db.session.query(func.max(Budget.id)).one()
#
#    max_id = int(result[0])
#
#    # Set the value for the next user_id to be max_id + 1
#    query = "SELECT setval('budget_id_seq', :new_id)"
#
#    db.session.execute(query, {'new_id': max_id + 1})
#    db.session.commit()
#
#
#def set_val_category_id():
#    """ Set value for the next category id after seeding database """
#
#    # Get the Max user id in the database
#    result = db.session.query(func.max(Category.id)).one()
#
#    max_id = int(result[0])
#
#    # Set the value for the next user_id to be max_id + 1
#    query = "SELECT setval('categories_id_seq', :new_id)"
#
#    db.session.execute(query, {'new_id': max_id + 1})
#    db.session.commit()

if __name__ == "__main__":
    #app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:pass@IP_POSTGRESQL/postgres"
    #spent_database = os.getenv('POSTGRES_DB_URL', 'postgres:///spending')
    #connect_to_db(app, spent_database)

    #database = 'sqlite:////tmp/budget-tracking.db'
    #app.config['SQLALCHEMY_DATABASE_URI'] = database
    #app.config['SQLALCHEMY_ECHO'] = True
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    #db.app = app
    #db.init_app(app)

    #with app.app_context():
    #    db.create_all()
    # In case tables haven't been created, create them

    # Import different types of data
    load_users()
    load_categories()
    load_budgets()
    load_expenditures()
    #set_val_user_id()
    #set_val_category_id()
    #set_val_expenditure_id()
    #set_val_budget_id()
