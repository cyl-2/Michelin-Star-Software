from flask import Flask, render_template, redirect, url_for, session, g, request, make_response, flash, Markup
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, ContactForm, ReplyForm, EmployeeForm, ResetPasswordForm, NewPasswordForm, CodeForm, TableForm, AddToRosterForm, RosterRequestForm, ProfileForm, RejectRosterRequestForm, AddDishForm, UserPic, cardDetails,submitModifications
from functools import wraps
from flask_mysqldb import MySQL 
from generate_roster import Roster
import json
from flask_mail import Mail, Message
import datetime
import random, string, time
from random import sample
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"
UPLOAD_FOLDER = "picture"
app.config["SESSION_PERMANENT"] = False
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#cur = mysql.connection.cursor()
# For the email function
mail= Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'no.reply.please.and.thank.you@gmail.com'
app.config['MAIL_PASSWORD'] = 'plseiqkwvpwfxwwr'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail.init_app(app)

app.config['MYSQL_USER'] = 'er12' # someone's deets
app.config['MYSQL_PASSWORD'] = 'meiph' # someone's deets
app.config['MYSQL_HOST'] = 'cs1.ucc.ie'
app.config['MYSQL_DB'] = 'cs2208_er12' # someone's deets
app.config['MYSQL_CURSORCLASS']= 'DictCursor'

mysql = MySQL(app)

@app.before_request
def logged_in():
    g.user = session.get("username", None)
    g.access = session.get("access_level", None)

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("customer_login")) #,next=request.url))
        return view(**kwargs)
    return wrapped_view

@app.route("/waiter_menu", methods=["GET","POST"])
def waiter_menu():     
    return render_template("staff/waiter_menu.html")

@app.route("/choose_table", methods=["GET","POST"])
def choose_table():
    cur = mysql.connection.cursor()
        
    cur.execute('SELECT table_id, x, y FROM tables ORDER BY table_id')
    data = cur.fetchall()
    table_positions = {}
    for i in range(len(data)):
        table_positions[data[i]['table_id']] = (data[i]['x'], data[i]['y'])
    return render_template("staff/choose_table.html", table_positions=table_positions)

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
        return render_template("staff/take_order.html", table=table, ordering=ordering, meals=meals, ordered=ordered)
    
    return render_template("staff/take_order.html", table=table, meals=meals, ordered=ordered)

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
    
    return render_template("staff/move_tables.html", table_positions=table_positions)

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
def staff_only(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.access != "ordinary staff":
            return redirect(url_for("index")) #,next=request.url))
        return view(**kwargs)
    return wrapped_view

def manager_only(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.access != "managerial":
            return redirect(url_for("index"))
        return view(**kwargs)
    return wrapped_view

@app.route("/auto_login_check_customer", methods=["GET","POST"])
def auto_login_check_customer():
    if request.cookies.get("email"):
        session.clear()
        session["username"] = request.cookies.get("email")
        next_page = request.args.get("next")
        if not next_page:
            return redirect("index")
        else:
            return redirect( next_page )
    return redirect( "customer_login" )

@app.route("/auto_login_check_staff", methods=["GET","POST"])
def auto_login_check_staff():
    if request.cookies.get("email"):
        session.clear()
        session["username"] = request.cookies.get("email")
        next_page = request.args.get("next")
        if not next_page:
            return redirect("index")
        else:
            return redirect( next_page )
    return redirect( "staff_login" )

@app.route("/delete_cookie/<cookie>",methods=["GET","POST"])
def delete_cookie(cookie):
    response = redirect(url_for('index'))
    response.set_cookie(cookie, '', expires=0)
    return response

@app.route("/logout", methods=["GET","POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html"),404

@app.route("/", methods=["GET","POST"])
def index():
    return render_template("home.html", title = "Home")
    
# Register for an account
@app.route("/registration", methods=["GET", "POST"])
def registration():
    cur = mysql.connection.cursor()
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        code = "None"

        '''
            Assuming that only customers can create new accounts
            New staff accounts will be created by the manager and then credentials will
            be provided to the staff member
        '''

        cur.execute("SELECT * FROM customer WHERE email = %s", (email,))
        r1 = cur.fetchone()

        if r1 is not None:
            form.email.errors.append("Sorry, the email you entered already exists, please use another email.")
        elif password.isupper() or password.isdigit() or password.islower() or password.isalpha():
            form.password.errors.append("Create a STRONG password with one uppercase character, one lowercase character and one number")
        else:
            cur.execute("""INSERT INTO customer ( email, first_name, last_name, password, code)
                        VALUES (%s,%s,%s,%s,%s);""", (email, first_name, last_name, generate_password_hash(password), code))
            mysql.connection.commit()
            cur.close()
            flash("Successful Registration! Please login now")
            return redirect( url_for("customer_login"))

            #response = make_response(redirect("auto_login_check"))
            #response.set_cookie("email",email,max_age=(60*60*24))
            #return response
    return render_template("customer/registration.html", form=form, title="Registration")

# Login to customer account
@app.route("/customer_login", methods=["GET", "POST"])
def customer_login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM customer WHERE email = %s", (email,))
        customer = cur.fetchone()
        cur.close()

        if 'counter' not in session:
            session['counter'] = 0

        if customer is None:
            form.email.errors.append("Email doesn't exist, please check your spelling")
        elif not check_password_hash(customer["password"], password):
            form.password.errors.append("Incorrect password")
            session['counter'] = session.get('counter') + 1
            if session.get('counter')==3:
                flash(Markup('Oh no, are you having trouble logging in? Click <a href="forgot_password">here</a> to reset your password.')) # reset password link need to go here
                session.pop('counter', None)
        else:
            session.clear()
            session["username"] = email
            
            # cur = mysql.connection.cursor()
            # cur.execute("SELECT last_updated FROM customer WHERE email = %s", (email,))
            # last_login = cur.fetchone()
            ''' if the date value stored at last_login is NOT today's date (eg if today is the 2nd Feb, and the last_login date value is the 1st)
             THEN execute this query -> cur.execute("""UPDATE customer set last_updated=CURRENT_TIMESTAMP WHERE email=%s""", (email,)) '''
            #cur.close()

            return redirect(url_for("customer_profile"))
            '''next_page = request.args.get("next")
            if not next_page:
                response = make_response( redirect( url_for('index')) )
            else:
                response = make_response( redirect(next_page) )
            response.set_cookie("username",username,max_age=(60*60*24*7))
            return response'''
    return render_template("customer/customer_login.html", form=form, title="Login")

# Login to staff account
@app.route("/staff_login", methods=["GET", "POST"])
def staff_login():
    cur = mysql.connection.cursor()
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data

        cur.execute("SELECT * FROM staff WHERE email = %s", (email,))
        staff = cur.fetchone()
        cur.close()

        if 'counter' not in session:
            session['counter'] = 0

        if staff is None:
            form.email.errors.append("Email doesn't exist, please check your spelling")
        elif not check_password_hash(staff["password"], password):
            form.password.errors.append("Incorrect password")
            session['counter'] = session.get('counter') + 1
            if session.get('counter')==3:
                flash(Markup('Oh no, are you having trouble logging in? Click <a href="forgot_password">here</a> to reset your password.'))
                session.pop('counter', None)
        else:
            session.clear()
            session["username"] = email
            if staff["access_level"] == "managerial":
                return redirect(url_for("manager"))
            elif staff["access_level"] == "ordinary staff":
                return redirect(url_for("staff_profile"))
                '''next_page = request.args.get("next")
                if not next_page:
                    response = make_response( redirect( url_for('index')) )
                else:
                    response = make_response( redirect(next_page) )
                response.set_cookie("username",username,max_age=(60*60*24*7))
                return response'''
    return render_template("staff/staff_login.html", form=form, title="Login")



# Contact form so that customers can send enquiries
@app.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    cur = mysql.connection.cursor()
    form = ContactForm()
    if form.validate_on_submit() == False:
      flash('All fields are required.')
    else:
        name = form.name.data
        email = form.email.data.lower().strip()
        subject = form.subject.data
        message = form.message.data

        cur.execute("""INSERT INTO user_queries (name, email, subject, message)
                        VALUES (%s,%s,%s,%s);""", (name, email, subject, message))
        mysql.connection.commit()
        cur.close()

        msg = Message(subject, sender='no.reply.please.and.thank.you@gmail.com', recipients=['no.reply.please.and.thank.you@gmail.com'])   
        msg.body = f"""
        From: {name} <{email}>
        {message}
        """
        mail.send(msg)
        flash("Message sent. We will reply to you in 2-3 business days.")
    return render_template("customer/enquiry_form.html",form=form, title="Contact Us")

# Change password
@app.route("/change_password/<table>", methods=["GET", "POST"])
#@login_required
def change_password(table):
    cur = mysql.connection.cursor()
    form = NewPasswordForm()
    if form.validate_on_submit():
        new_password = form.new_password.data

        if new_password.isupper() or new_password.islower() or new_password.isdigit():
            form.new_password.errors.append("Create a STRONG password with one uppercase character, one lowercase character and one number")
        else:
            if table == 'staff':
                cur.execute("""UPDATE staff SET password=%s WHERE email=%s;""", (generate_password_hash(new_password),g.user))
            else:
                cur.execute("""UPDATE customer SET password=%s WHERE email=%s;""", (generate_password_hash(new_password),g.user))
            mysql.connection.commit()
            session.clear()
            flash("Successfully changed password! Please login now.")
            cur.close()

            if table == 'staff':
                return redirect(url_for("staff_login"))
            else:
                return redirect(url_for("customer_login"))
    return render_template("password_management/change_password.html", title ="Change password", form=form)

# Reset password feature
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    cur = mysql.connection.cursor()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        table = form.role.data

        pin = sample(range(10000, 99999), 1)

        random_code = ""
        for i in pin:
            random_code += str(i)

        if table == 'staff':
            cur.execute("SELECT * FROM staff WHERE email = %s", (email,))
            user = cur.fetchone()
        else:
            cur.execute("SELECT * FROM customer WHERE email = %s", (email,))
            user = cur.fetchone()

        if user is None:
            form.email.errors.append("There is no account associated with this email, please check your spelling")
        else:
            msg = ""
            if table == 'staff':
                cur.execute("""UPDATE staff SET code=%s, last_updated=CURRENT_TIMESTAMP WHERE email=%s""", (random_code,email))
                mysql.connection.commit()
            else:
                cur.execute("""UPDATE customer SET code=%s, last_updated=CURRENT_TIMESTAMP WHERE email=%s""", (random_code,email))
                mysql.connection.commit()
            cur.close()

            msg = Message(f"Hello, {user['first_name']}", sender='no.reply.please.and.thank.you@gmail.com', recipients=[user["email"]])
            msg.body = f"""
            Hello,
            To reset your password, enter this code: 
            {random_code}"""
            mail.send(msg)
            flash("Great news! An email containing a 5 digit code has been sent to your email account. Enter the code below!")
            return redirect(url_for("confirm_code", email=email, table=table))
    return render_template("password_management/forgot_password.html", form=form, title= "Forgot Password")

# Checks whether the code the user received corresponds to the one in the database
@app.route("/confirm_code/<email>/<table>", methods=["GET", "POST"])
def confirm_code(email, table):
    form = CodeForm()
    if form.validate_on_submit():
        code = form.code.data.strip()

        cur = mysql.connection.cursor()

        if table == 'staff':
            cur.execute("SELECT code FROM staff WHERE email=%s;", (email,) )
            random_code = cur.fetchone()
        else:
            cur.execute("SELECT code FROM customer WHERE email=%s;", (email,) )
            random_code = cur.fetchone()
            
        cur.close()

        if code != random_code:
            form.code.errors.append("Oh no, that's not the code in your email!")
        else:
            flash("Code correct! Now you can reset your password :)")
            session["username"] = email
            return redirect(url_for("change_password", table=table))
    return render_template("password_management/confirm_code.html", form=form, title= "Confirm code")

@app.route('/kitchen', methods=['GET','POST'])
def kitchen():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT d.name, o.time, d.cook_time, o.tableNo, o.notes, o.status, o.dish_id
                    FROM orders as o 
                    JOIN dish as d 
                    ON o.dish_id=d.dish_id
                    ORDER BY o.notes='priority' DESC,
                            o.time,
                            o.time*d.cook_time DESC,
                            o.tableNo,  
                            d.cook_time DESC,
                            d.category='starter',
                            d.category='main',
                            d.category='side',
                            d.category='dessert';''')
    orderlist=cur.fetchall()

    return render_template('kitchen.html',orderlist=orderlist)

@app.route('/<int:dish_id>,<int:time>/kitchenUpdate', methods=['GET','POST'])

def kitchenUpdate(dish_id, time):
    cur = mysql.connection.cursor()
    cur.execute('''UPDATE orders
                                SET status="ongoing" 
                                WHERE time=%s and status="unmade" 
                                and dish_id=%s 
                                LIMIT 1;''',(time, dish_id))
    mysql.connection.commit()

    return redirect(url_for('kitchen'))

@app.route('/<int:dish_id>,<int:time>/kitchenDelete', methods=['GET','POST'])
def kitchenSentOut(dish_id, time):

    cur = mysql.connection.cursor()

    cur.execute('''UPDATE orders
                                SET status="sent out"
                                WHERE time=%s and status="ongoing" 
                                and dish_id =%s
                                LIMIT 1;''',(time, dish_id))
    mysql.connection.commit()

    return redirect(url_for('kitchen'))


##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
'''
            ALL FEATURES BELOW ARE RELATED TO THE STAFF
'''
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################

# Staff profile
@app.route("/staff_profile", methods=["GET", "POST"])
#@staff_only
def staff_profile():
    return render_template("staff/staff_profile.html", title="My Profile")

@app.route("/edit_staff_profile", methods=["GET", "POST"])
#@staff_only
def edit_staff_profile():
    form = ProfileForm()
    profile=None
    if form.validate_on_submit():
        bio = form.bio.data
        address = form.address.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        cur = mysql.connection.cursor()
        cur.execute("""UPDATE staff SET address=%s, bio=%s, first_name=%s, last_name=%s
                            WHERE email=%s;""", (address, bio, first_name, last_name, g.user))
        mysql.connection.commit()
        cur.close()
        flash ("successfully updated!")
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM staff WHERE email=%s;", (g.user,))
        profile = cur.fetchone()
        cur.close()
    return render_template("staff/edit_staff_profile.html", form=form, title="My Profile", profile=profile)

@app.route("/roster_request", methods=["GET", "POST"])
#@staff_only
def roster_request():
    cur = mysql.connection.cursor()
    form = RosterRequestForm()
    if form.validate_on_submit():
        message = form.message.data
        cur.execute("SELECT * FROM staff where email=%s", (g.user,))
        employee = cur.fetchone()
        employee = employee["first_name"] + " " + employee["last_name"]

        cur.execute("""INSERT INTO roster_requests (employee, message)
                            VALUES (%s,%s);""", (employee, message))
        mysql.connection.commit()
        cur.close()

        flash ("Request successfully sent!")
    return render_template("staff/roster_request.html", form=form,title="Roster Request")

##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
'''
            ALL FEATURES BELOW ARE RELATED TO THE MANAGER
'''
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
def get_random_password():
    random_char = string.ascii_letters + string.digits + string.punctuation
    password = random.choice(string.ascii_lowercase) 
    password += random.choice(string.ascii_lowercase) + random.choice(string.ascii_lowercase)
    password += random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase)
    password += random.choice(string.digits)
    password += random.choice(string.punctuation)

    for i in range(2):
        password += random.choice(random_char)

    password_list = list(password)
    # shuffle all characters to make it even more random
    random.SystemRandom().shuffle(password_list)
    password = ''.join(password_list)
    return password

# Manager account
#@manager_only
@app.route("/manager")
def manager():
    cur = mysql.connection.cursor()
    date = datetime.now().date()

    cur.execute("SELECT * FROM user_analytics")
    user_analytics = cur.fetchone()
    cur.execute("SELECT * FROM sales_analytics")
    sales_analytics = cur.fetchone()

    cur.execute("SELECT count(*) FROM user_queries where date(todays_date) = %s", (date,))
    query_count = cur.fetchone()

    cur.execute("SELECT * FROM roster_requests WHERE status = 'Pending'")
    pending_requests = cur.fetchall()

    cur.execute("SELECT * FROM roster_requests WHERE status = 'Approved' ORDER BY last_updated DESC")
    approved_requests = cur.fetchall()

    cur.execute("SELECT * FROM roster_requests WHERE status = 'Rejected' ORDER BY last_updated DESC")
    rejected_requests = cur.fetchall()

    cur.close()
    return render_template("manager/dashboard.html", rejected_requests=rejected_requests,approved_requests=approved_requests, pending_requests=pending_requests, user_analytics=user_analytics, sales_analytics=sales_analytics, query_count=query_count, title="Dashboard")

#@manager_only
@app.route("/roster_approve/<int:id>")
def roster_approve(id):
    cur = mysql.connection.cursor()
    print("the id is", id)
    status = "Approved"
    cur.execute("""UPDATE roster_requests SET status=%s, last_updated=CURRENT_TIMESTAMP WHERE request_id= %s;""", (status, id))
    mysql.connection.commit()
    flash("Approved")
    cur.close()
    return redirect(url_for("manager"))

#@manager_only
@app.route("/roster_reject/<int:id>", methods=["GET", "POST"])
def roster_reject(id):
    cur = mysql.connection.cursor()
    form = RejectRosterRequestForm()
    if form.validate_on_submit():
        response = form.response.data
        status = 'Rejected'
        cur.execute("""UPDATE roster_requests SET status=%s, response=%s, last_updated=CURRENT_TIMESTAMP WHERE request_id=%s;""", (status, response, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("manager"))
    return render_template("manager/roster_reject.html", form=form)

# View and manage all employees
#@manager_only
@app.route("/view_all_employees")
def view_all_employees():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM staff")
    employees = cur.fetchall()
    cur.close()
    return render_template("manager/employees.html", employees=employees, title="Employee Data")

# Add new employee
@app.route("/add_new_employee", methods=["GET", "POST"])
#@manager_only
def add_new_employee():
    cur = mysql.connection.cursor()
    form = EmployeeForm()
    print("after the form")
    if form.validate_on_submit():
        print("valid")
        role = form.role.data
        email = form.email.data
        access_level = form.access_level.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = get_random_password()
        
        cur.execute("""INSERT INTO staff (email, role, access_level, first_name, last_name, password, last_updated)
                            VALUES (%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP);""", (email, role, access_level, first_name, last_name, generate_password_hash(password)))
        mysql.connection.commit()
    
        # Notify employee's email about their new account
        message = "Please sign into your account with your email and password:" + password
        msg = Message("Welcome on board! We're happy you joined us.", sender='no.reply.please.and.thank.you@gmail.com', recipients=[email])   
        msg.body = f"""{message}"""
        mail.send(msg)
        
        flash ("New employee successfully added!")
        #cur.close()
        return redirect(url_for("view_all_employees"))
    return render_template("manager/add_new_staff.html", form=form, title="Add New Employee")   

# Remove existing employee
@app.route("/remove_employee/<int:id>")
#@manager_only
def remove_employee(id):
    cur = mysql.connection.cursor()
    cur.execute("""DELETE FROM staff WHERE staff_id=%s""", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("view_all_employees"))  

# View queries from users
#@manager_only
@app.route("/view_query")
def view_query():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_queries")
    queries = cur.fetchall()
    cur.close()
    return render_template("manager/queries.html", queries=queries)

# Delete queries from users
#@manager_only
@app.route("/delete_query/<int:id>")
def delete_query(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user_queries WHERE query_id=%s", (id,))
    cur.fetchone()
    mysql.connection.commit()
    flash ("Deleted!")
    cur.close()
    return redirect(url_for("view_query"))

# Manager can reply to user queries
#@manager_only
@app.route("/reply_email/<id>", methods=["GET", "POST"])
def reply_email(id):
    cur = mysql.connection.cursor()
    form = ReplyForm()
    cur.execute("SELECT * FROM user_queries WHERE query_id=%s", (id,))
    query = cur.fetchone()

    if form.validate_on_submit() == False:
        flash('All fields are required.')
    else:
        email = form.email.data
        subject = form.subject.data
        message = form.message.data

        msg = Message("Replying to your query: "+subject, sender='no.reply.please.and.thank.you@gmail.com', recipients=[email])   
        msg.body = f"""{message}"""
        mail.send(msg)
        flash("Message sent successfully.")
        cur.close()
    return render_template("manager/reply_email.html",form=form, title="Reply", query=query)

# Delete queries from users
#@manager_only
@app.route("/view_inventory")
def view_inventory():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ingredient;")
    inventory = cur.fetchall()
    cur.close()
    return render_template("manager/inventory.html", inventory=inventory, title="Inventory List")


#initally i'm gonna just get all dishes to display but i do want to be able to separate it into like starter, main course etc
@app.route('/menu',methods=['GET'])
def menu():
    cur=mysql.connection.cursor()
    cur.execute('''SELECT * FROM dish ORDERBY; ''')
    dishes =cur.fetchall()
    #want to order this so that we display by dishtype
    cur.execute(" SELECT * FROM dish WHERE dishType='starter' ")
    starters =cur.fetchall()
    cur.execute(" SELECT * FROM dish WHERE dishType='main' ")
    mainCourse = cur.fetchall()
    cur.execute(" SELECT * FROM dish WHERE dishType='dessert' ")
    dessert= cur.fetchall()
    cur.execute(" SELECT * FROM dish WHERE dishType='drink'")
    drink= cur.fetchall()
    cur.execute(" SELECT * FROM dish WHERE dishType='side'")
    side = cur.fetchall()
    cur.close()#
    print(g.user)
    return render_template('customer/dishes.html', dishes=dishes, starters=starters, mainCourse=mainCourse,dessert=dessert, drink=drink,side=side)




@app.route('/dish/<int:dish_id>', methods=['GET','POST'])
def dish(dish_id):
    if str(dish_id) not in session:
        session[str(dish_id)]={}
        print(session[str(dish_id)])
    session['CurrentDish'] = dish_id
    print(session[str(dish_id)])
    form = submitModifications()
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM dish WHERE dish_id=%s',(dish_id,))
    dish=cur.fetchone()
    dish_id=dish['dish_id']
    cur.execute("SELECT * FROM dish_ingredient JOIN ingredient ON dish_ingredient.ingredient_id = ingredient.ingredient_id  WHERE dish_ingredient.dish_id=%s",(dish_id,))
    result=cur.fetchall()
    print(result)
    for value in result:
        ingredient_id=value['ingredient_id']
        print('INGREDIENTID ', ingredient_id)
        if ingredient_id not in session[str(dish_id)]:
            session[str(dish_id)][ingredient_id] =1
            print('todo')
            print(session[str(dish_id)][ingredient_id])
    if form.validate_on_submit():
        changes = ''
        cur.execute('SELECT * FROM dish_ingredient WHERE dish_id=%s',(dish_id,))
        ingredients=cur.fetchall()
        for ingredient in ingredients:
            print(ingredient)
            ingredient_id = ingredient['ingredient_id']
            cur.execute("SELECT * FROM ingredient WHERE ingredient_id=%s",(ingredient_id,))
            ing_name=cur.fetchone()['name']
            #ingredient_name = ingredient['name']
            if ingredient_id not in session[str(dish_id)]:
                session[str(dish_id)][ingredient_id] =1
                print(session[dish_id])
            else:
                quantity=session[str(dish_id)][ingredient_id]
                changes+= str(ing_name) + str(quantity)
                print('changes1:',changes)
                session[str(dish_id)][ingredient_id] =1
        cur.execute("INSERT INTO modifications(dish_id,changes,user) VALUES(%s,%s,%s)",(dish_id,changes,g.user))
        mysql.connection.commit()
        session['CurrentDish'] = None
        return redirect(url_for('add_to_cart', dish_id=dish['dish_id']))
    return render_template('customer/dish.html', dish=dish,result=result,form=form,quant=session[str(dish_id)])

#so by default all amounts of ingredients should be 1 - should have the option to increase by 1 and decrease by 1
#added that so that should work
# I'M PRETTY SURE THIS WORKS BESIDES THE REDIRECT  
@app.route('/inc_quantity_ingredient/<int:ingredient_id>')
@login_required
def inc_quantity_ingredient(ingredient_id):
    cur = mysql.connection.cursor() 
    dish_id = session['CurrentDish']
    cur.execute("SELECT * FROM dish_ingredient WHERE ingredient_id=%s",(ingredient_id,))
    result=cur.fetchone()
    #dish_id = result['dish_id']
    if ingredient_id not in session[str(dish_id)]:
        session[str(dish_id)][ingredient_id] = 1
    session[str(dish_id)][ingredient_id] = session[str(dish_id)][ingredient_id] +1
    print(session[str(dish_id)][ingredient_id])
    return redirect(url_for('dish',dish_id=dish_id))

@app.route('/dec_quantity_ingredient/<int:ingredient_id>')
@login_required
def dec_quantity_ingredient(ingredient_id):
    cur = mysql.connection.cursor()
    dish_id = session['CurrentDish']
    cur.execute("SELECT * FROM dish_ingredient WHERE ingredient_id=%s",(ingredient_id,))
    result=cur.fetchone()
    #dish_id = result['dish_id']
    if ingredient_id not in session[str(dish_id)]:
        session[str(dish_id)][ingredient_id] = 1
    if session[str(dish_id)][ingredient_id] !=0:
        session[str(dish_id)][ingredient_id] = session[str(dish_id)][ingredient_id] -1
    return redirect(url_for('dish',dish_id=dish_id))


#manager only
#should add instead of a text box for dishtype like a drop down with only a couple of options
#NEED TO ADD ABILITY TO LIST INGREDIENTS NECESSARY FOR EACH DISH.
@app.route('/addDish', methods=['GET','POST'])
def addDish():
    cur = mysql.connection.cursor()
    form = AddDishForm()
    if form.validate_on_submit():
        name = form.name.data
        cur.execute('SELECT * from dish WHERE name=%s',(name,))
        result = cur.fetchone()
        if result is not None:
            form.name.errors.append("This dish is already in the db")
        else:
            cost = form.cost.data
            cookTime = form.cookTime.data
            dishType = (form.dishType.data).lower()
            dishDescription = form.dishDescription.data
            dishPic = form.dishPic.data
            ingredients = form.ingredients.data
            allergins= form.allergins.data
            filename = secure_filename(dishPic.filename)
            #print(filename)
            dishPic.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            cur.execute("INSERT INTO dish (name, cost, cook_time, dishType, description,dishPic,allergies) VALUES(%s,%s,%s,%s,%s,%s,%s);", (name,cost,cookTime,dishType,dishDescription,filename,allergins))
            mysql.connection.commit()
            print(ingredients)
            if ingredients is not None:
                ingredients=ingredients.split(',')
                for ingredient in ingredients:
                    print(ingredient)
                    cur.execute("SELECT * FROM ingredient WHERE name=%s",(ingredient,))
                    ingredient_id=cur.fetchone()
                    if ingredient_id is not None:
                        print('hellor', ingredient_id)
                        ingredient_id=ingredient_id['ingredient_id']
                        cur.execute('SELECT * FROM dish WHERE name=%s AND cost=%s AND cook_time=%s',(name, cost, cookTime))
                        dish_id=cur.fetchone()['dish_id']
                        cur.execute("INSERT INTO dish_ingredient(ingredient_id,dish_id) VALUES (%s,%s)",(ingredient_id,dish_id))
                        mysql.connection.commit()
                    else:
                        cur.execute('SELECT * FROM dish WHERE name=%s AND cost=%s AND cook_time=%s',(name, cost, cookTime))
                        dish_id=cur.fetchone()['dish_id']
                        cur.execute("INSERT INTO ingredient(name,quantity) VALUES (%s,%s)",(ingredient,0))
                        mysql.connection.commit()
                        cur.execute("SELECT * FROM ingredient WHERE name=%s",(ingredient,))
                        ingredient_id=cur.fetchone()['ingredient_id']
                        cur.execute("INSERT INTO dish_ingredient(ingredient_id,dish_id) VALUES (%s,%s)",(ingredient_id,dish_id))
                        mysql.connection.commit()
            #cur.close()
            return redirect(url_for('menu'))
    return render_template('manager/addDish.html', form=form)

#this was not working yesterday so I don't get why its working today

@app.route('/cart')
@login_required
def cart():
    #session['cart'].clear()
    cur = mysql.connection.cursor()
    dish=''
    full = 0
    if 'cart' not in session:
        session['cart'] = {}
        print('create session')
    names = {}
    print(session['cart'])
    for dish_id in session['cart']:
        print('heeloor',dish_id)
        cur.execute('SELECT * FROM dish WHERE dish_id=%s LIMIT 1;',(dish_id,))
        name = cur.fetchone()['name']
        print(name)
        names[dish_id] = name
        cur.execute(' SELECT * FROM dish WHERE dish_id=%s; ',(dish_id,))
        dish = cur.fetchone()
        cur.execute(' SELECT * FROM dish WHERE dish_id=%s',(dish_id,))
        cost = cur.fetchone()['cost']
        quantity = session['cart'][dish_id]
        full+= (int(cost) *int(quantity))
        #cur.close()
    return render_template('customer/cart.html', cart=session['cart'], names=names, dish=dish, full=full)

@app.route('/add_default_meal/<int:dish_id>')
@login_required
def add_default_meal(dish_id):
    cur = mysql.connection.cursor()
    if 'cart' not in session:
        session['cart'] = {}
    if dish_id not in session['cart']:
        session['cart'][dish_id] = 0
    session['cart'][dish_id]=session['cart'][dish_id]+1
    changes=""
    cur.execute("INSERT INTO modifications(dish_id,changes,user) VALUES(%s,%s,%s)",(dish_id,changes,g.user))
    mysql.connection.commit()

    return redirect(url_for('cart'))


#There's an issue here 
@app.route('/add_to_cart/<int:dish_id>')
@login_required
def add_to_cart(dish_id):
    #session['cart'].clear()
    cur = mysql.connection.cursor()
    if 'cart' not in session:
        session['cart'] = {} 
    if dish_id not in session['cart']:
        session['cart'][dish_id] = 0
    session['cart'][dish_id]= session['cart'][dish_id] + 1
    return redirect( url_for('cart') ) 

@app.route('/remove/<int:dish_id>')
@login_required
def remove(dish_id):
    if dish_id not in session['cart']:
        session['cart'][dish_id] = 0
    for dishId in session['cart'].copy():
        if dish_id == int(dishId):
            session['cart'].pop(dishId)
    return redirect(url_for('cart'))

@app.route('/inc_quantity/<int:dish_id>')
@login_required
def inc_quantity(dish_id):
    cur = mysql.connection.cursor()
    #stock_left = db.execute(''' SELECT * FROM inventory WHERE book_id=?; ''',(book_id,)).fetchone()['stock_left']
    if dish_id not in session['cart']:
        session['cart'][dish_id]=0
    #if session['cart'][book_id] < stock_left:
    session['cart'][dish_id] = session['cart'][dish_id] +1
    return redirect(url_for('cart'))

@app.route('/dec_quantity/<int:dish_id>')
@login_required
def dec_quantity(dish_id):
    if dish_id not in session['cart']:
        session['cart'][dish_id]=0
    if session['cart'][dish_id] >1:
        session['cart'][dish_id] = session['cart'][dish_id] -1
    return redirect(url_for('cart'))


#question does this need to be specific to user?? or is it already
@app.route('/checkout', methods=['GET','POST'])
def checkout():
    full =0
    form = cardDetails()
    names = {}
    username = g.user
    cur = mysql.connection.cursor()
    for dish_id in session['cart']:
        cur.execute('SELECT * FROM dish WHERE dish_id=%s;',(dish_id,))
        name = cur.fetchone()['name']
        names[dish_id] = name
        cur.execute("SELECT * FROM dish WHERE dish_id=%s",(dish_id,))
        cost = cur.fetchone()['cost']
        cur.execute(' SELECT * FROM dish WHERE dish_id=%s;',(dish_id,))
        dish = cur.fetchone()
        quantity = session['cart'][dish_id]
        full += (cost *quantity)
        cur.execute('SELECT * FROM dish_ingredient WHERE dish_id=%s',(dish_id,))
        ingredients=cur.fetchall()
        changes=''
        print('session',session['cart'])
    if form.validate_on_submit():
        cardNum=form.cardNum.data
        cardHolder = form.cardHolder.data
        cvv = form.cvv.data
        date = datetime.now().strftime(' %d-%m-%y')
        now = datetime.now()
        for dish_id in session['cart']:
            cur.execute('SELECT * FROM modifications WHERE dish_id=%s AND user=%s',(dish_id,g.user))
            result = cur.fetchall()
            print('Result:',result)
            for values in result:
                print('myval',values)
                cur.execute('SELECT * FROM dish WHERE dish_id=%s',(dish_id,))
                currentDish=cur.fetchone()
                print('cd',currentDish)
                cost=currentDish['cost']
                changes=values['changes']
                cur.execute('INSERT INTO transactions(username, dish_id,cost,quantity,date) VALUES(%s,%s,%s,%s,%s) ',(username, dish_id,cost,1,date))
                mysql.connection.commit()
                cur.execute("INSERT INTO orders(time,dish_id,changes) VALUES(%s,%s,%s)",(now,dish_id,changes))
                mysql.connection.commit()
            #cur.execute('DELETE FROM modifications WHERE user=%s',(g.user,))
        cur.execute('DELETE FROM modifications WHERE user=%s',(g.user,))
        mysql.connection.commit()    
        session['cart'].clear()
        cur.close()
        return render_template('cart.html')
    return render_template('customer/checkout.html', cart=session['cart'],form=form,full=full,names=names,dish=dish)

    #need table number to be inputed here 


@app.route('/customer_profile')
@login_required
def customer_profile():
    username = session['username']
    cur = mysql.connection.cursor()
    message = ''
    transactionHistory=''
    image = None
    cur.execute(" SELECT * FROM customer WHERE email=%s",(username,))
    check= cur.fetchone()['profile_pic']
    print(check)
    if check is None:
        error = 'No profile picture yet'
        print('why')
    else:  
        image=check
        print(image)
    cur.execute("SELECT * FROM transactions WHERE username=%s;",(username,))
    check2 = cur.fetchall()
    if check2 is not None:
        message = "You've made no transactions yet"
    else:
        cur.execute(" SELECT * FROM dishes;")
        dish = cur.fetchall()
        cur.execute(" SELECT * FROM transactions WHERE username=%s ",(username,))
        transactionHistory = cur.fetchall()
    cur.close()
    #return render_template("customer/profile.html", title="My Profile")
    return render_template('customer/customer_profile.html',image=image, transactionHistory=transactionHistory)


@app.route('/user_pic', methods=['GET','POST'])
@login_required
def user_pic():
    username = session['username']
    cur = mysql.connection.cursor()
    form = UserPic()
    if form.validate_on_submit():
        profile_pic = form.profile_pic.data
        filename = secure_filename(profile_pic.filename)
        profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cur.execute(' UPDATE customer SET profile_pic=%s WHERE email=%s; ' ,(filename,username))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('customer_profile'))
    return render_template('customer/profile_pic.html', form=form)


#gonna implement this pretending 
@app.route('/breaks', methods=['GET','POST'])
def breakTimes():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM staff')
    staff = cur.fetchall()
    cur.execute("SELECT * FROM roster")
    roster = cur.fetchall()
    now = datetime.datetime.now()
    day = (now.strftime("%a")).lower()
    breaksAssigned = {}
    workingToday = {}
    for working in roster:
        if working[day] != '':
            shift = working[day]
            workingToday[working['staff_id']] =shift
    print('hello')
    print(workingToday)
    numWorkers = len(workingToday)
    for employee in workingToday:
        shift = workingToday[employee]
        print(shift)
        hoursWorking= int(shift[0]+shift[1]) - int(shift[6]+shift[7])
        if hoursWorking <0:
            hoursWorking = hoursWorking*-1
            workingToday[employee] = [shift,hoursWorking]
        if hoursWorking >4 and hoursWorking >= 8:
            breaks = 2
            #want to do my little test here
            #2 breaks needed
        elif hoursWorking >4:
            breaks=1
            #1 break needed
        else: 
            breaks =0
        start = int(shift[0]+shift[1])
        endShift = int(shift[6] + shift[7])
        for i in range(0,breaks):
            print(i)
            proposedBreak = 0
            #start =None
            for j in range(4,1,-1):
                print()
                print('start',start)
                proposedBreak = start + j
                if proposedBreak in breaksAssigned: 
                    proposedBreak = 0
                elif proposedBreak  >= endShift or (proposedBreak) == endShift -2:
                    proposedBreak =0
                else:
                    breaksAssigned[proposedBreak] =1
                    if i == 0:
                        start = start +j
                        endBreak = start +0.45
                        workingToday[employee].append(start)
                    elif i ==1:
                        start = start + j
                        endBreak =start+0.45
                        workingToday[employee].append(start)
                    break
            #if breaksAssigned[proposedBreak] <=
            #end = start +.45
            #print(start)
            #no break
        print("shiftLength",hoursWorking) 
    return ("breaks.html")




if __name__ == '__main__':
    app.run(debug=True)




