from flask import Flask, render_template, redirect, url_for, session, g, request, make_response
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
#from forms import RegisterForm, LoginForm
from functools import wraps
from flask_mysqldb import MySQL 
import json
import sqlite3



app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

 
 

"""
cursor.execute(''' CREATE TABLE tables
(   
    table_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seats INTEGER NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL
); ''')
cursor.execute(''' INSERT INTO tables VALUES(4,50,100) ''')
""" 


def login_required(view):
    """
    if login needed, auto login if possible
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user == None:
            return redirect(url_for("auto_login_check",next=request.url))
        return view(**kwargs)
    return wrapped_view

@app.route("/", methods=["GET","POST"])
def index():
    """
    start route must be "/", directs straight to home page 
    """
    return redirect("home")

@app.route("/home", methods=["GET","POST"])
def home():     
    return render_template("home.html")

@app.route("/waiter_menu", methods=["GET","POST"])
def waiter_menu():     
    return render_template("waiter_menu.html")

@app.route("/choose_table", methods=["GET","POST"])
def choose_table():
    con = sqlite3.connect('app.db')
    with con:    
        cur = con.cursor()    

        cur.execute('SELECT x, y FROM tables ORDER BY table_id')
        data = cur.fetchall()
    
    table_positions = {}
    for i in range(len(data)):
        table_positions[i+1] = data[i]
    return render_template("choose_table.html", table_positions=table_positions)

@app.route("/<int:table>/take_order", methods=["GET","POST"])
def take_order(table):   
    if request.cookies.get("order"):
        order = json.loads(request.cookies.get("order"))
        return render_template("take_order.html", table=table, order=order)
    return render_template("take_order.html", table=table)

@app.route("/<int:table>/add_order/<meal>", methods=["GET","POST"])
def add_order(table, meal):
    order = []
    if request.cookies.get("order"):
        order = json.loads(request.cookies.get("order"))
    order.append(str(meal))
    
    response = make_response(redirect(url_for('take_order', table=1)))
    response.set_cookie('order', json.dumps(order), max_age=(60*60*24))
    return response

@app.route("/<int:table>/remove_order/<meal>", methods=["GET","POST"])
def remove_order(table, meal):
    order = json.loads(request.cookies.get("order"))
    for i in range(len(order)):
        if meal == order[i]:
            index = i
    order.pop(index)
    
    response = make_response(render_template("take_order.html", table=table, order=order))
    response.set_cookie('order', json.dumps(order), max_age=(60*60*24))
    return response

@app.route("/<int:table>/cancel_order", methods=["GET","POST"])
def cancel_order(table):
    
    response = make_response(render_template("take_order.html", table=table))
    response.set_cookie('order', '', expires=0)
    return response

@app.route("/move_tables", methods=["GET","POST"])
def move_tables():
    con = sqlite3.connect('app.db')
    with con:    
        cur = con.cursor()    

        cur.execute('SELECT x, y FROM tables ORDER BY table_id')
        data = cur.fetchall()
    
    table_positions = {}
    for i in range(len(data)):
        table_positions[i+1] = data[i]
    return render_template("move_tables.html", table_positions=table_positions)

@app.route('/save_tables', methods=['GET','POST'])
def save_tables():
    co_ords = request.get_json()
    if co_ords is not None:
        con = sqlite3.connect('app.db')
        with con:    
            cur = con.cursor()
            for i in range(4):
                cur.execute("UPDATE tables SET x = '"+co_ords[i*2]+"', y = '"+co_ords[(i*2)+1]+"' WHERE table_id ="+str(i+1)+"; ")
                con.commit()
        
    return redirect(url_for('choose_table'))
    