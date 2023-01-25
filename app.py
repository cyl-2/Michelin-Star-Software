from flask import Flask, render_template, redirect, url_for, session, g, request, make_response
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import TableForm
from functools import wraps
from flask_mysqldb import MySQL 
import json
import sqlite3



app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['MYSQL_USER'] = 'root' # someone's deets
app.config['MYSQL_PASSWORD'] = '' # someone's deets
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'world' # someone's deets
app.config['MYSQL_CURSORCLASS']= 'DictCursor'

mysql = MySQL(app)


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

        cur.execute('SELECT table_id, x, y FROM tables ORDER BY table_id')
        data = cur.fetchall()
    
    table_positions = {}
    for i in range(len(data)):
        table_positions[data[i][0]] = (data[i][1], data[i][2])
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
    
    con = sqlite3.connect('app.db')
    with con:    
        cur = con.cursor()

        cur.execute('SELECT dish_id FROM dish WHERE name = ?',(meal,))
        dish_ids = cur.fetchall()
        
        for id in dish_ids:
            cur.execute('SELECT ingredient_id FROM dish_ingredient WHERE dish_id = ?',(id[0],))
            ingredient_ids = cur.fetchall()
        
        min = 100
        for id in ingredient_ids:
            cur.execute('SELECT MIN(quantity) FROM ingredient WHERE ingredient_id = ?',(id[0],))
            value = cur.fetchone()
            if value[0] < min:
                min = value[0]
        if min > 0:
            order.append(str(meal))
        else:
            response = make_response(redirect(url_for('take_order', table=1)))
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

@app.route("/<int:table>/complete_order", methods=["GET","POST"])
def complete_order(table):   
    if request.cookies.get("order"):
        order = json.loads(request.cookies.get("order"))
        for meal in order:
            con = sqlite3.connect('app.db')
            with con:    
                cur = con.cursor()

                cur.execute('SELECT dish_id, cook_time FROM dish WHERE name = ?',(meal,))
                data = cur.fetchone()
                
                cur.execute("INSERT INTO orders VALUES (?, ?);",(data[0], data[1]))
                con.commit()
                
    return redirect(url_for('choose_table'))

@app.route("/move_tables", methods=["GET","POST"])
def move_tables():
    con = sqlite3.connect('app.db')
    with con:    
        cur = con.cursor()    

        cur.execute('SELECT table_id, x, y FROM tables ORDER BY table_id')
        data = cur.fetchall()
    
    table_positions = {}
    for i in range(len(data)):
        table_positions[data[i][0]] = (data[i][1], data[i][2])
    
    return render_template("move_tables.html", table_positions=table_positions)

@app.route('/save_tables', methods=['GET','POST'])
def save_tables():
    co_ords = request.get_json()
    if co_ords is not None:
        con = sqlite3.connect('app.db')
        with con:    
            cur = con.cursor()
            for i in range(len(co_ords)):
                cur.execute("UPDATE tables SET x = '"+co_ords[i*2]+"', y = '"+co_ords[(i*2)+1]+"' WHERE table_id ="+str(i+1)+"; ")
                con.commit()
        
    return redirect(url_for('choose_table'))
    
@app.route("/add_table", methods=["GET", "POST"])
def add_table():
    form = TableForm()
    if form.validate_on_submit():
        table_number = form.table_number.data
        seats = form.seats.data
        x = str(form.x.data) + 'px'
        y = str(form.y.data) + 'px'

        con = sqlite3.connect('app.db')
        with con:    
            cur = con.cursor()

            cur.execute('SELECT * FROM tables WHERE table_id = ?',(table_number,))
            data = cur.fetchall()
            if len(data) > 0:
                form.table_number.errors.append("Table Number already in use")
                return render_template("manager/add_table.html", form=form)
            else:
                cur.execute("INSERT INTO tables VALUES (?, ?, ?, ?);",(table_number, seats, x, y))
                con.commit()
                return redirect(url_for('choose_table'))

    return render_template("manager/add_table.html", form=form)