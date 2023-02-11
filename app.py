from flask import Flask, render_template, redirect, url_for, session, g, request, make_response, flash, Markup
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, ContactForm, ReplyForm, EmployeeForm, ResetPasswordForm, NewPasswordForm, CodeForm, TableForm, AddToRosterForm, RosterRequestForm, RosterRequirementsForm, ProfileForm, RejectRosterRequestForm, submitModifications
from functools import wraps
from flask_mysqldb import MySQL 
from generate_roster import Roster
import json
from flask_mail import Mail, Message
from datetime import datetime
import random, string, time
from random import sample

app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"

app.config["SESSION_PERMANENT"] = False
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

app.config['MYSQL_USER'] = 'root' # someone's deets
app.config['MYSQL_PASSWORD'] = 'PaZARIX9' # someone's deets
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_DB'] = 'sys' # someone's deets
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
            SELECT dish.name, orders.status, order_id, dish.dishType, orders.info
            FROM orders JOIN dish 
            ON orders.dish_id = dish.dish_id
            WHERE orders.table_id = %s 
            AND orders.status != %s
            AND orders.status != %s
        """,(table,'complete', 'cancelled')
    )
    ordered = cur.fetchall()
    if 'ordering' not in session:
        session['ordering'] = {}
    if table in session['ordering']:
        ordering = session['ordering'][table]
        return render_template("staff/take_order.html", table=table, ordering=ordering, meals=meals, ordered=ordered)
    return render_template("staff/take_order.html", table=table, meals=meals, ordered=ordered)

@app.route('/<int:table>/waiter_customize_dish/<int:dish_id>', methods=['GET','POST'])
def waiter_customize_dish(table, dish_id):
    if str(dish_id) not in session:
        session[str(dish_id)]={}
    session['CurrentDish'] = dish_id
    form = submitModifications()
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM dish WHERE dish_id=%s',(dish_id,))
    dish=cur.fetchone()
    cur.execute("SELECT * FROM dish_ingredient JOIN ingredient ON dish_ingredient.ingredient_id = ingredient.ingredient_id  WHERE dish_ingredient.dish_id=%s",(dish_id,))
    result=cur.fetchall()
    for value in result:
        ingredient_id=value['ingredient_id']
        if ingredient_id not in session[str(dish_id)]:
            session[str(dish_id)][ingredient_id] =1
            
    if form.validate_on_submit():
        cur.execute('SELECT * FROM dish_ingredient WHERE dish_id=%s',(dish_id,))
        ingredients=cur.fetchall()
        if 'mods' not in session:
            session['mods'] = {}
        if table not in session['mods']:
            session['mods'][table] = {}
        cur.execute('SELECT ingredient_id FROM dish_ingredient WHERE dish_id = %s',(dish_id,))
        ingredient_ids = cur.fetchall()
        
        min = 100
        for id in ingredient_ids:
            cur.execute('SELECT MIN(quantity) FROM ingredient WHERE ingredient_id = %s',(id['ingredient_id'],))
            value = cur.fetchone()
            if value['MIN(quantity)'] < min:
                min = value['MIN(quantity)']
        if min > 0:
            for ingredient in ingredients:
                ingredient_id = ingredient['ingredient_id']
                if ingredient_id not in session[str(dish_id)]:
                    session[str(dish_id)][ingredient_id] =1
                    
            
            session['mods'][table][dish['name']] = {}
            for value in result:
                session['mods'][table][dish['name']][value['name']] = session[str(dish_id)][value['ingredient_id']]
            for ingredient in ingredients:
                session[str(dish_id)][ingredient['ingredient_id']] = 1
            session['CurrentDish'] = None
            return redirect(url_for('add_order', table=table, meal=dish['name']))
    return render_template('staff/customize_dish.html', table=table, dish=dish,result=result,form=form,quant=session[str(dish_id)])

@app.route('/<int:table>/waiter_inc_quantity_ingredient/<int:ingredient_id>')
#@login_required
def waiter_inc_quantity_ingredient(table, ingredient_id):
    dish_id = session['CurrentDish'] # put this as input
    if ingredient_id not in session[str(dish_id)]:
        session[str(dish_id)][ingredient_id] = 1
    session[str(dish_id)][ingredient_id] = session[str(dish_id)][ingredient_id] +1
    return redirect(url_for('waiter_customize_dish', table=table, dish_id=dish_id))

@app.route('/<int:table>/waiter_dec_quantity_ingredient/<int:ingredient_id>')
#@login_required
def waiter_dec_quantity_ingredient(table, ingredient_id):
    dish_id = session['CurrentDish']
    if ingredient_id not in session[str(dish_id)]:
        session[str(dish_id)][ingredient_id] = 1
    if session[str(dish_id)][ingredient_id] !=0:
        session[str(dish_id)][ingredient_id] = session[str(dish_id)][ingredient_id] -1
    return redirect(url_for('waiter_customize_dish',table=table, dish_id=dish_id))


@app.route("/<int:table>/add_order/<meal>", methods=["GET","POST"])
def add_order(table, meal):
    if 'mods' not in session:
        session['mods'] = {}
    if 'ordering' not in session:
        session['ordering'] = {}
    if table not in session['ordering']:
        session['ordering'][table] = {}
    cur = mysql.connection.cursor()

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
        mods = {}
        if table in session['mods']:
            if session['mods'][table] != {}:
                for key in session['mods'][table]:
                    mods = session['mods'][table][key]
            
        if str(meal) in session['ordering'][table]:
            session['ordering'][table][str(meal)].append(mods)
        else:
            session['ordering'][table][str(meal)] = [mods]
            
        session['mods'][table] = {}
    return redirect(url_for('take_order', table=table))

# do after maybe index
@app.route("/<int:table>/remove_meal/<meal>/<int:index>", methods=["GET","POST"])
def remove_meal(table, meal, index):
    session['ordering'][table][meal].pop(index)
    if len(session['ordering'][table][meal]) == 0:
        session['ordering'][table].pop(meal)
    return redirect(url_for("take_order", table=table))

@app.route("/<int:table>/cancel_meal/<int:meal_id>", methods=["GET","POST"])
def cancel_meal(table, meal_id):
    
    cur = mysql.connection.cursor()
     
    cur.execute("DELETE FROM orders WHERE order_id = %s AND table_id = %s;",(meal_id, table ))
    mysql.connection.commit()
    
    return redirect(url_for("take_order", table=table))

@app.route("/<int:table>/cancel_order", methods=["GET","POST"])
def cancel_order(table):
    session['mods'][table] = {}
    session['ordering'][table] = {}
    return redirect(url_for("take_order", table=table))


@app.route("/<int:table>/complete_order", methods=["GET","POST"])
def complete_order(table):  
    cur = mysql.connection.cursor()
        
    if table in session['ordering']:
        ordering = session['ordering'][table]
        print(ordering)
        for meal in ordering:
            cur.execute('SELECT dish_id, cook_time FROM dish WHERE name = %s',(meal,))
            data = cur.fetchone()
            for times in ordering[meal]:
                info = ""
                for ingredients in times:
                    if times[ingredients] != 1:
                        info += ingredients+"-"+str(times[ingredients])+", "
                cur.execute("INSERT INTO orders (time, dish_id, table_id, status, info) VALUES (%s, %s, %s, 'waiting', %s);",(data['cook_time'], data['dish_id'], table, info))
                mysql.connection.commit()
    
    session['ordering'][table] = {}
    return redirect(url_for('take_order', table=table))

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

@app.route("/manage_shift_requirements", methods=["GET","POST"])
def manage_shift_requirements():
    form = RosterRequirementsForm()
    week = {'mon':'Monday','tue':'Tuesday','wed':'Wednesday','thu':'Thursday','fri':'Friday','sat':'Saturday','sun':'Sunday'}
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM shift_requirements;")
    requirements = cur.fetchall()
    for requirement in requirements:
        requirement['unavailable'] = json.loads(requirement['unavailable'])
    cur.execute("SELECT staff_id, first_name FROM staff;")
    staff = cur.fetchall()
    
    if form.validate_on_submit():
        day = form.day.data
        opening_time = form.opening_time.data
        closing_time = form.closing_time.data
        min_workers = form.min_workers.data
        
        if form.unavailable.data is None or form.unavailable.data == '':
            for requirement in requirements:
                if requirement['day'] == day:
                    unavailable = requirement['unavailable']
        else:
            unavailable = form.unavailable.data
            try:
                unavailable = unavailable.split(" ")
                for i in range(len(unavailable)):
                    unavailable[i] = int(unavailable[i])
                unavailable = json.dumps(unavailable)
            except TypeError:
                form.unavailable.errors.append("Values should be space separated ID's")
                unavailable = '[]'
        cur.execute("""UPDATE shift_requirements SET opening_time = %s, closing_time = %s, min_workers = %s, unavailable = %s
                        WHERE day = %s;""", ( opening_time, closing_time, min_workers, unavailable, day))
        mysql.connection.commit()
        cur.execute("SELECT * FROM shift_requirements;")
        requirements = cur.fetchall()
        for requirement in requirements:
            requirement['unavailable'] = json.loads(requirement['unavailable'])
    else:
        form.opening_time.data = requirements[0]['opening_time']
        form.closing_time.data = requirements[0]['closing_time']
        form.min_workers.data = requirements[0]['min_workers']
    
    return render_template("manager/shift_requirements.html", requirements=requirements, staff=staff, week=week, form=form)

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
    result = roster.generate(requirements, employees)
    cur.execute("UPDATE roster SET mon = '', tue = '', wed = '', thu = '', fri = '', sat = '', sun = '';")
    mysql.connection.commit()
    for day in result:
        for shift in result[day]:
            for person in result[day][shift]:
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

# Customer profile
@app.route("/customer_profile")
@login_required
def customer_profile():
    #cur = mysql.connection.cursor()
    #cur.execute("SELECT * FROM customer WHERE email = %s", (g.user,))
    #user = cur.fetchone()
    return render_template("customer/profile.html", title="My Profile")#, user=user)

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
    if form.validate_on_submit():
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

if __name__ == '__main__':
    app.run(debug=True)
