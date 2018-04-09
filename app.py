from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, func, desc, asc
from model import db, Resto, Locals, User, Item, SearchForm
from model import Ratings, QueryRestaurants, LoginForm
from model import CreateForm, CreateResto, CreateItem
from faker import Faker
from sqlalchemy import text

import socketserver as socketserver
import traceback as traceback
import random as random
import decimal as decimal
import sys
import datetime as datetime
import pdb as pdb

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
    rating = most_popular()
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
    return render_template("index.html", category=category, data=data, form=form, rating=rating)  # noqa


@app.route("/restaurant/<resto_name>")
def search_resto(resto_name):
    """ finds the name of a restaurant manager, location etc."""
    # 1A
    data = db.session.query(Resto, Locals).join(Locals, Resto.restaurantid == Locals.restaurantid).filter(Resto.types.like("%"+resto_name+"%")).all()  # noqa
    return render_template("type.html", data=data)


@app.route("/restaurant/items/<resto_id>/<resto_name>")
def find_resto_menu(resto_id, resto_name):
    # 1B
    """ display the menu items of a specific restaurant """
    data = db.session.query(Item, Resto).join(Resto, Item.restaurantid == Resto.restaurantid).filter(Resto.restaurantid == resto_id).order_by(Item.category).all()  # noqa

    return render_template("item.html", data=data)  # noqa


@app.route("/restaurant/<resto_type>")
def resto_category(resto_type):
    """ Finds all restaurant which belong to a specific category """
    # 1C
    donee = avg_price(resto_type)
    data = db.session.query(Resto.name, Locals.manager_name, Locals.first_open_date).join(Locals, Locals.restaurantid == Resto.restaurantid).filter(Resto.types == resto_type)  # noqa

    return render_template("type.html", data=data, donee=donee)


@app.route("/restaurant/location/<resto_name>")
def find_location(resto_name):
    # 1D
    """ Finds the max Item, Manager Name and all in a restaurant """
    subquery = db.session.query(func.max(Item.price)).join(Resto, Item.restaurantid == Resto.restaurantid).join(Locals, Locals.restaurantid == Resto.restaurantid).filter(Resto.name == resto_name).distinct().subquery()  # noqa

    data = db.session.query(Item.name, Item.price, Locals.manager_name, Resto.url, Locals.hour_open, Locals.hour_close).join(Resto, Item.restaurantid == Resto.restaurantid).join(Locals, Locals.restaurantid == Resto.restaurantid).filter(Resto.name == resto_name).filter(Item.price == subquery)  # noqa

    return render_template("info.html", data=data, resto=resto_name)


def avg_price(resto_type):
    # 1E
    """ Finds the average price per category in a restaurant """
    subquery = db.session.query(Resto.restaurantid).filter(Resto.types == resto_type).subquery()  # noqa
    data = db.session.query(Item.category, func.avg(Item.price)).join(Resto, Item.restaurantid == Resto.restaurantid).filter(Resto.restaurantid.in_(subquery)).group_by(Resto.types, Item.category).order_by(Resto.types, Item.category)  # noqa

    return data


@app.route("/restaurant/ratings/")
def user_resto_rating():
    # 2F
    """ Finds the total number of ratings for each restaurant by each rater """
    data = db.session.query(Resto.name, User.name, Ratings.price, Ratings.food, Ratings.mood, Ratings.staff).join(Ratings, Resto.restaurantid == Ratings.restaurantid).join(User, User.user_id == Ratings.user_id).group_by(User.name, Resto.restaurantid, Ratings.price, Ratings.food, Ratings.mood, Ratings.staff).order_by(Resto.name, User.name)  # noqa

    return render_template('user_ratings.html', data=data)


@app.route("/restaurant/rating/<date>/")
def rating_date(date):
    # 2G
    """ Restuarants not rated in a specific month and year """
    data = db.session.query(Resto.name, Locals.manager_name, Resto.types).join(Locals, Locals.restaurantid == Resto.restaurantid).join(Ratings, Ratings.restaurantid == Resto.restaurantid).filter(func.extract('month', Ratings.date) != date[1]).all()  # noqa
    return render_template('rating_date.html', data=data)


@app.route("/restaurants/ratings/lower_than/<name>")
def min_staff(name):
    """ Staff ratings of restaurants compared to that given by a specific rater """  # noqa
    subquery = db.session.query(func.min(Ratings.staff)).join(User, User.user_id == Ratings.user_id).filter(User.name == name).subquery()  # noqa

    data = db.session.query(Resto.name, Locals.manager_name, Locals.first_open_date).join(Locals, Locals.restaurantid == Resto.restaurantid).filter(Ratings.staff > subquery).distinct()  # noqa

    return render_template('min.html', data=data)


@app.route('/restaurant/ratings/<types>/<criteria>')
def highest_rating(criteria, types):
    """ Finds the highest rating for a specific criteria based on restaurant type"""  # noqa

    if criteria == 'food':
        data = db.session.query(Resto.name, User.name).join(Ratings, Resto.restaurantid == Ratings.restaurantid).filter(User.user_id == Ratings.user_id).filter(Resto.types == types).filter(Ratings.food >= 4)  # noqa
    elif criteria == 'price':
        data = db.session.query(Resto.name, User.name).join(Ratings, Resto.restaurantid == Ratings.restaurantid).filter(User.user_id == Ratings.user_id).filter(Resto.types == types).filter(Ratings.price >= 4)  # noqa
    elif criteria == 'mood':
        data = db.session.query(Resto.name, User.name).join(Ratings, Resto.restaurantid == Ratings.restaurantid).filter(User.user_id == Ratings.user_id).filter(Resto.types == types).filter(Ratings.mood >= 4)  # noqa
    else:
        data = db.session.query(Resto.name, User.name).join(Ratings, Resto.restaurantid == Ratings.restaurantid).filter(User.user_id == Ratings.user_id).filter(Resto.types == types).filter(Ratings.staff >= 4)  # noqa

    return render_template('criteria_type.html', data=data)


def most_popular():
    """ Most popular restaurant types in C-1378 """
    data = db.session.execute("select distinct res.types, count(res.types) from restaurant res, rating ra where ra.restaurantid = res.restaurantid group by (res.types) order by(count) desc;").fetchall()  # noqa

    return data


@app.route("/restaurant/miscellenous/food/mood")
def food_mood():
    q1 = popular_and_criteria()
    q2 = popular_or_criteria()
    return render_template("food_mood.html", q1=q1, q2=q2)


def popular_and_criteria():
    data = db.session.execute("select distinct r.name, r.join_date,r.reputation from rating ra, rater r, restaurant res where ra.restaurantid = res.restaurantid and ra.user_id = r.user_id and ra.mood >=4  and ra.food >= 4;")  # noqa

    return data


def popular_or_criteria():
    data = db.session.execute("select distinct r.name, r.join_date,r.reputation from rating ra, rater r, restaurant res where ra.restaurantid = res.restaurantid and ra.user_id = r.user_id and ra.mood >= 4 OR ra.food >= 4;")  # noqa

    return data


@app.route("/restaurant/ratings/<resto_name>")
def find_ratings(resto_name):
    data = db.session.query(User.name, Ratings.date, Ratings.comments, Ratings.food, Ratings.mood, Ratings.staff, Ratings.price).join(Ratings, Ratings.user_id == User.user_id and Resto.restaurantid == Ratings.Restuarantid).filter(Resto.name == resto_name).order_by(Ratings.date)  # noqa

    return render_template("rating.html", data=data, name=resto_name)

<<<<<<< HEAD
def names_and_reputation():
    data = db.session.execute("select res.name, r.name, r.reputation, m.name, m.price, ri.comment from rater r, ratingitem ri, menuitem m, restaurant res where m.item_id= ri.item_id and res.name = 'Don Cuco' and r.name = any (Select result1.name from (select results.resname,results.ratername as name,count(results.ratername) as tcount from (select res.name as resname, r.name as ratername, mi.name as itemname from menuitem mi inner join ratingitem ri on mi.item_id=ri.item_id inner join restaurant res on res.restaurantid = mi.restaurantid inner join rater r on r.user_id = ri.user_id where res.name = 'Don Cuco') as results group by(results.resname,results.ratername,results.ratername) order by tcount desc limit 2) as result1);")
    
def rating_lower_john():
    data = db.session.execute("select subQ.name, subQ.email, subQ.overall_ratings from (select r1.name, r1.email,((avg(ra1.price)+avg(ra1.food)+avg(ra1.mood)+avg(ra1.staff))/4) as overall_ratings from rater r1, rating ra1 where r1.user_id = ra1.user_id group by (r1.name,r1.email))as subQ where subQ.overall_ratings < (select (avg(ra.price)+avg(ra.food)+avg(ra.mood)+avg(ra.staff))/4 from rater r, rating ra where ra.user_id = r.user_id and r.name like '%John%');")  # noqa


@app.route("/restaurant/ratings/frequent/rater/<resto_name>")
def freq_raters(resto_name):
    return render_template()
=======
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
>>>>>>> ad94c262f80914923064176461c5bb3f4f0c3961


def query_category():
    data = db.session.query(Resto.types).order_by(Resto.types).distinct()
    return data


def query_restaurants():
    data = db.session.query(Resto.restaurantid, Resto.name, Resto.types).order_by(Resto.name)  # noqa
    return data


def query_raters():
    data = db.session.query(User.name).order_by(User.name)
    return data


@app.route("/restaurant/query/form/", methods=['GET', 'POST'])
def query_form():
    form = QueryRestaurants(request.form)
    resto = query_category()
    user = query_raters()

    if request.method == 'POST':
        date = request.form['date']
        rate = request.form['rater']
        rest = request.form['resto']
        # options = request.form['types']

        if date != "":
            newdate = change_time(date)
            return redirect(url_for("rating_date", date=newdate))
        elif rate != "Rater" and rate != "":
            return redirect(url_for("min_staff", name=rate))  # noqa
        elif rest != "":
            return redirect(url_for("highest_rating", criteria='food', types=rest))
        else:
            return redirect(url_for('main'))
    return render_template('queryform.html', form=form, resto=resto, user=user)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        name = request.form['email']
        print(name)
    return render_template("login.html", form=form)


@app.route("/create_account", methods=['GET', 'POST'])
def new_account():
    form = CreateForm(request.form)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        types = request.form['type']
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        user = User(email, name, date, types, 1)
        db.session.add(user)
        db.session.commit()
    return render_template("create.html", form=form)


def change_time(date):
    a = date.replace(",", "").split(" ")
    d = {"January": 1, "Ferbuary": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "October": 10, "November": 11, "December": 12, "September": 9}  # noqa

    date = datetime.date(year=int(a[2]), month=d[a[0]], day=int(a[1]))
    date = datetime.datetime.strftime(date, '%Y-%m-%d')
    date = datetime.datetime.strptime(date, '%Y-%m-%d')

    date = (date.month, date.year)
    return date


@app.route("/add", methods=['GET', 'POST'])
def addItem():
    form = CreateItem(request.form)

    if request.method == 'POST':
        name = request.form['item']
        category = request.form['category']
        price = request.form.get('price')
        resto = request.form['resto']
        description = request.form['description']
        item = Item(name, category, description, price, resto)
        db.session.add(item)
        db.session.commit()

    data = db.session.query(Resto.restaurantid, Resto.name).order_by(Resto.name)

    return render_template('additem.html', form=form, data=data)




@app.route("/new_resto", methods=['GET', 'POST'])
def add_resto():
        form = CreateResto(request.form)

        if request.method == 'POST':
            name = request.form['name']
            category = request.form['type']
            url = request.form['url']
            resto = Resto(name, category, url)
            db.session.add(resto)
            db.session.commit()

        return render_template('addresto.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
