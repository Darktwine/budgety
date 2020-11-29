from budgety import db

class User(db.Model):
    """ Web app's user """

    __tablename__ = "users"
    id       = db.Column('id',       db.Integer, autoincrement=True, primary_key=True)
    name     = db.Column('name',     db.String(64))
    email    = db.Column('email',    db.String(64))
    password = db.Column('password', db.String(64))

class Category(db.Model):
    """ Category table """

    __tablename__ = "categories"
    id       = db.Column('id',       db.Integer, autoincrement=True, primary_key=True)
    category = db.Column('category', db.String(64))

class Budget(db.Model):
    """ This is the user's budget """

    __tablename__ = "budget"
    id                = db.Column('id',                db.Integer, autoincrement=True, primary_key=True)
    # the data type of tdb.he budget should match the ddb.ata type of the price
    budget            = db.Column('budget',            db.Numeric(15, 2))
    category_id       = db.Column('category_id',       db.Integer, db.ForeignKey('categories.id'))
    budget_userid     = db.Column('budget_userid',     db.Integer, db.ForeignKey('users.id'))
    budget_start_date = db.Column('budget_start_date', db.DateTime)
    budget_end_date   = db.Column('budget_end_date',   db.DateTime)

    user     = db.relationship('User',     backref=db.backref('budget'))
    category = db.relationship('Category', backref=db.backref('budget'))

    def __repr__(self):
        """ Provide useful info """

        return "<Budget id=%s budget=%s budget_userid=%s category=%s budget_start_date=%s budget_end_date=%s>" % (
            self.id, self.budget, self.budget_userid, self.category, self.budget_start_date, self.budget_end_date)

class Expenditure(db.Model):
    """ This contains expenditures """

    __tablename__ = "expenditures"

    id                   = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_id          = db.Column(db.Integer, db.ForeignKey('categories.id'))
    price                = db.Column(db.Numeric(15, 2))
    date_of_expenditure  = db.Column(db.DateTime)
    expenditure_userid   = db.Column(db.Integer, db.ForeignKey('users.id'))
    where_bought         = db.Column(db.String(100))
    description          = db.Column(db.UnicodeText)

    user     = db.relationship("User", backref=db.backref('expenditures'))
    category = db.relationship("Category", backref=db.backref('expenditures'))

db.create_all()
db.session.commit()
