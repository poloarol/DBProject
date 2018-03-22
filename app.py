from flask import Flask, render_template
from sqlalchemy import create_engine
from model import db, Resto, Locals, User, Item
from faker import Faker
from sqlalchemy.sql import func

import socketserver as socketserver
import traceback as traceback
import random as random
import decimal as decimal
import sys

app = Flask(__name__)


app.config['DEBUG'] = True
engine = create_engine('postgresql://postgres:polo@localhost/restaurants')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:polo@localhost/restaurants'  # noqa
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

fake = Faker()
db.init_app(app)
# db.create_all()

# with app.app_context:
#     User.__table__.create(engine)
#     with open("db.txt", "r") as f:
#         for line in f:
#             data = line.split(",")
#             user = User(fake.email(), fake.date(), data[0])
#             db.session.add(user)
#             db.session.commit()


@app.route("/")
def main():
    data = query_restaurants()
    display_resto_info("Bar & Grill")
    return render_template("index.html", data=data)


@app.route("/restaurant/items/<resto_name>")
def find_resto_menu(resto_name):
    data = db.session.query(Item, Resto).join(Resto, Item.restaurantid == Resto.restaurantid).filter(Resto.name == resto_name).order_by(Item.category).all()  # noqa
    for item in data:
        print(item.Item.category + " " + item.Item.name)


@app.route("/restaurant/<resto_type>")
def display_resto_info(resto_type):
    print(1)


def query_restaurants():
    data = db.session.query(Resto).order_by(Resto.name)
    return data


if __name__ == '__main__':
    app.run(debug=True)
