from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from model import db, Resto, Locals, User, Item, SearchForm, Ratings
from faker import Faker
from sqlalchemy import text

import socketserver as socketserver
import traceback as traceback
import random as random
import decimal as decimal
import sys

app = Flask(__name__)


app.config['DEBUG'] = True
engine = create_engine('postgresql://postgres:abc123@localhost/restaurants')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abc123@localhost/restaurants'  # noqa
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


@app.route("/", methods=['GET', 'POST'])
@app.route("/restaurant", methods=['GET', 'POST'])
def main():
    data = query_restaurants()
    category = query_category()
    form = SearchForm(request.form)
    if request.method == 'POST':
        search = request.form['search']
        option = request.form['type_resto']
        resto = request.form['resto_location']
        if search != "":
            # return redirect(url_for("search_resto", resto_name=search))
            print('John')
        elif option != 'Type':
            return redirect(url_for("resto_category", resto_type=option))
        else:
            return redirect(url_for("find_location", resto_name=resto))
    return render_template("index.html", category=category, data=data, form=form)  # noqa


@app.route("/restaurant/items/<resto_id>/<resto_name>")
def find_resto_menu(resto_id, resto_name):
    resto_item = db.session.query(Item, Resto).join(Resto, Item.restaurantid == Resto.restaurantid).filter(Resto.restaurantid == resto_id).order_by(Item.category).all()  # noqa

    return render_template("item.html", data=resto_item)  # noqa


@app.route("/restaurant/<resto_name>")
def search_resto(resto_name):
    data = db.session.query(Resto, Locals).join(Locals, Resto.restaurantid == Locals.restaurantid).filter(Resto.types.like("%"+resto_name+"%")).all()  # noqa
    return render_template("type.html", data=data)


@app.route("/restaurant/<resto_type>")
def resto_category(resto_type):
    data = db.session.query(Resto.name, Locals.manager_name, Locals.first_open_date).join(Resto, Locals, Locals.restaurantid == Resto.restaurantid).filter(Resto.types == resto_type)  # noqa
    return render_template("type.html", data=data)


@app.route("/restaurant/location/<resto_name>")
def find_location(resto_name):
    data = db.session.query(Locals.manager_name, Locals.first_open_date, Locals.street_address, Locals.phone_number, Locals.hour_open, Locals.hour_close).join(Resto, Locals.restaurantid == Resto.restaurantid).filter(Resto.name == resto_name)  # noqa
    return render_template("info.html", data=data)


@app.route("/restaurant/rating/<resto_name>")
def find_ratings(resto_name):
    data = db.session.query(User.name, Ratings.date, Ratings.comments, Ratings.food, Ratings.mood, Ratings.staff, Ratings.price).join(Ratings, Ratings.user_id == User.user_id and Resto.restaurantid == Ratings.Restuarantid).filter(Resto.name == resto_name).order_by(Ratings.date)  # noqa

    # access data like so data[0]
    return render_template("rating.html", data=data, name=resto_name)

def find_max_item():
    #data = db.session.execute("select * from restaurant")

    queryF = db.session.execute("select res.name,r.name, ra.price,ra.food,ra.mood, ra.staff from rater r , rating ra, restaurant res where r.user_id = ra.user_id and ra.restaurantid = res.restaurantid group by (r.name,res.restaurantid,ra.price,ra.food,ra.mood, ra.staff) order by (res.name,r.name);")# noqa

    queryG= db.session.execute("select distinct res.name, l.phone_number,res.types from restaurant res, location l, rating ra where res.restaurantid = ra.restaurantid and l.restaurantid = res.restaurantid and ra.date not between '2015-01-01' and '2015-12-31' order by (res.name);")# noqa

    queryH= db.session.execute("select distinct res.name, l.first_open_date from restaurant res , location l ,rating ra where res.restaurantid = ra.restaurantid and l.restaurantid = res.restaurantid and ra.staff <(select min(ra.staff) from rater r, rating ra where r.name = 'Stone' and ra.user_id = r.user_id);")# noqa
    #spacing problem with fastfoods
    queryI= db.session.execute("select distinct res.name, r.name from rater r, rating ra ,restaurant res where r.user_id = ra.user_id and ra.restaurantid = res.restaurantid and res.types =' Fast Food ' and ra.food = 5 ;")# noqa

    queryJ= db.session.execute("select distinct res.types, count(res.types) from restaurant res, rating ra where ra.restaurantid = res.restaurantid group by (res.types) order by(count) desc;")# noqa

    queryK= db.session.execute("select distinct r.name, r.join_date,r.reputation from rating ra, rater r, restaurant res where ra.restaurantid = res.restaurantid and ra.user_id = r.user_id and ra.mood = 5 and ra.food = 5;")# noqa

    queryL= db.session.execute("select distinct r.name,r.reputation from rating ra, rater r, restaurant res where ra.restaurantid = res.restaurantid and ra.user_id = r.user_id and ra.mood = 5 or ra.food = 5; ")# noqa



    for item in data:
        print(data0.name)
    for item in data:
        print(item.Item.name, item.Item.price, item.Locals.manager_name)


def query_category():
    data = db.session.query(Resto.types).order_by(Resto.types).distinct()
    return data


def query_restaurants():
    data = db.session.query(Resto).order_by(Resto.name)
    return data


if __name__ == '__main__':
    app.run(debug=True)
