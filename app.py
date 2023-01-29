from flask import Flask, render_template, redirect, url_for, session, g, request, make_response
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import TableForm
from functools import wraps
from flask_mysqldb import MySQL 
import json
import sqlite3

"""
remove meal - meal has been selected but then order not placed
cancel meal - meal order has been placed but then cancelled

cancel order - tables order was selected but not placed
"""

app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['MYSQL_USER'] = 'root' # someone's deets
app.config['MYSQL_PASSWORD'] = '' # someone's deets
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'bens_restaurant' # someone's deets
app.config['MYSQL_CURSORCLASS']= 'DictCursor'

mysql = MySQL(app)

#cur = mysql.connection.cursor()

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
    con = sqlite3.connect('app.db')
    with con:    
        cur = con.cursor()    

        cur.execute('SELECT * FROM dish')
        meals = cur.fetchall()
        
        cur.execute(
            """
                SELECT dish.name, orders.status, order_id, dish.dishType
                FROM orders JOIN dish 
                ON orders.dish_id = dish.dish_id
                WHERE orders.table_id = ? 
                AND orders.status != ?
                AND orders.status != ?
            """,(table,'complete', 'cancelled')
        )
        ordered = cur.fetchall()
        
    if request.cookies.get("ordering"+str(table)):
        ordering = json.loads(request.cookies.get("ordering"+str(table)))

        return render_template("take_order.html", table=table, ordering=ordering, meals=meals, ordered=ordered)
    
    return render_template("take_order.html", table=table, meals=meals, ordered=ordered)

@app.route("/<int:table>/add_order/<meal>", methods=["GET","POST"])
def add_order(table, meal):
    ordering = []
    if request.cookies.get("ordering"+str(table)):
        ordering = json.loads(request.cookies.get("ordering"+str(table)))
    con = sqlite3.connect('app.db')
    with con:   
        # If not enough ingredients to make the meal, not added to order
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
            ordering.append(str(meal))
        else:
            response = make_response(redirect(url_for('take_order', table=table)))
    response = make_response(redirect(url_for('take_order', table=table)))
    response.set_cookie('ordering'+str(table), json.dumps(ordering), max_age=(60*60*24))
    return response

@app.route("/<int:table>/remove_meal/<meal>", methods=["GET","POST"])
def remove_meal(table, meal):
    ordering = json.loads(request.cookies.get("ordering"+str(table)))
    for i in range(len(ordering)):
        if meal == ordering[i]:
            index = i
    ordering.pop(index)
    
    response = make_response(redirect(url_for("take_order", table=table)))
    response.set_cookie('ordering'+str(table), json.dumps(ordering), max_age=(60*60*24))
    return response

@app.route("/<int:table>/cancel_meal/<int:meal_id>", methods=["GET","POST"])
def cancel_meal(table, meal_id):
    
    con = sqlite3.connect('app.db')
    with con:    
        cur = con.cursor()
                
        cur.execute("DELETE FROM orders WHERE order_id = ? AND table_id = ?;",(meal_id, table ))
        con.commit()
    
    return redirect(url_for("take_order", table=table))

@app.route("/<int:table>/cancel_order", methods=["GET","POST"])
def cancel_order(table):
    
    response = make_response(redirect(url_for("take_order", table=table)))
    response.set_cookie('ordering'+str(table), '', expires=0)
    return response


@app.route("/<int:table>/complete_order", methods=["GET","POST"])
def complete_order(table):  
    con = sqlite3.connect('app.db')
    with con:    
        cur = con.cursor()    

        

    if request.cookies.get("ordering"+str(table)):
        ordering = json.loads(request.cookies.get("ordering"+str(table)))
        con = sqlite3.connect('app.db')
        with con:  
            cur.execute(
                """
                    SELECT dish.name, orders.status 
                    FROM orders JOIN dish 
                    ON orders.dish_id = dish.dish_id
                    WHERE orders.table_id = ? 
                    AND orders.status != ?
                    AND orders.status != ?
                """,(table,'complete', 'cancelled')
            )
            ordered = cur.fetchall()
            
            for meal in ordering:
                cur = con.cursor()

                cur.execute('SELECT dish_id, cook_time FROM dish WHERE name = ?',(meal,))
                data = cur.fetchone()
                cur.execute("INSERT INTO orders (time, dish_id, table_id, status) VALUES (?, ?, ?, 'waiting');",(data[1], data[0], table))
                con.commit()
    
    response = make_response(redirect(url_for('take_order', table=table)))
    response.set_cookie('ordering'+str(table), json.dumps([]), max_age=(60*60*24))
    return response

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

@app.route("/remove_table_menu", methods=["GET","POST"])
def remove_table_menu():
    con = sqlite3.connect('app.db')
    with con:    
        cur = con.cursor()    

        cur.execute('SELECT table_id, x, y FROM tables ORDER BY table_id')
        data = cur.fetchall()
    
    table_positions = {}
    for i in range(len(data)):
        table_positions[data[i][0]] = (data[i][1], data[i][2])
    return render_template("manager/remove_table.html", table_positions=table_positions)

@app.route("/<int:table>/remove_table", methods=["GET", "POST"])
def remove_table(table):
    con = sqlite3.connect('app.db')
    with con:   
        cur = con.cursor() 
        cur.execute("DELETE FROM tables WHERE table_id = ?;",(table,))
        con.commit()
    return redirect(url_for('remove_table_menu'))
            
@app.route("/break_timetable", methods=["GET","POST"])
def break_timetable():
    staff_breaks = [{'name':'Ben', 'time':'9:00'},{'name':'John', 'time':'13:00'},{'name':'Tim', 'time':'8 :00'}]
    return render_template("manager/break_timetable.html", staff_breaks=staff_breaks)

@app.route("/roster_timetable", methods=["GET","POST"])
def roster_timetable():
    con = sqlite3.connect('app.db')
    with con:   
        cur = con.cursor() 
        cur.execute("SELECT * FROM roster JOIN staff ON roster.staff_id = staff.staff_id ORDER BY staff.staff_id;")
        roster = cur.fetchall() 
    return render_template("manager/roster_timetable.html", roster=roster)

