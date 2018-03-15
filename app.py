from flask import Flask, render_template
from sqlalchemy import create_engine
from model import db, Restuarant
from faker import Faker

import socketserver as socketserver

app = Flask(__name__)


app.config['DEBUG'] = True
engine = create_engine('postgresql://postgres:polo@localhost/restaurants')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:polo@localhost/restaurants'  # noqa
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

fake = Faker()
db.init_app(app)
# db.create_all()

with app.app_context():
    try:
        db.drop_all()
        db.create_all()
        resto = Restuarant(name="Joe's", type="Bar & Grill", url="joeysshit")
        db.session.add(resto)
        db.session.commit()
    except Exception:
        print("Unable to add tuple to database")


@app.route("/")
def main():
    r = Restuarant.query.filter_by()
    return "Hello World"


if __name__ == '__main__':
    app.run()
