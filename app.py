from flask import Flask, render_template
from sqlalchemy import create_engine
from model import db, Resto, Locals, User, Item
from faker import Faker
from sqlalchemy import text

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


@app.route("/restaurant")
def main():
    data = query_restaurants()
    category = query_category()
    return render_template("index.html", category=category, data=data)


@app.route("/restaurant/items/<resto_id>/<resto_name>")
def find_resto_menu(resto_id, resto_name):
    resto_item = db.session.query(Item, Resto).join(Resto, Item.restaurantid == Resto.restaurantid).filter(Resto.restaurantid == resto_id).order_by(Item.category).all()  # noqa

    return render_template("item.html", data=resto_item)  # noqa


# @app.route("/restaurant/<resto_id>")
# def resto_info(resto_name):
#     data = db.session.query(Locals, Resto).join(Resto, Locals.restaurantid == Resto.restaurantid).filter(Resto.restaurantid == resto_id)  # noqa
#
#     return render_template()


@app.route("/restaurant/<resto_type>")
def resto_category(resto_type):
    data = db.session.query(Resto).filter(Resto.types == resto_type)
    return render_template("type.html", data=data)


# def find_max_item():
#     data = db.session.execute("select * from restaurant")
#     for item in data:
#         print(data.name)
#     for item in data:
#         print(item.Item.name, item.Item.price, item.Locals.manager_name)

def query_category():
    data = db.session.query(Resto.types).order_by(Resto.types).distinct()
    return data


def query_restaurants():
    data = db.session.query(Resto).order_by(Resto.name)
    return data


if __name__ == '__main__':
    app.run(debug=True)
