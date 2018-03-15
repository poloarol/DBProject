from flask_sqlalchemy import SQLAlchemy
import datetime as datime

db = SQLAlchemy()

# class BaseModel(db.Model):
#     """ Base data model for objects """
#     __abstract__ = True
#
#     # define here __repr__ and json methods or any common methods
#     # that you need for all your models
#
#     def __init__(self, *args):
#         super().__init__(*args)
#
#     def __repr__(self):
#         """ Define a base way to print models """
#
#         return '%s(%s)' % (self.__class__.__name__, {
#             column: value
#             for column, value in self._to_dict().items()
#         })
#
#     def json(self):
#         """ Define a base way to jsonify, dealing with datetime objects """
#         return {
#             column: value if not ininstance(value, datime.date) else value.strftime('%Y-%m-%d')
#             for column, value in self._to_dict().items()
#         }


class Restuarant(db.Model):
    """ Model for the Restuarant table """
    __tablename__ = 'resto'

    restaurantid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(20), nullable=False)
    type = db.Column(db.VARCHAR(20), nullable=False)
    url = db.Column(db.VARCHAR(50))

    def __init__(self, name, type, url):
        self.name = name
        self.type = type
        self.url = url

    def __repr__(self):
        return '<id> {}'.format(self.name, self.type, self.url)


class Locations(db.Model):
    """ Model for the Locations """
    __tablename__ = 'locate'
    locationid = db.Column(db.Integer, primary_key=True)
    first_open_date = db.Column(db.Date, nullable=False)
    manager_name = db.Column(db.VARCHAR(30), nullable=False)
    phone_number = db.Column(db.VARCHAR(10), nullable=False)
    street_address = db.Column(db.VARCHAR(30), nullable=False)
    hour_open = db.Column(db.VARCHAR(5), nullable=False)
    hour_close = db.Column(db.VARCHAR(5), nullable=False)
    restaurantid = db.Column(db.Integer, db.ForeignKey("resto.restaurantid"), nullable=False)
