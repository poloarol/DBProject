from flask import Flask, render_template

app = Flask(__name__)

app.config['SQLALHEMY_DATABASE_URL'] = 'postgresql://localhost/restaurants'
