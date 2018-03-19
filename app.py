from flask import Flask, render_template
from sqlalchemy import create_engine
from model import db, Resto, Locals, User, Item, Ratings, RateItem
from faker import Faker

import socketserver as socketserver
import traceback as traceback
import random as random

app = Flask(__name__)


app.config['DEBUG'] = True
engine = create_engine('postgresql://postgres:abc123@localhost/restaurants')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:abc123@localhost/restaurants'  # noqa
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

fake = Faker()
db.init_app(app)
# db.create_all()

with app.app_context():
	Ratings.__table__.drop(engine)
	# User.__table__.drop(engine)
    # data = ''
    # try:
    #     with open("db.txt", "r") as f:
    #         for line in f:
    #             data = line.split(",")
                # resto = Resto(name=data[0], type=data[1], url="")
                # db.session.add(resto)
                # db.session.commit()
                # elif(line == "time"):
                #     next(line)
                # fdate = fake.date(pattern="%Y-%m-%d", end_datetime=None)
                # name = fake.name()
                # phone = fake.phone_number()
                # street = fake.street_address()
                # data = line.split(",")
                # loco = Locals(first_open_date=fdate,
                #                  manager_name=name,
                #                  phone_number=phone,
                #                  street_address=street,
                #                  hour_open=data[0],
                #                  hour_close=data[1],
                #                  restaurantid=data[2])
                # email = fake.email()
                # date = fake.date(pattern="%Y-%m-%d", end_datetime=None)
                # user = User(email, data[0], date, data[1],1)
                # db.session.add(user)
                # db.session.commit()

    # except Exception:
        # traceback.print_exc()


@app.route("/")
def main():
    return fake.name()


if __name__ == '__main__':
    app.run()
