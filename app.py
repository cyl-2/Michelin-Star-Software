from flask import Flask, render_template, redirect, url_for, session, g, request, make_response
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import TableForm, AddToRosterForm
from functools import wraps
from flask_mysqldb import MySQL 
from generate_roster import Roster
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
app.config['MYSQL_PASSWORD'] = 'PaZARIX9' # someone's deets
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_DB'] = 'sys' # someone's deets
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
    cur = mysql.connection.cursor()
        
    cur.execute('SELECT table_id, x, y FROM tables ORDER BY table_id')
    data = cur.fetchall()
    table_positions = {}
    for i in range(len(data)):
        table_positions[data[i]['table_id']] = (data[i]['x'], data[i]['y'])
    return render_template("choose_table.html", table_positions=table_positions)

@app.route("/<int:table>/take_order", methods=["GET","POST"])
def take_order(table):  
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM dish')
    meals = cur.fetchall()
        
    cur.execute(
        """
            SELECT dish.name, orders.status, order_id, dish.dishType
            FROM orders JOIN dish 
            ON orders.dish_id = dish.dish_id
            WHERE orders.table_id = %s 
            AND orders.status != %s
            AND orders.status != %s
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
    cur = mysql.connection.cursor()
       
    # If not enough ingredients to make the meal, not added to order


    cur.execute('SELECT dish_id FROM dish WHERE name = %s',(meal,))
    dish_ids = cur.fetchall()
    
    for id in dish_ids:
        cur.execute('SELECT ingredient_id FROM dish_ingredient WHERE dish_id = %s',(id['dish_id'],))
        ingredient_ids = cur.fetchall()
    
    min = 100
    for id in ingredient_ids:
        cur.execute('SELECT MIN(quantity) FROM ingredient WHERE ingredient_id = %s',(id['ingredient_id'],))
        value = cur.fetchone()
        if value['MIN(quantity)'] < min:
            min = value['MIN(quantity)']
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
    
    cur = mysql.connection.cursor()
     
    cur.execute("DELETE FROM orders WHERE order_id = %s AND table_id = %s;",(meal_id, table ))
    mysql.connection.commit()
    
    return redirect(url_for("take_order", table=table))

@app.route("/<int:table>/cancel_order", methods=["GET","POST"])
def cancel_order(table):
    
    response = make_response(redirect(url_for("take_order", table=table)))
    response.set_cookie('ordering'+str(table), '', expires=0)
    return response


@app.route("/<int:table>/complete_order", methods=["GET","POST"])
def complete_order(table):  
    cur = mysql.connection.cursor()
        
           

    if request.cookies.get("ordering"+str(table)):
        ordering = json.loads(request.cookies.get("ordering"+str(table)))
        
        for meal in ordering:
            cur.execute('SELECT dish_id, cook_time FROM dish WHERE name = %s',(meal,))
            data = cur.fetchone()
            cur.execute("INSERT INTO orders (time, dish_id, table_id, status) VALUES (%s, %s, %s., 'waiting');",(data['cook_time'], data['dish_id'], table))
            mysql.connection.commit()
    
    response = make_response(redirect(url_for('take_order', table=table)))
    response.set_cookie('ordering'+str(table), json.dumps([]), max_age=(60*60*24))
    return response

@app.route("/move_tables", methods=["GET","POST"])
def move_tables():
    cur = mysql.connection.cursor()
        
    cur.execute('SELECT table_id, x, y FROM tables ORDER BY table_id')
    data = cur.fetchall()
    
    table_positions = {}
    for i in range(len(data)):
        table_positions[data[i]['table_id']] = (data[i]['x'], data[i]['y'])
    
    return render_template("move_tables.html", table_positions=table_positions)

@app.route('/save_tables', methods=['GET','POST'])
def save_tables():
    co_ords = request.get_json()
    if co_ords is not None:
        cur = mysql.connection.cursor()
        for i in range(int(len(co_ords)/2)):
            cur.execute("UPDATE tables SET x = '"+co_ords[i*2]+"', y = '"+co_ords[(i*2)+1]+"' WHERE table_id ="+str(i+1)+"; ")
            mysql.connection.commit()
        
    return redirect(url_for('choose_table'))
    
@app.route("/add_table", methods=["GET", "POST"])
def add_table():
    form = TableForm()
    if form.validate_on_submit():
        table_number = form.table_number.data
        seats = form.seats.data
        x = str(form.x.data) + 'px'
        y = str(form.y.data) + 'px'

        cur = mysql.connection.cursor()
            
        cur.execute('SELECT * FROM tables WHERE table_id = %s',(table_number,))
        data = cur.fetchall()
        if len(data) > 0:
            form.table_number.errors.append("Table Number already in use")
            return render_template("manager/add_table.html", form=form)
        else:
            cur.execute("INSERT INTO tables VALUES (%s, %s, %s, %s);",(table_number, seats, x, y))
            mysql.connection.commit()
            return redirect(url_for('choose_table'))

    return render_template("manager/add_table.html", form=form)

@app.route("/remove_table_menu", methods=["GET","POST"])
def remove_table_menu():
    cur = mysql.connection.cursor()
    cur.execute('SELECT table_id, x, y FROM tables ORDER BY table_id')
    data = cur.fetchall()
    
    table_positions = {}
    for i in range(len(data)):
        table_positions[data[i]['table_id']] = (data[i]['x'], data[i]['y'])
    return render_template("manager/remove_table.html", table_positions=table_positions)

@app.route("/<int:table>/remove_table", methods=["GET", "POST"])
def remove_table(table):
    cur = mysql.connection.cursor()
        
    cur.execute("DELETE FROM tables WHERE table_id = %s;",(table,))
    mysql.connection.commit()
    return redirect(url_for('remove_table_menu'))
            
@app.route("/break_timetable", methods=["GET","POST"])
def break_timetable():
    staff_breaks = [{'name':'Ben', 'time':'9:00'},{'name':'John', 'time':'13:00'},{'name':'Tim', 'time':'8:00'}]
    return render_template("manager/break_timetable.html", staff_breaks=staff_breaks)

@app.route("/generate_roster", methods=["GET","POST"])
def generate_roster():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM shift_requirements;")
    requirements = cur.fetchall()
    cur.execute("SELECT staff_id FROM staff;")
    data = cur.fetchall()
    employees = []
    for id in data:
        employees.append(id['staff_id'])
    roster = Roster()
    print(requirements)
    result = roster.generate(requirements, employees)
    cur.execute("UPDATE roster SET mon = '', tue = '', wed = '', thu = '', fri = '', sat = '', sun = '';")
    mysql.connection.commit()
    for day in result:
        for shift in result[day]:
            for person in result[day][shift]:##
                command = 'UPDATE roster SET '+ day +' = %s WHERE staff_id = %s;'
                cur.execute(command,( shift, person))
                mysql.connection.commit()
    return redirect(url_for('roster_timetable'))


@app.route("/roster_timetable", methods=["GET","POST"])
def roster_timetable():
    cur = mysql.connection.cursor()
        
        
    cur.execute("SELECT * FROM roster JOIN staff ON roster.staff_id = staff.staff_id ORDER BY staff.staff_id;")
    roster = cur.fetchall()
    return render_template("manager/roster_timetable.html", roster=roster)

@app.route("/delete_from_roster", methods=["GET","POST"])
def delete_from_roster():
    cur = mysql.connection.cursor()
       
        
    cur.execute("SELECT * FROM roster JOIN staff ON roster.staff_id = staff.staff_id ORDER BY staff.staff_id;")
    roster = cur.fetchall() 
    return render_template("manager/delete_from_roster.html", roster=roster)

@app.route("/remove_roster_slot/<int:staff_id>/<int:day>", methods=["GET","POST"])
def remove_roster_slot(staff_id, day):
    week = ['mon','tue','wed','thu','fri','sat','sun']
    cur = mysql.connection.cursor()
           
    cur.execute("UPDATE roster SET "+week[day]+" = '' WHERE staff_id = %s;",(staff_id,))
    mysql.connection.commit()
    return redirect(url_for('delete_from_roster'))

@app.route("/add_to_roster_timetable", methods=["GET","POST"])
def add_to_roster_timetable():
    cur = mysql.connection.cursor()
    
    form = AddToRosterForm()
    if form.validate_on_submit():
        staff_id = form.staff_id.data
        cur.execute("SELECT * FROM staff WHERE staff_id = %s",(staff_id,))
        staff = cur.fetchone() 
        if staff is not None:
            day = form.day.data
            time = form.time.data
            cur.execute("UPDATE roster SET "+day+" = %s WHERE staff_id = %s;",(time, staff_id,))
            mysql.connection.commit()
        else:
            form.staff_id.errors = "Staff ID does not exists"
    cur.execute("SELECT * FROM roster JOIN staff ON roster.staff_id = staff.staff_id ORDER BY staff.staff_id;")
    roster = cur.fetchall() 
    return render_template("manager/add_to_roster_timetable.html", roster=roster, form=form)