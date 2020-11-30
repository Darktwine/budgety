
# Budgety

**Budgety** is a simple budget tracking web application.

# Starting Up

## Installing dependencies

Move into the `budgety` directory and run the following command to install the
web application's module dependencies:

```
$ python --version
Python 3.8.6
$ pip install -r requirements.txt
```

If you've the latest version of Python, `pip` should come preinstalled with it.

## Serving the webapp

1. Execute `load.py` to load the data under `budgety/data/` into the tables.
   This will load some few users, along with their data.
2. Serve the webapp by executing `python app.py`. You'll be provided with a
   local server.
3. The following are the users and their passwords in the database:

|Email|Password|
|:-------------|:-------|
|jotaro@kujo.com|StarPlatinum|
|josuke@higashikat.com|CrazyDiamond|
|giorno@giovanna.com|GoldExperience|
|jolyne@cujo.com|StoneFree|
|trish@una.com|SpiceGirl|

# Dashboard description

* **AVERAGE SPENT OVER THE LAST 30 DAYS:** Bar chart that displays the average
amount spent by the user per category over the last 30 days. First column
displays the total spent and the second one the average of that.

* **TOTAL SPENT OVER THE LAST 30 DAYS:** Pie chart that displays the total
  amount spent by the user per category over the last 30 days. 

* **BUDGET:** Table that displays the budget for each category within a period
  of time.

* **BUDGET REMAINING:** Table that displays the remaining amount for each
  category.

* **EXPENDITURES:** Table that displays the amount spent by the user on a
  certain date per category.

* **TOTAL SPENT:** Table that displays the total amount spent by the user per
category within a certain period of time.

* **AVERAGE SPENT:** Table that displays the average amount spent by the user per
category within a certain period of time.

# Acknowledgement

This was duplicated from https://github.com/emilydowgialo/Spent.
