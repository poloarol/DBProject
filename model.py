from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, SubmitField, RadioField, validators  # noqa
from wtforms.fields.html5 import DateField
import datetime as datime

db = SQLAlchemy()


class Resto(db.Model):
    """ Model for the Restuarant table """
    __tablename__ = 'restaurant'

    restaurantid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(20), nullable=False, unique=True)
    types = db.Column(db.VARCHAR(20), nullable=False)
    url = db.Column(db.VARCHAR(50))

    def __init__(self, name, types, url):
        self.name = name
        self.types = types
        self.url = url

    def __repr__(self):
        return '<restaurantid> {}'.format(self.name, self.types, self.url)


class Locals(db.Model):
    """ Model for the Locations """
    __tablename__ = 'location'
    locationid = db.Column(db.Integer, primary_key=True)
    first_open_date = db.Column(db.Date(), nullable=False)
    manager_name = db.Column(db.VARCHAR(20), nullable=False)
    phone_number = db.Column(db.VARCHAR(20), nullable=False)
    street_address = db.Column(db.VARCHAR(50), nullable=False)
    hour_open = db.Column(db.VARCHAR(10), nullable=False)
    hour_close = db.Column(db.VARCHAR(10), nullable=False)
    restaurantid = db.Column(db.Integer, db.ForeignKey("restaurant.restaurantid"), nullable=False)  # noqa

    def __init__(self, first_open_date, manager_name, phone_number, street_address, hour_open, hour_close, restaurantid):  # noqa
        self.first_open_date = first_open_date
        self.hour_close = hour_close
        self.hour_open = hour_open
        self.street_address = street_address
        self.restaurantid = restaurantid
        self.phone_number = phone_number
        self.manager_name = manager_name

    def __repr__(self):
        return '<location> {}'.format(self.manager_name, self.street_address)


class User(db.Model):
    """ Model for Raters Table """
    __tablename__ = 'rater'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.VARCHAR(30), nullable=False)
    name = db.Column(db.VARCHAR(15), nullable=False)
    join_date = db.Column(db.Date, nullable=False)
    rater_type = db.Column(db.VARCHAR(15), nullable=False)
    reputation = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.CheckConstraint('reputation >= 1 AND reputation <= 5', name='reputation'),)  # noqa

    def __init__(self, email, name, join_date, rater_type, reputation):  # noqa
        self.email = email
        self.join_date = join_date
        self.name = name
        self.rater_type = rater_type
        self.reputation = int(reputation)


class Ratings(db.Model):
    """ Ratings Table model, groups user comments in the db """
    __tablename__ = 'rating'
    user_id = db.Column(db.Integer, db.ForeignKey("rater.user_id"), nullable=False, primary_key=True)  # noqa
    date = db.Column(db.Date(), nullable=False, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    food = db.Column(db.Integer, nullable=False)
    mood = db.Column(db.Integer, nullable=False)
    staff = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.TEXT, nullable=True)
    restaurantid = db.Column(db.Integer, db.ForeignKey("restaurant.restaurantid"), nullable=False)  # noqa

    def __init__(self, user_id, date, price, food, mood, staff, comments, restaurantid):  # noqa
        self.user_id = user_id
        self.date = date
        self.price = price
        self.food = food
        self.mood = mood
        self.staff = staff
        self.comments = comments
        self.restaurantid = restaurantid

    __table_args__ = (db.CheckConstraint('price >= 1 AND price <= 5', name='price'),  # noqa
                      db.CheckConstraint('food >= 1 AND food <= 5', name='food'),  # noqa
                      db.CheckConstraint('mood >= 1 AND mood <= 5', name='mood'),  # noqa
                      db.CheckConstraint('staff >= 1 AND staff <= 5', name='staff',))  # noqa


class Item(db.Model):
    """ Item data model, The different items present in a restaurant """
    __tablename__ = 'menuitem'
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(30), nullable=False)
    category = db.Column(db.VARCHAR(15), nullable=False)
    description = db.Column(db.TEXT, nullable=False)
    price = db.Column(db.Numeric(5, 2), nullable=False)
    restaurantid = db.Column(db.Integer, db.ForeignKey("restaurant.restaurantid"), nullable=False)  # noqa

    resto = db.relationship('Resto', backref='resto', lazy=True)

    def __init__(self, name, category, description, price, restaurantid):  # noqa
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.restaurantid = restaurantid


class RateItem(db.Model):
    """ Model for Rated Item, allos users to rate an item """
    __tablename__ = "ratingitem"
    user_id = db.Column(db.Integer, db.ForeignKey("rater.user_id"), primary_key=True)  # noqa
    date = db.Column(db.Date(), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("menuitem.item_id"), primary_key=True)  # noqa
    rating = db.Column(db.Integer, nullable=False)  # noqa
    comment = db.Column(db.Text, nullable=False)

    def __init__(self, user_id, date, item_id, rating, comment):
        self.user_id = user_id
        self.date = date
        self.item_id = item_id
        self.rating = rating
        self.comment = comment

    __table_args__ = (db.CheckConstraint('rating >= 1 AND rating <= 5', name='rating'),)  # noqa


class SearchForm(Form):
    """ Search From which allows to query the restaurant and Locals table """
    option = StringField('Option')
    name = StringField('Name')
    submit = SubmitField('submit')


class QueryRestaurants(Form):
    """ Form which allows for the query of both the raters and Rating Table """
    types = RadioField('Label', choices=[('food', 'FOOD'), ('mood', 'MOOD'), ('price', 'PRICE'), ('staff', 'STAFF')])  # noqa
    date = DateField('Date', format='%Y-%m-%d')
    rater_name = StringField('Rater Name')
    submit = SubmitField('Submit')


class RestoPicture:
    """ Stores path to pictures for a specific restaurants """
    __tablename__ = 'restopicture'
    pic_id = db.Column(db.Integer, primary_key=True)
    resto_id = db.Column(db.Integer, db.ForeignKey("restaurant.restaurantid"))
    path = db.Column(db.Text, nullable=False)


class LoginForm(Form):
    submit = SubmitField('Submit')


class CreateForm(Form):
    submit = SubmitField('Submit')


class CreateResto(Form):
    submit = SubmitField('Submit')


class CreateItem(Form):
    submit = SubmitField('Submit')
