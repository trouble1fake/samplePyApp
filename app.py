"""Flask Login Example and instagram fallowing find"""

from flask import Flask, url_for, render_template, request, redirect, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
import requests
import html


def getfollowedby(url):
    """View Instagram user follower count"""
    link = f'https://www.instagram.com/{url}/?__a=1'
    user = requests.get(link)
    return (user.json()['graphql']['user']['edge_followed_by']['count'])


def getname(url):
    return url.split("instagram.com/")[1].replace("/", "")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    """ Create user table"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/', methods=['GET', 'POST'])
def home():
    """ Session control"""
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        if request.method == 'POST':
            username = getname(request.form['username'])
            return render_template('index.html', data=getfollowedby(username))
        return render_template('index.html')


#-------------------------Vulnerable Code Below-------------------------#


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     """Login Form"""
#     if request.method == 'GET':
#         return render_template('login.html')
#     else:
#         name = request.form['username']
#         passw = request.form['password']
#         try:
#             data = db.engine.execute(("select * from User where username = '"+name+"' and password = '"+ passw + "'")).fetchall()
#             if data != []:
#                 session['logged_in'] = True
#                 return redirect(url_for('home'))
#             else:
#                 return render_template_string(f"Invalid Password of username: {name}")
#         except Exception as e:
#             print(e)
#             return "Wrong Password"



#--------------------------Secured Code Below-------------------------


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Form"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['username']
        passw = request.form['password']
        try:
       
            data = User.query.filter_by(username=name, password=passw).first()	
            if data is not None:
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                return html.escape(f"Invalid Password of username: {name}")

        except Exception as e:
            print(e)
            return "Wrong Password"

#----------------------------------------------------------------------------


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Register Form"""
    if request.method == 'POST':
        new_user = User(
            username=request.form['username'],
            password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('register.html')


@app.route("/logout")
def logout():
    """Logout Form"""
    session['logged_in'] = False
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.secret_key = "123"
    app.run(host='0.0.0.0', port=8000)
    
