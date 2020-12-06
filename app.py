from flask import Flask, render_template, request, url_for
import requests
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField

app = Flask(__name__)
app.config["SECRET_KEY"] = "dnAD67vf68PcDArJ"
app.config[
    "MONGO_URI"] = "mongodb+srv://lalbe019:0dVfX6Foolm6lhX2@cluster0.pfmkn.mongodb.net/<dbname>?retryWrites=true&w=majority"

mongo = PyMongo(app)


class Expenses(FlaskForm):
    description = StringField("Description")
    category = SelectField("Category", choices=[
        ("rent", "Rent"),
        ("electricity", "Electricity"),
        ("phone", "Phone"),
        ("groceries", "Groceries"),
        ("entertainment", "Entertainment"),
        ("restaurants", "Restaurants"),
        ("gas", "Gas")])
    currency = SelectField("Currency", choices=[
        ('USDUSD', 'US Dollar'),
        ('USDBTC', 'Bitcoin'),
        ('USDCAD', 'Canadian Dollar'),
        ('USDEUR', 'Euro')])
    cost = DecimalField("Cost")
    date = DateField("Date", format='%m-%d-%Y')

def get_total_expenses(category):
    my_expenses = mongo.db.expenses.find({"category": category})
    total_cost = 0
    for i in my_expenses:
        total_cost += float(i["cost"])
    return total_cost


def currency_converter(cost, currency):
    url = "http://api.currencylayer.com/live?access_key=ca71727826e0b83b486118e97e123e6c"
    response = requests.get(url).json()
    print(cost)
    print(response)
    converted_cost = float(cost / response['quotes'][currency])

    return converted_cost


@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    total_cost = 0
    for i in my_expenses:
        total_cost += float(i["cost"])
    expensesByCategory = [
        ("rent", get_total_expenses("rent")),
        ("electricity", get_total_expenses("electricity")),
        ("phone", get_total_expenses("phone")),
        ("groceries", get_total_expenses("groceries")),
        ("entertainment", get_total_expenses("entertainment")),
        ("restaurants", get_total_expenses("restaurants")),
        ("gas", get_total_expenses("gas"))
    ]
    return render_template("index.html", expenses=total_cost, expensesByCategory=expensesByCategory)


@app.route('/addExpenses', methods=["GET", "POST"])
def addExpenses():
    expensesForm = Expenses(request.form)
    if request.method == "POST":

        description = request.form['description']
        category = request.form['category']
        cost = float(request.form['cost'])
        currency = request.form['currency']
        date = request.form['date']

        cost = currency_converter(cost, currency)

        mongo.db.expenses.insert_one(
                {'description': description,
                    'category': category,
                    'cost': float(cost),
                    'date': date})

        return render_template("expenseAdded.html")
    return render_template("addExpenses.html", form=expensesForm)



app.run()
