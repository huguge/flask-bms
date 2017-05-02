from flask import Flask,render_template
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_script import Manager

app = Flask(__name__)
Bootstrap(app)
moment = Moment(app)
manager= Manager(app)

@app.route('/')
def index():
    return render_template('index.html',app_name = 'Flask-BMS')

@app.route('/ebooks')
def ebooks():
    return render_template('ebooks.html',app_name = 'Flask-BMS')
@app.route('/books')
def books():
    return render_template('books.html',app_name = 'Flask-BMS')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_pages/404.html'),404

@app.errorhandler(500)
def server_500_error(e):
    return render_template('error_pages/500.html'),404

# python main.py runserver
if __name__ == '__main__':
    manager.run()