from flask import Flask, render_template, redirect, url_for, session, g, request, make_response, flash, Markup
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, ContactForm, ReplyForm, EmployeeForm, ResetPasswordForm, NewPasswordForm, CodeForm, TableForm, AddToRosterForm, RosterRequestForm, RosterRequirementsForm, ProfileForm, RejectRosterRequestForm, submitModifications, AddDishForm, UserPic, cardDetails, Review, makeBooking, StockForm, Supplier, EditSupplier
from functools import wraps
from flask_mysqldb import MySQL 
from generate_roster import Roster
import json
from flask_mail import Mail, Message
import datetime
from datetime import datetime #
import random, string, time
from random import sample
from werkzeug.utils import secure_filename
import os
import credentials
import time

from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)


app.config["SECRET_KEY"] = "MY_SECRET_KEY"
UPLOAD_FOLDER = "static/picture"
app.config['DEBUG'] = False
app.config["SESSION_PERMANENT"] = False
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# For the email function
mail= Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = credentials.flask_email
app.config['MAIL_PASSWORD'] = credentials.flask_email_password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail.init_app(app)

app.config['MYSQL_USER'] = credentials.user
app.config['MYSQL_PASSWORD'] = credentials.password
app.config['MYSQL_HOST'] = credentials.host
app.config['MYSQL_DB'] = credentials.db
app.config['MYSQL_CURSORCLASS']= 'DictCursor'
app.config['MYSQL_CURSORCLASS']= 'DictCursor'

mysql = MySQL(app)

def get_personal_notifs():
    cur = mysql.connection.cursor()
    notifications = cur.execute("SELECT * FROM notifications WHERE user = %s", (g.user,))
    notifications =  cur.fetchall()
    cur.close()
    return notifications

def get_managerial_notifs():
    cur = mysql.connection.cursor()
    notifications = cur.execute("SELECT * FROM notifications WHERE user = 'manager'")
    notifications = cur.fetchall()
    cur.close()
    return notifications

def get_staff_notifs():
    cur = mysql.connection.cursor()
    notifications = cur.execute("SELECT * FROM notifications WHERE user = 'staff'")
    notifications = cur.fetchall()
    cur.close()
    return notifications

@app.before_request
def logged_in():
    g.user = session.get("username", None)
    g.access = session.get("access_level", None)
    g.notifications_personal = get_personal_notifs()
    g.notifications_managerial = get_managerial_notifs()
    g.notifications_staff = get_staff_notifs()

def all_logged_in_users(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Please login to access this feature")
            return redirect( url_for("customer_login"))
        return view(**kwargs)
    return wrapped_view

def customer_only(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.access != "customer":
            return render_template("error.html"), 404
        return view(**kwargs)
    return wrapped_view

def business_only(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.access != "ordinary staff" and g.access != "managerial":
            return render_template("error.html"), 404
        return view(**kwargs)
    return wrapped_view


def staff_only(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.access != "ordinary staff":
            return render_template("error.html"), 404
        return view(**kwargs)
    return wrapped_view

def manager_only(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.access != "managerial":
            return render_template("error.html"), 404
        return view(**kwargs)
    return wrapped_view

@app.route("/logout", methods=["GET","POST"])
def logout():
    session.clear()
    return redirect(url_for("menu"))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html"), 404

@app.route("/", methods=["GET","POST"])
def index():
    if g.access is None:
        flash("Please login to access this feature")
        return redirect( url_for("customer_login"))
    if g.access == "managerial":
        return redirect( url_for("manager"))
    if g.access == "ordinary staff":
        return redirect( url_for("choose_table"))
    if g.access == "customer":
        return redirect( url_for("customer_profile"))

##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
'''
            CUSTOMER SUPPORT FEATURE
'''
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################

# Contact form so that customers can send enquiries
@app.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    form = ContactForm()
    if form.validate_on_submit() == False:
      flash('All fields are required.')
    else:
        cur = mysql.connection.cursor()
        name = form.name.data
        email = form.email.data.lower().strip()
        subject = form.subject.data
        message = form.message.data

        cur.execute("""INSERT INTO user_queries (name, email, subject, message)
                        VALUES (%s,%s,%s,%s);""", (name, email, subject, message))
        mysql.connection.commit()

        cur.execute("""INSERT INTO notifications (user, title, message)
                    VALUES ("manager", "New Customer Enquiry","Enquiry regarding '%s'");""", (subject,))
        mysql.connection.commit()
        cur.close()
        
        msg = Message(subject, sender=credentials.flask_email, recipients=[credentials.flask_email])   
        msg.body = f"""
        From: {name} <{email}>
        {message}
        """
        mail.send(msg)
        flash("Message sent. We will reply to you in 2-3 business days.")
    return render_template("customer/enquiry_form.html",form=form, title="Contact Us")

##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
'''
            NOTIFICATION FEATURE
'''
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################

# clears all notifications
@app.route("/clear_all_notifications", methods=["POST"])
def clear_all_notifications():
    current_url = request.form['current_url']

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM notifications WHERE user = %s", (g.user,))
    mysql.connection.commit()

    if g.access == "managerial":
        cur.execute('DELETE FROM notifications WHERE user = "manager" ')
        mysql.connection.commit()

    cur.close()
    return redirect(current_url)

# clears one notification
@app.route("/clear_one_notification/<int:id>", methods=["POST"])
def clear_one_notification(id):
    current_url = request.form['current_url']

    cur = mysql.connection.cursor()
    notifications = cur.execute("DELETE FROM notifications WHERE notif_id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(current_url)

##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
'''
            ALL FEATURES BELOW ARE RELATED TO ACCOUNT REGISTRATION/LOGIN, AND PASSWORD MANAGEMENT
'''
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
# Register for an account
@app.route("/registration", methods=["GET", "POST"])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        email = form.email.data.strip().lower()
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        code = "None"

        '''
            Only customers can create new accounts
            New staff accounts will be created by the manager and the password
            will be autogenerated by an algorithm, and then sent 
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
        
        if 'counter' not in session:
            session['counter'] = 0

        if customer is None:
            form.email.errors.append("Email or password is incorrect")
        elif not check_password_hash(customer["password"], password):
            form.password.errors.append("Incorrect password")
            session['counter'] = session.get('counter') + 1
            if session.get('counter')==3:
                flash(Markup('Oh no, are you having trouble logging in? Click <a href="forgot_password">here</a> to reset your password.')) # reset password link need to go here
            if session.get('counter')==5:
                msg = Message(f"Various Login Attempts For Your Michelin Star Account", sender=credentials.flask_email, recipients=[email])
                msg.body = f"""
                Hello,
                There has been an abnormal number of attempts of logins to your account.
                If it wasn't you, please take action to reset your password now."""
                mail.send(msg)
                session.pop('counter', None)
        else:
            session.clear()
            session["username"] = email
            session["access_level"] = "customer"
            
            ''' if the date value stored at last_login is NOT today's date (eg if today is the 2nd Feb, and the last_login date value is the 1st)
             THEN execute this query ->  '''
            cur.execute("""UPDATE customer set last_updated=CURRENT_TIMESTAMP WHERE email=%s""", (email,))
            cur.close()

            return redirect(url_for("customer_profile"))
        cur.close()
    return render_template("customer/customer_login.html", form=form, title="Login")

# Login to staff account
@app.route("/staff_login", methods=["GET", "POST"])
def staff_login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM staff WHERE email = %s", (email,))
        staff = cur.fetchone()
        cur.close()

        if 'counter' not in session:
            session['counter'] = 0

        if staff is None:
            form.email.errors.append("Email or password is incorrect")
        elif not check_password_hash(staff["password"], password):
            form.password.errors.append("Incorrect password")
            session['counter'] = session.get('counter') + 1
            if session.get('counter')==3:
                flash(Markup('Oh no, are you having trouble logging in? Click <a href="forgot_password">HERE</a> to reset your password.'))
                session.pop('counter', None)
        else:
            session.clear()
            session["username"] = email
            if staff["access_level"] == "managerial":
                session["access_level"] = "managerial"
                session['expiry_check_executed'] = False
                return redirect(url_for("manager"))
            elif staff["access_level"] == "ordinary staff":
                session["access_level"] = "ordinary staff"
                return redirect(url_for("staff_profile"))
    return render_template("staff/staff_login.html", form=form, title="Login")

# Change password
@app.route("/change_password/<table>", methods=["GET", "POST"])
def change_password(table):
    form = NewPasswordForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        new_password = form.new_password.data

        if new_password.isupper() or new_password.islower() or new_password.isdigit():
            form.new_password.errors.append("Create a STRONG password with one uppercase character, one lowercase character and one number")
        else:
            if table == 'staff':
                cur.execute("""UPDATE staff SET password=%s WHERE email=%s;""", (generate_password_hash(new_password),g.user))
            else:
                cur.execute("""UPDATE customer SET password=%s WHERE email=%s;""", (generate_password_hash(new_password),g.user))
            mysql.connection.commit()
            cur.close()
            session.clear()
            flash("Successfully changed password! Please login now.")
            
            msg = Message("Michelin Star Password Change Notification", sender=email, recipients=[credentials.flask_email])   
            msg.body = f"""
            Your password has been changed. If this wasn't done by you, please take action now.
            """
            mail.send(msg)

            if table == 'staff':
                return redirect(url_for("staff_login"))
            else:
                return redirect(url_for("customer_login"))
    return render_template("password_management/change_password.html", title ="Change password", form=form)

# Reset password feature
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        table = form.role.data

        pin = sample(range(10000, 99999), 1)

        random_code = ""
        for i in pin:
            random_code += str(i)

        cur = mysql.connection.cursor()
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

            msg = Message(f"Hello, {user['first_name']}", sender=credentials.flask_email, recipients=[user["email"]])
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

        if code != random_code["code"]:
            form.code.errors.append("Oh no, that's not the code in your email!")
        else:
            flash("Code correct! Now you can reset your password :)")
            session["username"] = email
            if table == "customer":
                session["access_level"] = "customer"
            else:
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM staff WHERE email=%s;", (email,) )
                staff = cur.fetchone()
                session["access_level"] = staff['access_level']
                cur.close()
            return redirect(url_for("change_password", table=table))
    return render_template("password_management/confirm_code.html", form=form, title= "Confirm code")

##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
'''
            ALL FEATURES BELOW ARE RELATED TO THE CUSTOMER ACCOUNT FEATURE
'''
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################

#Customer profile - can see info about past transactions + leave a review
@app.route('/customer_profile')
@customer_only
def customer_profile():
    username = session['username']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM dish")
    dishes= cur.fetchall()
    message = ''
    image = None
    cur.execute(" SELECT * FROM customer WHERE email=%s",(username,))
    check= cur.fetchone()['profile_pic']
    if check is None:
        error = 'No profile picture yet'
    else:  
        image=check
    cur.execute("SELECT * FROM transactions WHERE username=%s;",(username,))
    transactionHistory = cur.fetchall()
    if transactionHistory is not None:
        message = "You've made no transactions yet"
    cur.close()
    return render_template('customer/customer_profile.html',image=image, transactionHistory=transactionHistory,dishes=dishes,user=g.user)

@app.route('/user_pic', methods=['GET','POST'])
@customer_only
def user_pic():
    cur = mysql.connection.cursor()
    form = UserPic()
    if form.validate_on_submit():
        profile_pic = form.profile_pic.data
        filename = secure_filename(profile_pic.filename)
        profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cur.execute(' UPDATE customer SET profile_pic=%s WHERE email=%s; ' ,(filename, g.user))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('customer_profile'))
    return render_template('customer/profile_pic.html', form=form)

##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
'''
            ALL FEATURES BELOW ARE RELATED TO THE KITCHEN STAFF
'''
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
# Staff profile
@app.route("/edit_staff_profile", methods=["GET", "POST"])
@business_only
def edit_staff_profile():
    form = ProfileForm()
    profile=None
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM staff WHERE email = %s", (g.user,))
    staff = cur.fetchone()
    cur.close()
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
        flash ("Successfully updated!")
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM staff WHERE email=%s;", (g.user,))
        profile = cur.fetchone()
        cur.close()
    return render_template("staff/edit_staff_profile.html", staff=staff, form=form, title="My Profile", profile=profile)

# creates undolist 
def undoList():
    session['undoList']=[]

# organises and displays priority queue
@app.route('/kitchen', methods=['GET','POST'])
@staff_only
def kitchen():
    if 'undoList' not in session:
        undoList()
    cur = mysql.connection.cursor()

    cur.execute('''SELECT o.order_id, d.name, o.time, d.cook_time, o.table_id, o.notes, o.status, o.dish_id
                    FROM orders as o 
                    JOIN dish as d 
                    ON o.dish_id=d.dish_id
                    ORDER BY o.notes LIKE 'priority,' DESC,
                            o.time,
                            o.time*d.cook_time DESC,
                            o.table_id,  
                            d.cook_time DESC,
                            d.dishType='starter',
                            d.dishType='main',
                            d.dishType='side',
                            d.dishType='dessert';''')
    orderlist=cur.fetchall()
    cur.close()
    return render_template('staff/kitchen.html',orderlist=orderlist)

# updates the status of a meal

@app.route('/<int:dish_id>,<int:order_id>,<int:time>/kitchenUpdate', methods=['GET','POST'])
@staff_only
def kitchenUpdate(dish_id,order_id, time):
    cur = mysql.connection.cursor()
    cur.execute('''UPDATE orders
                                SET status="ongoing" 
                                WHERE time=%s and status="not started" 
                                and order_id=%s 
                                LIMIT 1;''',(time, order_id))
    mysql.connection.commit()
    session['undoList'].append(order_id)

# lowers ingredient stock used
    cur.execute('''SELECT i.ingredient_id
                    FROM orders as o
                    JOIN dish_ingredient as di
                    JOIN ingredient as i
                    JOIN dish as d
                    ON i.ingredient_id=di.ingredient_id AND di.dish_id=d.dish_id AND d.dish_id=o.dish_id
                    WHERE di.dish_id=%s''',(dish_id,))
    ingredientDict=cur.fetchall()
    for ingredient in ingredientDict:
        cur.execute('''UPDATE stock
                        SET quantity=quantity-1
                        WHERE ingredient_id=%s
                        ORDER BY batch_id
                        LIMIT 1''',(ingredientDict[0][ingredient],) )
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('kitchen'))

# updates meal status to sent out
@app.route('/<int:order_id>,<int:time>/kitchenDelete', methods=['GET','POST'])
@staff_only
def kitchenSentOut(order_id, time):

    cur = mysql.connection.cursor()
    cur.execute('''UPDATE orders
                                SET status="sent out"
                                WHERE time=%s and status="ongoing" 
                                and order_id =%s
                                LIMIT 1;''',(time, order_id))
    mysql.connection.commit()
    session['undoList'].append(order_id)
    cur.close()
    return redirect(url_for('kitchen'))

# changes an order to complete and re-routes to kitchen
@app.route('/<int:order_id>,<int:time>/kitchenComplete', methods=['GET','POST'])
@staff_only
def kitchenComplete(order_id, time):

    cur = mysql.connection.cursor()
    cur.execute('''UPDATE orders
                                SET status="completed"
                                WHERE time=%s and status="sent out" 
                                and order_id =%s
                                LIMIT 1;''',(time, order_id))
    mysql.connection.commit()
    session['undoList'].append(order_id)
    cur.close()
    return redirect(url_for('kitchen'))

# undo previous action
@app.route('/kitchenUndo', methods=['GET','POST'])
@staff_only
def kitchenUndo():
    if session['undoList']==[]:
        return redirect(url_for('kitchen'))
    undoID=session['undoList'][-1]
    cur = mysql.connection.cursor()
    cur.execute('''SELECT status
                    FROM orders
                    WHERE order_id=%s;''',(undoID,) )
    status=cur.fetchall()
    if status[0]["status"]=="ongoing":
        cur.execute('''UPDATE orders
                                    SET status="not started"
                                    WHERE order_id =%s;''',(undoID,))  
        cur.execute('''SELECT dish_id
                        FROM orders
                        WHERE order_id=%s''',(undoID,))
        dish_id=cur.fetchone()
        cur.execute('''SELECT i.ingredient_id
                    FROM orders as o
                    JOIN dish_ingredient as di
                    JOIN ingredient as i
                    JOIN dish as d
                    ON i.ingredient_id=di.ingredient_id AND di.dish_id=d.dish_id AND d.dish_id=o.dish_id
                    WHERE di.dish_id=%s''',(dish_id["dish_id"],))
        ingredientDict=cur.fetchall()
        for ingredient in ingredientDict:
            cur.execute('''UPDATE stock
                            SET quantity=quantity+1
                            WHERE ingredient_id=%s
                            ORDER BY batch_id
                            LIMIT 1''',(ingredient["ingredient_id"],) )
            mysql.connection.commit()
    else:
        cur.execute('''UPDATE orders
                                    SET status="ongoing"
                                    WHERE order_id =%s;''',(undoID,))
    mysql.connection.commit()
    del session['undoList'][-1]
    cur.close()
    return redirect(url_for('kitchen'))

##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
'''
            ALL FEATURES BELOW ARE RELATED TO THE WAITER STAFF
'''
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################

# Waiter chooses a table to take an order from
@app.route("/choose_table", methods=["GET","POST"])
@staff_only
def choose_table():
    cur = mysql.connection.cursor()
        
    cur.execute('SELECT table_id, x, y FROM tables ORDER BY table_id')
    data = cur.fetchall()
    
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H")
    
    cur.execute('SELECT * FROM bookings WHERE time = %s AND date = %s',(time, date))
    booking_current = cur.fetchall()
    
    cur.execute('SELECT * FROM bookings WHERE time = %s AND date = %s',(int(time)+1, date))
    booking_next = cur.fetchall()
    
    cur.close()
    table_positions = {}
    for i in range(len(data)):
        table_positions[data[i]['table_id']] = [data[i]['x'], data[i]['y'], 'btn btn-outline-success', None, None]
        
    for booking in booking_next:
        table_positions[booking['table_id']][2] = 'btn btn-outline-warning'
        
    for booking in booking_current:
        table_positions[booking['table_id']][2] = 'btn btn-outline-danger'
        table_positions[booking['table_id']][3] = booking['name']
        table_positions[booking['table_id']][4] = booking['time']

    return render_template("staff/choose_table.html", table_positions=table_positions)

# offers a simple view of the menu, ordered meals and an order list similar to a waiter's notepad
@app.route("/<int:table>/take_order", methods=["GET","POST"])
@staff_only
def take_order(table):  
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM dish')
    meals = cur.fetchall()
        
    cur.execute(
        """
            SELECT dish.name, orders.status, order_id, dish.dishType, orders.notes
            FROM orders JOIN dish 
            ON orders.dish_id = dish.dish_id
            WHERE orders.table_id = %s 
            AND orders.status != %s
            AND orders.status != %s
        """,(table,'complete', 'cancelled')
    )
    ordered = cur.fetchall()
    
    current_day = datetime.now().strftime("%d")
    current_month = datetime.now().strftime("%m")
    current_year = datetime.now().strftime("%Y")
    date = current_year+"-"+current_month+"-"+current_day
    time = datetime.now().strftime("%H")
    
    cur.execute(
        """
            SELECT * FROM bookings
            WHERE date = %s 
            AND time = %s
            AND table_id = %s
        """,(date, time, table)
    )
    booking = cur.fetchall()
    if len(booking) > 0:
        allocated = 1
    else:
        allocated = 0
    if 'ordering' not in session:
        session['ordering'] = {}
    if table in session['ordering']:
        ordering = session['ordering'][table]
        return render_template("staff/take_order.html", table=table, ordering=ordering, meals=meals, ordered=ordered, allocated=allocated)
    return render_template("staff/take_order.html", table=table, meals=meals, ordered=ordered, allocated=allocated)

# allows waiter to customize ingredients in a meal and add it to the order
@app.route('/<int:table>/waiter_customize_dish/<int:dish_id>', methods=['GET','POST'])
@staff_only
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
        """
        min = 100
        for id in ingredient_ids:
            cur.execute('''SELECT MIN(quantity) FROM stock WHERE ingredient_id = %s
                        ORDER BY batch_id
                        LIMIT 1''',(id['ingredient_id'],))
            value = cur.fetchone()
            if value['MIN(quantity)'] < min:
                min = value['MIN(quantity)']
        if min > 0:
        """
        if True:
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

# increases portion of an ingredient in a dish
@app.route('/<int:table>/waiter_inc_quantity_ingredient/<int:ingredient_id>')
@staff_only
def waiter_inc_quantity_ingredient(table, ingredient_id):
    dish_id = session['CurrentDish'] # put this as input
    if ingredient_id not in session[str(dish_id)]:
        session[str(dish_id)][ingredient_id] = 1
    session[str(dish_id)][ingredient_id] = session[str(dish_id)][ingredient_id] +1
    return redirect(url_for('waiter_customize_dish', table=table, dish_id=dish_id))

# decreases portion of an ingredient in a dish
@app.route('/<int:table>/waiter_dec_quantity_ingredient/<int:ingredient_id>')
@staff_only
def waiter_dec_quantity_ingredient(table, ingredient_id):
    dish_id = session['CurrentDish']
    if ingredient_id not in session[str(dish_id)]:
        session[str(dish_id)][ingredient_id] = 1
    if session[str(dish_id)][ingredient_id] !=0:
        session[str(dish_id)][ingredient_id] = session[str(dish_id)][ingredient_id] -1
    return redirect(url_for('waiter_customize_dish',table=table, dish_id=dish_id))

# adds meal to order if ingredients are available
@app.route("/<int:table>/add_order/<meal>", methods=["GET","POST"])
@staff_only
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
    """
    min = 100
    for id in ingredient_ids:
        cur.execute('SELECT MIN(quantity) FROM stock WHERE ingredient_id = %s ORDER BY batch_id LIMIT 1',(id['ingredient_id'],))
        value = cur.fetchone()
        if value['MIN(quantity)'] < min:
            min = value['MIN(quantity)']
    if min > 0:
    """
    if True:
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

# remove a meal from the ordering list
@app.route("/<int:table>/remove_meal/<meal>/<int:index>", methods=["GET","POST"])
@staff_only
def remove_meal(table, meal, index):
    session['ordering'][table][meal].pop(index)
    if len(session['ordering'][table][meal]) == 0:
        session['ordering'][table].pop(meal)
    return redirect(url_for("take_order", table=table))

# cancel a meal that has been sent to the kitchen
@app.route("/<int:table>/cancel_meal/<int:meal_id>", methods=["GET","POST"])
@staff_only
def cancel_meal(table, meal_id):
    
    cur = mysql.connection.cursor()
    cur.execute(
        """
            UPDATE orders SET status = 'cancelled'
            WHERE table_id = %s 
            AND status != %s
            AND order_id = %s
        """,(table, 'completed', meal_id)
    )
    mysql.connection.commit()

    cur.execute("""INSERT INTO notifications (user, title, message)
                    VALUES (%s, "Meal Cancelled","Table ID %s");""", (g.user, table,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("take_order", table=table))

# prioritise a meal that has been sent to the kitchen
@app.route("/<int:table>/prioritise/<int:meal_id>", methods=["GET","POST"])
@staff_only
def prioritise(table, meal_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT notes FROM orders WHERE table_id = %s AND order_id = %s',(table, meal_id))
    notes = cur.fetchone()['notes']
    notes += " Prioritise"
    cur.execute(
        """
            UPDATE orders SET notes = %s
            WHERE table_id = %s 
            AND order_id = %s
        """,(notes, table, meal_id)
    )
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("take_order", table=table))

# cancel all meals in the ordering section
@app.route("/<int:table>/cancel_order", methods=["GET","POST"])
@staff_only
def cancel_order(table):
    session['mods'][table] = {}
    session['ordering'][table] = {}
    return redirect(url_for("take_order", table=table))

# send ordering list to the kitchen, displayed in orders
@app.route("/<int:table>/complete_order", methods=["GET","POST"])
@staff_only
def complete_order(table):  
    cur = mysql.connection.cursor()
    if table in session['ordering']:
        ordering = session['ordering'][table]
        for meal in ordering:
            cur.execute('SELECT dish_id, cook_time FROM dish WHERE name = %s',(meal,))
            data = cur.fetchone()
            for times in ordering[meal]:
                info = ""
                for ingredients in times:
                    if times[ingredients] != 1:
                        info += ingredients+"-"+str(times[ingredients])+", "
                cur.execute("INSERT INTO orders (time, dish_id, table_id, status, notes) VALUES (%s, %s, %s, 'unmade', %s);",(datetime.now().strftime("%H:%M:%S"), data['dish_id'], table, info))
                mysql.connection.commit()
    
    session['ordering'][table] = {}
    return redirect(url_for('take_order', table=table))

# simulates physical payment, marks orders as 'paid'
@app.route("/<int:table>/take_payment", methods=["GET","POST"])
@staff_only
def take_payment(table):  
    cur = mysql.connection.cursor()
    cur.execute(
        """
            UPDATE orders SET status = 'complete'
            WHERE table_id = %s 
            AND status != %s
        """,(table, 'cancelled')
    )
    mysql.connection.commit()
    return redirect(url_for('take_order', table=table))

# drag and drop table icons on GUI
@app.route("/move_tables", methods=["GET","POST"])
@business_only
def move_tables():
    cur = mysql.connection.cursor()
    
    cur.execute('SELECT table_id, x, y FROM tables ORDER BY table_id')
    data = cur.fetchall()
    cur.close()
    table_positions = {}
    for i in range(len(data)):
        table_positions[data[i]['table_id']] = (data[i]['x'], data[i]['y'])
    return render_template("staff/move_tables.html", table_positions=table_positions)

# takes new table positions from /move_tables and saves the new layout
@app.route('/save_tables', methods=['GET','POST'])
@business_only
def save_tables():
    co_ords = request.get_json()
    if co_ords is not None:
        cur = mysql.connection.cursor()
        for i in range(int(len(co_ords)/2)):
            cur.execute("UPDATE tables SET x = '"+co_ords[i*2]+"', y = '"+co_ords[(i*2)+1]+"' WHERE table_id ="+str(i+1)+"; ")
            mysql.connection.commit()
        cur.close()
    return redirect(url_for('choose_table'))

# waiter can reserve a table on the system for walk in customers
@app.route('/allocate_table/<int:table>', methods=['GET','POST'])
@staff_only
def allocate_table(table):
    cur = mysql.connection.cursor()
    current_day = datetime.now().strftime("%d")
    current_month = datetime.now().strftime("%m")
    current_year = datetime.now().strftime("%Y")
    time = datetime.now().strftime("%H")
    date = current_year+"-"+current_month+"-"+current_day
    cur.execute('INSERT INTO bookings(booker_id,table_id,name,date,time) VALUES(%s,%s,%s,%s,%s) ',(0, table,'Walk in',date,time))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('take_order', table=table))

@app.route("/roster_request", methods=["GET", "POST"])
@staff_only
def roster_request():
    cur = mysql.connection.cursor()
    form = RosterRequestForm()
    if form.validate_on_submit():
        message = form.message.data
        cur.execute("SELECT * FROM staff where email=%s", (g.user,))
        employee = cur.fetchone()
        employee_name = employee["first_name"] + " " + employee["last_name"]

        cur.execute("""INSERT INTO roster_requests (employee_email, employee_name, message)
                            VALUES (%s,%s,%s);""", (g.user, employee_name, message))
        mysql.connection.commit()
        cur.execute("""INSERT INTO notifications (user, title, message)
                    VALUES ("manager", "New Roster Request","From %s");""", (employee,))
        mysql.connection.commit()
        cur.close()

        flash ("Request successfully sent!")
    return render_template("staff/roster_request.html", form=form,title="Roster Request")

# displays roster for staff and manager
@app.route("/roster_timetable", methods=["GET","POST"])
@business_only
def roster_timetable():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM roster JOIN staff ON roster.staff_id = staff.staff_id ORDER BY staff.staff_id;")
    roster = cur.fetchall()
    cur.close()
    return render_template("manager/roster_timetable.html", roster=roster)

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

#checks expiry date of stock and reorders stock in short supply
def manageStock():
    cur = mysql.connection.cursor()
    date = datetime.now().date()

    cur.execute('''SELECT i.name 
                FROM ingredient as i 
                JOIN stock as s 
                ON i.ingredient_id=s.ingredient_id
                WHERE expiry_date=%s;''', (date,))
    name=cur.fetchall()

    cur.execute('''DELETE FROM stock
                WHERE expiry_date=%s;''', (date,))
    mysql.connection.commit()

    message=""

    for item in name:
    # Notify manager about expiry of stock
      message =message + f"Your {item['name']} is expired!\n"
      msg = Message("Expiry Notice", sender=credentials.flask_email, recipients=[g.user])   
      msg.body = f"""{message}"""
      mail.send(msg)

    for item in name:
        cur.execute("""INSERT INTO notifications (user, title, message)
                    VALUES ("manager", "Inventory Expired Notice","Inventory items << %s >> has expired, please take action.");""", (item['name'],))
        mysql.connection.commit()  

    cur.execute('''SELECT *
                    FROM ingredient as i
                    JOIN stock as s
                    ON i.ingredient_id=s.ingredient_id
                    WHERE s.quantity<=10;''')
    emails=cur.fetchall()

    cur.execute('''SELECT i.ingredient_id, i.pending_restock
                    FROM ingredients as i
                    JOIN stock as s
                    ON i.ingredient_id=s.ingredient_id
                    WHERE o.quantity>10 AND pending_stock=1;''')
    restocked=cur.fetchall()

    for ingredient in restocked:
        cur.execute('''UPDATE ingredients
                        SET pending_restock=0
                        WHERE ingredient_id=%s;''', (ingredient["ingredient_id"],))
        mysql.connection.commit()

    for email in emails:
        if email['pending_restock']==0:
          if email["supplier_email"] is not None:
              message = f"can we have more {email['name']} please. Same as last week!"
              msg = Message("Order Notice", sender=credentials.flask_email, recipients=[email["supplier_email"]])   
              msg.body = f"""{message}"""
              mail.send(msg)

              cur.execute('''UPDATE ingredients
                          SET pending_restock=1
                          WHERE ingredient_id=%s;''', (email["ingredient_id"],))
              mysql.connection.commit()
    cur.close()

scheduler = BackgroundScheduler()
scheduler.add_job(func=manageStock, trigger="interval", hours=24)
scheduler.start()

# Manager dashboard feature data analytics, user analytics and staff requests
@app.route("/manager")
@manager_only
def manager():
    cur = mysql.connection.cursor()
    date = datetime.date.today().strftime('%Y-%m-%d')
    
    cur.execute("SELECT * FROM user_analytics WHERE DATE(todays_date)=%s", (date,))
    user_analytics = cur.fetchone()
    
    # ================= START of fetching gross profit data for the past year, month and day ================= 
    cur.execute(
        """SELECT SUM(dish.cost) AS gross_profit
        FROM orders
        INNER JOIN dish ON orders.dish_id = dish.dish_id
        WHERE orders.time BETWEEN DATE_SUB(DATE_ADD(CURDATE(), INTERVAL 1 DAY), INTERVAL 1 YEAR) 
        AND DATE_ADD(CURDATE(), INTERVAL 1 DAY);""")
    yearly_profit = cur.fetchone()
    yearly_profit = yearly_profit["gross_profit"]

    cur.execute(
        """SELECT SUM(dish.cost) AS gross_profit
        FROM orders
        INNER JOIN dish ON orders.dish_id = dish.dish_id
        WHERE orders.time BETWEEN DATE_SUB(DATE_ADD(CURDATE(), INTERVAL 1 DAY), INTERVAL 30 DAY) 
        AND DATE_ADD(CURDATE(), INTERVAL 1 DAY);""")
    monthly_profit = cur.fetchone()
    monthly_profit = monthly_profit["gross_profit"]

    cur.execute(
        """SELECT SUM(dish.cost) AS gross_profit
        FROM orders
        INNER JOIN dish ON orders.dish_id = dish.dish_id
        WHERE DATE(orders.time) = CURDATE();""")
    daily_profit = cur.fetchone()
    daily_profit = daily_profit["gross_profit"]

    if daily_profit is None:
        daily_profit=0.00
    # =================  END of fetching gross profit data for the past year, month and day ================= 

    # ================= START of calculating turnover ================= 
    cur.execute(
        """SELECT * FROM monthly_revenue
            WHERE the_month = DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 YEAR), '%Y-%m-01');""")
    same_month_of_prev_year = cur.fetchone()
    same_month_of_prev_year = same_month_of_prev_year["monthly_sales"]

    cur.execute(
        """SELECT * FROM yearly_revenue
        WHERE the_year = DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 YEAR), '%Y-01-01');
        """)
    prev_year = cur.fetchone()
    prev_year = prev_year["yearly_sales"]
    
    monthly_turnover = round((((float(monthly_profit) - float(same_month_of_prev_year)) / float(same_month_of_prev_year)) * 100.0),2)
    yearly_turnover = round((((float(yearly_profit) - float(prev_year)) / float(prev_year)) * 100.0),2)
    # ================= END of calculating turnover ================= 

    cur.execute("SELECT count(*) FROM user_queries where date(date_received) = %s", (date,))
    query_count = cur.fetchone()

    cur.execute("SELECT * FROM roster_requests WHERE status = 'Pending'")
    pending_requests = cur.fetchall()

    cur.execute("SELECT * FROM roster_requests WHERE status = 'Approved' ORDER BY last_updated DESC")
    approved_requests = cur.fetchall()

    cur.execute("SELECT * FROM roster_requests WHERE status = 'Rejected' ORDER BY last_updated DESC")
    rejected_requests = cur.fetchall()

    daily_profit = '{:,.2f}'.format(float(daily_profit))
    monthly_profit = '{:,.2f}'.format(float(monthly_profit))
    yearly_profit = '{:,.2f}'.format(float(yearly_profit))

    cur.close()
    return render_template("manager/dashboard.html", yearly_turnover=yearly_turnover, monthly_turnover=monthly_turnover, daily_profit=daily_profit, monthly_profit=monthly_profit, yearly_profit=yearly_profit, rejected_requests=rejected_requests,approved_requests=approved_requests, pending_requests=pending_requests, user_analytics=user_analytics, query_count=query_count, title="Dashboard")

# function that marks the roster request as "accepted"
@app.route("/roster_approve/<int:id>")
@manager_only
def roster_approve(id):
    cur = mysql.connection.cursor()
    cur.execute("""UPDATE roster_requests SET status='Approved', last_updated=CURRENT_TIMESTAMP WHERE request_id= %s;""", (id,))
    mysql.connection.commit()

    cur.execute("SELECT * roster_requests WHERE request_id= %s", (id,))
    employee = cur.fetchone()
    email = employee["employee_email"]

    cur.execute("""INSERT INTO notifications (user, title, message)
                    VALUES (%s, 'Roster Request Approved!','Your manager has approved your request!');""", (email,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("manager"))

# function that marks the roster request as "rejected"
@app.route("/roster_reject/<int:id>", methods=["GET", "POST"])
@manager_only
def roster_reject(id):
    form = RejectRosterRequestForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        response = form.response.data
        status = 'Rejected'
        cur.execute("""UPDATE roster_requests SET status=%s, response=%s, last_updated=CURRENT_TIMESTAMP WHERE request_id=%s;""", (status, response, id))
        mysql.connection.commit()
        
        cur.execute("""SELECT * roster_requests WHERE request_id= %s;""", (id,))
        employee = cur.fetchone()
        cur.execute("""INSERT INTO notifications (user, title, message)
                        VALUES (%s, "Roster Request Rejected","Your manager's reponse: '%s'");""", (employee["employee_email"],response))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("manager"))
    return render_template("manager/roster_reject.html", form=form)

# generates a random roster based on shift requirements
@app.route("/generate_roster", methods=["GET","POST"])
@manager_only
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
    cur.execute("""INSERT INTO notifications (user, title, message)
                        VALUES ("staff", "New Weekly Schedule Released","Go check out the new weekly schedule!");""")
    mysql.connection.commit()
    cur.close()
    flash("Roster successfully generated! Below is your new weekly schedule.")
    flash(Markup('Not happy with the results? Click <a href="generate_roster">here</a> to generate the roster again!'))
    return redirect(url_for('roster_timetable'))

# Roster view where individual shifts can be deleted
@app.route("/delete_from_roster", methods=["GET"])
@manager_only
def delete_from_roster():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM roster JOIN staff ON roster.staff_id = staff.staff_id ORDER BY staff.staff_id;")
    roster = cur.fetchall()
    cur.close() 
    return render_template("manager/delete_from_roster.html", roster=roster)

# removes shift from roster for a staff member
@app.route("/remove_roster_slot/<int:staff_id>/<int:day>", methods=["GET","POST"])
@manager_only
def remove_roster_slot(staff_id, day):
    week = ['mon','tue','wed','thu','fri','sat','sun']
    cur = mysql.connection.cursor()
           
    cur.execute("UPDATE roster SET "+week[day]+" = '' WHERE staff_id = %s;",(staff_id,))
    mysql.connection.commit()
    
    cur.execute("SELECT * FROM staff WHERE staff_id = %s;",(staff_id,))
    staff = cur.fetchall()

    cur.execute("""INSERT INTO notifications (user, title, message)
                        VALUES (%s, "A shift has been removed","Please check the schedule for updates");""", (staff["email"],))
    mysql.connection.commit()
    return redirect(url_for('delete_from_roster'))

# manually enter a shift into the roster
@app.route("/add_to_roster_timetable", methods=["GET","POST"])
@manager_only
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
            form.staff_id.errors = "Staff ID does not exist"
    cur.execute("SELECT * FROM roster JOIN staff ON roster.staff_id = staff.staff_id ORDER BY staff.staff_id;")
    roster = cur.fetchall()
    cur.close()
    return render_template("manager/add_to_roster_timetable.html", roster=roster, form=form)

# form to change shift requirements -> eg opening hours, minimum staff levels
@app.route("/manage_shift_requirements", methods=["GET","POST"])
@manager_only
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
                        WHERE day = %s;""", (opening_time, closing_time, min_workers, unavailable, day))
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

# View and manage all employees
@manager_only
@app.route("/view_all_employees")
def view_all_employees():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM staff")
    employees = cur.fetchall()
    cur.close()
    return render_template("manager/employees.html", employees=employees, title="Employee Data")

# Remove existing employee
@app.route("/remove_employee/<int:id>")
@manager_only
def remove_employee(id):
    cur = mysql.connection.cursor()
    cur.execute("""DELETE FROM staff WHERE staff_id=%s""", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("view_all_employees"))

# Add new employee
@app.route("/add_new_employee", methods=["GET", "POST"])
@manager_only
def add_new_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
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
        msg = Message("Welcome on board! We're happy you joined us.", sender=credentials.flask_email, recipients=[email])   
        msg.body = f"""{message}"""
        mail.send(msg)

        cur.execute("""INSERT INTO notifications (user, title, message)
                        VALUES (%s, "Welcome!","We're happy to have you onboard with us!");""", (email,))
        mysql.connection.commit()
        cur.close()
        flash ("New employee successfully added!")
        return redirect(url_for("add_new_employee"))
    return render_template("manager/add_new_staff.html", form=form, title="Add New Employee")   

# View queries from users
@app.route("/view_query")
@manager_only
def view_query():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_queries")
    queries = cur.fetchall()
    cur.close()
    return render_template("manager/queries.html", queries=queries)

# Delete queries from users

@app.route("/delete_query/<int:id>")
@manager_only
def delete_query(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user_queries WHERE query_id=%s", (id,))
    cur.fetchone()
    mysql.connection.commit()
    cur.close()
    flash ("Deleted!")
    return redirect(url_for("view_query"))

# Manager can reply to user queries
@app.route("/reply_email/<id>", methods=["GET", "POST"])
@manager_only
def reply_email(id):
    cur = mysql.connection.cursor()
    form = ReplyForm()
    cur.execute("SELECT * FROM user_queries WHERE query_id=%s", (id,))
    query = cur.fetchone()
    cur.close()

    if form.validate_on_submit() == False:
        flash('All fields are required.')
    else:
        email = form.email.data
        subject = form.subject.data
        message = form.message.data

        msg = Message("Replying to your query: "+subject, sender=credentials.flask_email, recipients=[email])   
        msg.body = f"""{message}"""
        mail.send(msg)
        flash("Message sent successfully.")
    return render_template("manager/reply_email.html",form=form, title="Reply", query=query)


# View the ingredients masterlist
@app.route("/view_inventory", methods=["GET", "POST"])
@manager_only
def view_inventory():
    form = Supplier()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ingredient;")
    inventory = cur.fetchall()
    cur.close()
    return render_template("manager/inventory.html",form=form, inventory=inventory, title="Inventory List")

# Associate a supplier to an ingredient 
@app.route("/add_supplier/<int:id>", methods=["GET", "POST"])
@manager_only
def add_supplier(id):
    form = Supplier()
    if form.validate_on_submit():
        data = form.email.data
        cur = mysql.connection.cursor()
        cur.execute("UPDATE ingredient SET supplier_email = %s WHERE ingredient_id = %s;",(data, id))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('view_inventory'))

# Edit supplier email if the email is incorrect/supplier is changed
@app.route("/edit_supplier/<int:id>", methods=["GET", "POST"])
def edit_supplier(id):
    form = EditSupplier()
    if form.validate_on_submit():
        data = form.email.data
        cur = mysql.connection.cursor()
        cur.execute("UPDATE ingredient SET supplier_email = %s WHERE ingredient_id = %s;",(data, id))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('view_inventory'))

# Delete an ingredient from the masterlist
@app.route("/delete_ingredient/<int:id>")
@manager_only
def delete_ingredient(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM ingredient WHERE ingredient_id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("Ingredient deleted!")
    return redirect(url_for('view_inventory'))

# Add a new dish to the menu
@app.route('/addDish', methods=['GET','POST'])
@manager_only
def addDish():
    cur = mysql.connection.cursor()
    form = AddDishForm()
    if form.validate_on_submit():
        name = form.name.data
        cur.execute('SELECT * from dish WHERE name=%s',(name,))
        result = cur.fetchone()
        if result is not None:
            form.name.errors.append("This menu item already exists")
        else:
            day = form.day.data
            cost = form.cost.data
            cookTime = form.cookTime.data
            dishType = (form.dishType.data).lower()
            dishDescription = form.dishDescription.data
            dishPic = form.dishPic.data
            ingredients = form.ingredients.data
            allergins= form.allergins.data
            filename = secure_filename(dishPic.filename)
            dishPic.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            cur.execute("INSERT INTO dish (name, cost, cook_time, dishType, description,dishPic,allergies,day) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);", (name,cost,cookTime,dishType,dishDescription,filename,allergins,day))
           
            mysql.connection.commit()
            if ingredients is not None:
                ingredients=ingredients.split(',')
                for ingredient in ingredients:
                    cur.execute("SELECT * FROM ingredient WHERE name=%s",(ingredient,))
                    ingredient_id=cur.fetchone()
                    if ingredient_id is not None:
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
            
            cur.execute("""INSERT INTO notifications (user, title, message)
                        VALUES ("staff", "Release of new menu item","New menu item <%s> is now active!");""", (name,))
            mysql.connection.commit()

            cur.close()
            flash("Successfully added new menu item!")
            return redirect(url_for('addDish'))
    return render_template('manager/addDish.html', form=form)

# View and manage all existing menu items
#@manager_only
@app.route("/view_all_menu_items")
@manager_only
def view_all_menu_items():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM dish")
    menu_items = cur.fetchall()
    cur.close()
    return render_template("manager/menu_items.html", menu_items=menu_items, title="Menu Items Data")

# Remove menu items
@app.route("/remove_menu_item/<int:id>")
@manager_only
def remove_menu_item(id):
    cur = mysql.connection.cursor()
    cur.execute("""DELETE FROM dish WHERE dish_id=%s""", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("view_all_menu_items"))

# form to add a new table in the restaurant
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
            cur.close()
            return render_template("manager/add_table.html", form=form)
        else:
            cur.execute("INSERT INTO tables VALUES (%s, %s, %s, %s);",(table_number, seats, x, y))
            mysql.connection.commit()
            cur.execute("""INSERT INTO notifications (user, title, message)
                        VALUES ("staff", "New Table Has Been Added To The GUI","New table number <%s> is now active!");""", (table_number,))
            mysql.connection.commit()
            cur.close()
            flash("Table successfully added!")
            return redirect(url_for('add_table'))
    return render_template("manager/add_table.html", form=form)

# displays tables which can be deleted
@app.route("/remove_table_menu", methods=["GET","POST"])
@manager_only
def remove_table_menu():
    cur = mysql.connection.cursor()
    cur.execute('SELECT table_id, x, y FROM tables ORDER BY table_id')
    data = cur.fetchall()
    cur.close()
    table_positions = {}
    for i in range(len(data)):
        table_positions[data[i]['table_id']] = (data[i]['x'], data[i]['y'])
    return render_template("manager/remove_table.html", table_positions=table_positions)

# removes a table from the system, called from /remove_table_menu
@app.route("/<int:table>/remove_table", methods=["GET", "POST"])
@manager_only
def remove_table(table):
    cur = mysql.connection.cursor()
        
    cur.execute("DELETE FROM tables WHERE table_id = %s;",(table,))
    mysql.connection.commit()
    cur.execute("""INSERT INTO notifications (user, title, message)
                        VALUES ("staff", "A Table Has Been Deleted From The GUI","Table number <%s> has been deleted.");""", (table,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('remove_table_menu'))

# display ingredient batches ordered and expiry dates
@app.route("/stock", methods=["GET", "POST"])
@manager_only
def stock():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stock JOIN ingredient ON stock.ingredient_id = ingredient.ingredient_id")
    stock = cur.fetchall()
    cur.execute("SELECT name FROM ingredient")
    ingredients = cur.fetchall()
    ingredientList = []
    for ingredient in ingredients:
        ingredientList.append(ingredient['name'])
    form=StockForm()
    form.ingredient.choices = ingredientList
    if form.validate_on_submit():
        ingredient_name = form.ingredient.data
        date = form.date.data
        quantity = form.quantity.data
        cur.execute("SELECT ingredient_id FROM ingredient WHERE name = %s",(ingredient_name,))
        ingredient = cur.fetchall()
        cur.execute("""INSERT INTO stock (ingredient_id, expiry_date, quantity)
                            VALUES (%s,%s,%s);""", (ingredient[0]['ingredient_id'], date, quantity))
        mysql.connection.commit()
        cur.execute("SELECT * FROM stock JOIN ingredient ON stock.ingredient_id = ingredient.ingredient_id")
        stock = cur.fetchall()
        cur.execute("SELECT name FROM ingredient")
        ingredients = cur.fetchall()
        ingredientList = []
        for ingredient in ingredients:
            ingredientList.append(ingredient['name'])

    return render_template("manager/stock.html", stockList=stock, ingredientList=ingredientList, form=form)

##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
'''
            ALL FEATURES BELOW ARE RELATED TO MENU, CART AND CHECKOUT FEATURES
'''
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################

#For customers to view all dish items they could order
@app.route('/menu',methods=['GET'])
def menu():
    if 'order_by' not in session:
        session['order_by'] = 'low'
    cur=mysql.connection.cursor()
    
    if session['order_by'] == 'low':
        cur.execute("""SELECT d.cost, d.description, d.dishPic,d.name, d.dish_id, IFNULL(ROUND(avg(rating)*2)/2, 0) AS avg_rating
                      FROM dish AS d
                      LEFT JOIN reviews AS r ON d.dish_id = r.dish_id
                      WHERE d.dishType='starter'
                      GROUP BY dish_id
                      ORDER BY cost;""")
        starters = cur.fetchall()
        cur.execute("""SELECT d.cost, d.description, d.name,d.dishPic ,d.dish_id, IFNULL(ROUND(avg(rating)*2)/2, 0) AS avg_rating
                      FROM dish AS d
                      LEFT JOIN reviews AS r ON d.dish_id = r.dish_id
                      WHERE d.dishType='main'
                      GROUP BY dish_id
                      ORDER BY cost;""")
        mainCourse = cur.fetchall()
        cur.execute("""SELECT d.cost, d.description, d.name,d.dishPic, d.dish_id, IFNULL(ROUND(avg(rating)*2)/2, 0) AS avg_rating
                      FROM dish AS d
                      LEFT JOIN reviews AS r ON d.dish_id = r.dish_id
                      WHERE d.dishType='dessert'
                      GROUP BY dish_id
                      ORDER BY cost;""")
        dessert = cur.fetchall()
        cur.execute("""SELECT d.cost, d.description, d.name,d.dishPic, d.dish_id, IFNULL(ROUND(avg(rating)*2)/2, 0) AS avg_rating
                      FROM dish AS d
                      LEFT JOIN reviews AS r ON d.dish_id = r.dish_id
                      WHERE d.dishType='drink'
                      GROUP BY dish_id
                      ORDER BY cost;""")
        drink = cur.fetchall()
        cur.execute("""SELECT d.cost, d.description, d.dishPic,d.name, d.dish_id, IFNULL(ROUND(avg(rating)*2)/2, 0) AS avg_rating
                      FROM dish AS d
                      LEFT JOIN reviews AS r ON d.dish_id = r.dish_id
                      WHERE d.dishType='side'
                      GROUP BY dish_id
                      ORDER BY cost;""")
        side = cur.fetchall()
    
    else:
        cur.execute("""SELECT d.cost, d.description, d.dishPic,d.name, d.dish_id, IFNULL(ROUND(avg(rating)*2)/2, 0) AS avg_rating
                        FROM dish AS d
                        LEFT JOIN reviews AS r ON d.dish_id = r.dish_id
                        WHERE d.dishType='starter'
                        GROUP BY dish_id
                        ORDER BY cost DESC;""")
        starters = cur.fetchall()
        cur.execute("""SELECT d.cost, d.description, d.name, d.dishPic,d.dish_id, IFNULL(ROUND(avg(rating)*2)/2, 0) AS avg_rating
                        FROM dish AS d
                        LEFT JOIN reviews AS r ON d.dish_id = r.dish_id
                        WHERE d.dishType='main'
                        GROUP BY dish_id
                        ORDER BY cost DESC;""")
        mainCourse = cur.fetchall()
        cur.execute("""SELECT d.cost, d.description, d.name,d.dishPic ,d.dish_id, IFNULL(ROUND(avg(rating)*2)/2, 0) AS avg_rating
                        FROM dish AS d
                        LEFT JOIN reviews AS r ON d.dish_id = r.dish_id
                        WHERE d.dishType='dessert'
                        GROUP BY dish_id
                        ORDER BY cost DESC;""")
        dessert = cur.fetchall()
        cur.execute("""SELECT d.cost, d.description, d.name, d.dishPic,d.dish_id, IFNULL(ROUND(avg(rating)*2)/2, 0) AS avg_rating
                        FROM dish AS d
                        LEFT JOIN reviews AS r ON d.dish_id = r.dish_id
                        WHERE d.dishType='drink'
                        GROUP BY dish_id
                        ORDER BY cost DESC;""")
        drink = cur.fetchall()
        cur.execute("""SELECT d.cost, d.description, d.name, d.dishPic,d.dish_id, IFNULL(ROUND(avg(rating)*2)/2, 0) AS avg_rating
                        FROM dish AS d
                        LEFT JOIN reviews AS r ON d.dish_id = r.dish_id
                        WHERE d.dishType='side'
                        GROUP BY dish_id
                        ORDER BY cost DESC;""")
        side = cur.fetchall()
      
    cur.execute("SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
    cur.execute("""SELECT DISTINCT(dish_id), dish_name, comment, rating
                    FROM reviews
                    WHERE rating >= 4 and comment != ''
                    GROUP BY dish_id
                    """)
    reviews=cur.fetchall()
    
    cur.execute("SELECT dish_id FROM dish where name='Beef Burger' or name='Roast chicken' or name='Cupcake' LIMIT 3")
    slider_ids = cur.fetchall()
    slider_list = []
    for id in slider_ids:
        slider_list.append(id['dish_id'])
    cur.execute(" SELECT * FROM dish WHERE dish_id IN %s",(slider_list,))
    slider = cur.fetchall()
    
    day = datetime.now().weekday()
    cur.execute(" SELECT * FROM dish WHERE dishType='special' AND day = %s",(day,))
    special = cur.fetchall()
    
    cur.execute(" SELECT * FROM reviews where rating >= 4 and comment != '' ")
    cur.close()
    return render_template('customer/dishes.html', starters=starters, mainCourse=mainCourse,dessert=dessert, drink=drink,side=side, reviews=reviews, special=special, slider=slider, session=session)

@app.route('/swap_sort',methods=['GET', 'POST'])
def swap_sort():
    if session['order_by'] == 'low':
        session['order_by'] = 'high'
    else:
        session['order_by'] = 'low'
    return redirect(url_for('menu'))

# Customer can give a rating and comment for a dish they've purchased
@app.route('/review_dish/<int:dish_id>',methods=['GET', 'POST'])
@customer_only
def review_dish(dish_id):
    cur=mysql.connection.cursor()
    cur.execute('''SELECT * FROM dish WHERE dish_id = %s''',(dish_id,))
    dish = cur.fetchone()
    url = request.url # current webpage
    form = Review()
    if form.validate_on_submit():
        rating = request.form['stars'] # this would give a value between 1 to 5, depending on the num of stars selected
        comment = form.comment.data
        cur.execute("SELECT * FROM customer WHERE email=%s", (g.user,))
        customer = cur.fetchone()
        cur.execute("""INSERT INTO reviews ( username, name, comment, rating, dish_name, dish_id) VALUES
                (%s,%s,%s,%s,%s,%s)""",(g.user, customer["first_name"], comment, int(rating), dish["name"], dish_id))
        mysql.connection.commit()
        
        cur.execute("""INSERT INTO notifications (user, title, message)
                        VALUES (%s, "You are awesome!","Thank you for submitting a review for %s");""", (g.user, dish["name"]))
        mysql.connection.commit()
        cur.close()
        flash("Review submitted!")
        return redirect(url)
    return render_template('customer/review_dish.html', dish=dish, form=form)

# Detailed view of dish - allows place to leave a review and make dish modifications 
@app.route('/dish/<int:dish_id>', methods=['GET','POST'])
@customer_only
def dish(dish_id):
    if str(dish_id) not in session:
        session[str(dish_id)]={}
    session['CurrentDish'] = dish_id
    now = datetime.now()
    form = submitModifications()
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM dish WHERE dish_id=%s',(dish_id,))
    dish=cur.fetchone()
    dishPhoto=dish['dishPic']
    path = "/static/picture/" + str(dishPhoto)
    dish_id=dish['dish_id']
    cur.execute("SELECT * FROM dish_ingredient JOIN ingredient ON dish_ingredient.ingredient_id = ingredient.ingredient_id  WHERE dish_ingredient.dish_id=%s",(dish_id,))
    result=cur.fetchall()
    cur.execute("SELECT * FROM reviews WHERE dish_id=%s",(dish_id,))
    reviews = cur.fetchall()
    cur.execute("SELECT comment, rating FROM reviews WHERE dish_id=%s",(dish_id,))
    comments=cur.fetchall()
    
    for value in result:
        ingredient_id=value['ingredient_id']
        if ingredient_id not in session[str(dish_id)]:
            session[str(dish_id)][ingredient_id] =1
    if form.validate_on_submit():
        changes = ''
        cur.execute('SELECT * FROM dish_ingredient WHERE dish_id=%s',(dish_id,))
        ingredients=cur.fetchall()
        for ingredient in ingredients:
            ingredient_id = ingredient['ingredient_id']
            cur.execute("SELECT * FROM ingredient WHERE ingredient_id=%s",(ingredient_id,))
            ing_name=cur.fetchone()['name']
            if ingredient_id not in session[str(dish_id)]:
                session[str(dish_id)][ingredient_id] =1
            else:
                quantity=session[str(dish_id)][ingredient_id]
                changes+= str(ing_name) + ":" + str(quantity) + " "
                session[str(dish_id)][ingredient_id] =1
        cur.execute("INSERT INTO modifications(dish_id,notes,user) VALUES(%s,%s,%s)",(dish_id,changes,g.user))
        mysql.connection.commit()
        session['CurrentDish'] = None
        return redirect(url_for('add_to_cart', dish_id=dish['dish_id']))
    return render_template('customer/dish.html', dish=dish,result=result,form=form,quant=session[str(dish_id)],comments=comments,reviews=reviews)

# Increase the amount of an ingredient in a dish
@app.route('/inc_quantity_ingredient/<int:ingredient_id>')
@customer_only
def inc_quantity_ingredient(ingredient_id):
    cur = mysql.connection.cursor() 
    dish_id = session['CurrentDish']
    cur.execute("SELECT * FROM dish_ingredient WHERE ingredient_id=%s",(ingredient_id,))
    result=cur.fetchone()
    if ingredient_id not in session[str(dish_id)]:
        session[str(dish_id)][ingredient_id] = 1
    session[str(dish_id)][ingredient_id] = session[str(dish_id)][ingredient_id] +1
    return redirect(url_for('dish',dish_id=dish_id))

# Decrease the amount of an ingredient in a dish
@app.route('/dec_quantity_ingredient/<int:ingredient_id>')
@customer_only
def dec_quantity_ingredient(ingredient_id):
    cur = mysql.connection.cursor()
    dish_id = session['CurrentDish']
    cur.execute("SELECT * FROM dish_ingredient WHERE ingredient_id=%s",(ingredient_id,))
    result=cur.fetchone()
    if ingredient_id not in session[str(dish_id)]:
        session[str(dish_id)][ingredient_id] = 1
    if session[str(dish_id)][ingredient_id] !=0:
        session[str(dish_id)][ingredient_id] = session[str(dish_id)][ingredient_id] -1
    return redirect(url_for('dish',dish_id=dish_id))

# Place for customers to view all the menu items they've added to their order
@app.route('/cart')
@customer_only
def cart():
    cur = mysql.connection.cursor()
    cur.execute('select * from dish;')
    dishes=cur.fetchall()
    dish=''
    full = 0
    if 'cart' not in session:
        session['cart'] = {}
    names = {}
    modifications={}
    for dish_id in session['cart']:
        cur.execute('SELECT * FROM dish WHERE dish_id=%s LIMIT 1;',(dish_id,))
        name = cur.fetchone()['name']
        names[dish_id] = name
        cur.execute(' SELECT * FROM dish WHERE dish_id=%s; ',(dish_id,))
        dish = cur.fetchone()
        cur.execute(' SELECT * FROM dish WHERE dish_id=%s',(dish_id,))
        cost = cur.fetchone()['cost']
        quantity = session['cart'][dish_id]
        full+= (int(cost) *int(quantity))
        cur.execute("SELECT * FROM modifications WHERE dish_id=%s AND user=%s",(dish_id,g.user))
        mods = cur.fetchall()
        list = []
        for vals in mods:
            changes =vals['notes']
            list.append(changes)
        modifications[dish_id] = list
    return render_template('customer/cart.html', cart=session['cart'], dishes=dishes,mods=modifications,names=names, dish=dish, full=full)

# Adds the default item to cart
@app.route('/add_default_meal/<int:dish_id>')
@customer_only
def add_default_meal(dish_id):
    cur = mysql.connection.cursor()
    if 'cart' not in session:
        session['cart'] = {}
    if dish_id not in session['cart']:
        session['cart'][dish_id] = 0
    session['cart'][dish_id]=session['cart'][dish_id]+1
    changes=""
    cur.execute("SELECT * FROM dish_ingredient JOIN ingredient ON dish_ingredient.ingredient_id = ingredient.ingredient_id  WHERE dish_ingredient.dish_id=%s",(dish_id,))
    result=cur.fetchall()
    for value in result:
        name=value['name']
        changes+=str(name)+":" "1 "
    cur.execute("INSERT INTO modifications(dish_id,notes,user) VALUES(%s,%s,%s)",(dish_id,changes,g.user))
    mysql.connection.commit()
    return redirect(url_for('cart'))

@app.route('/add_to_cart/<int:dish_id>')
@customer_only
def add_to_cart(dish_id):
    if 'cart' not in session:
        session['cart'] = {} 
    if dish_id not in session['cart']:
        session['cart'][dish_id] = 0
    session['cart'][dish_id]= session['cart'][dish_id] + 1
    return redirect( url_for('cart') ) 

# Remove a specific modification from cart based on the changes made and the dish_id
@app.route('/remove_specific/<string:changes>/<int:dish_id>')
@customer_only
def remove_specific(changes,dish_id):
    if changes=="":
        if dish_id not in session['cart']:
            session['cart'][dish_id]=0
        if session['cart'][dish_id] >1:
            session['cart'][dish_id] = session['cart'][dish_id] -1
        return redirect(url_for('cart')) 
    cur = mysql.connection.cursor()
    cur.execute("Select * FROM modifications WHERE user=%s AND notes=%s AND dish_id=%s",(g.user,changes,dish_id))
    modificationId = cur.fetchone()['modifications_id']
    cur.execute('DELETE FROM modifications WHERE modifications_id=%s',(modificationId,))
    mysql.connection.commit()
    if dish_id not in session['cart']:
        session['cart'][dish_id]=0
    if session['cart'][dish_id] >1:
        session['cart'][dish_id] = session['cart'][dish_id] -1
    elif session['cart'][dish_id] ==1:
        session['cart'].pop(dish_id)
    return redirect(url_for('cart'))

# Completely clears cart of any orders
@app.route('/clearCart')
@customer_only
def clearCart():
    cur = mysql.connection.cursor()
    for dish_id in session['cart']:
        cur.execute('DELETE FROM modifications where dish_id=%s',(dish_id,))
        mysql.connection.commit()
    session['cart'].clear()

    return redirect(url_for('cart'))

# Deletes all menu items with specified dish_id
@app.route('/remove/<int:dish_id>')
@customer_only
def remove(dish_id):
    cur = mysql.connection.cursor()
    if dish_id not in session['cart']:
        session['cart'][dish_id] = 0
    for dishId in session['cart'].copy():
        if dish_id == int(dishId):
            session['cart'].pop(dishId)
    cur.execute('DELETE FROM modifications where dish_id=%s',(dish_id,))
    mysql.connection.commit()
    return redirect(url_for('cart'))

# Allows user to pay for items selected
@app.route('/checkout', methods=['GET','POST'])
@customer_only
def checkout():
    cur = mysql.connection.cursor()
    full =0
    form = cardDetails()
    names = {}
    username = g.user
    cur.execute('select * from dish')
    dishes = cur.fetchall()

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

    cur.execute("SELECT * FROM transactions WHERE username=%s;",(username,))
    transactions = cur.fetchall()
    discount=False
    if len(transactions) % 10 == 0 and len(transactions) > 1:
        discount=True

    if form.validate_on_submit():
        cardNum=form.cardNum.data
        cardHolder = form.cardHolder.data
        cvv = form.cvv.data
        tableNum=form.tableNum.data
        date = datetime.now().strftime(' %d-%m-%y')
        now = datetime.now()
        for dish_id in session['cart']:
            cur.execute('SELECT * FROM modifications WHERE dish_id=%s AND user=%s',(dish_id,g.user))
            result = cur.fetchall()
            for values in result:
                cur.execute('SELECT * FROM dish WHERE dish_id=%s',(dish_id,))
                currentDish=cur.fetchone()
                cost=currentDish['cost']
                changes=values['notes']
                cur.execute('INSERT INTO transactions(username, dish_id,cost,quantity,date) VALUES(%s,%s,%s,%s,%s) ',(username, dish_id,cost,1,date))
                mysql.connection.commit()

                cur.execute("INSERT INTO orders(time,dish_id,notes,table_id,status) VALUES(%s,%s,%s,%s,%s)",(now,dish_id,changes,tableNum,"ordered"))

                mysql.connection.commit()
        cur.execute('DELETE FROM modifications WHERE user=%s',(g.user,))
        mysql.connection.commit()    
        session['cart'].clear()
        cur.execute("""INSERT INTO notifications (user, title, message)
                        VALUES (%s, "Order Confirmed!","Your order is in preparation, thank you!");""", (g.user,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('menu'))
    return render_template('customer/checkout.html', cart=session['cart'],form=form,full=full,names=names,dish=dish,dishes=dishes)


##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
'''
            ALL FEATURES BELOW ARE RELATED TO THE CUSTOMER RESERVATION FEATURE
'''
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################

# allows customer to book a table for a date and time
@app.route('/booking',methods=['GET', 'POST'])
@customer_only
def booking():
    form = makeBooking()
    if form.validate_on_submit():
        name = form.name.data
        date = form.date.data
        date = date.strip()
        valid = True
        
        day = date[:2]
        month = date[3:5]
        year = date[6:]
        current_day = datetime.now().strftime("%d")
        current_month = datetime.now().strftime("%m")
        current_year = datetime.now().strftime("%Y")[2:]
        
        if not (len(date) == 8 and int(date[:2]) > 0 and int(date[:2]) < 32 
            and int(date[3:5]) > 0 and int(date[3:5]) < 13
            and int(date[6:]) >= 23 and date[2] == "-" and date[5] == "-"):
            form.date.errors.append('Invalid date given, use DD-MM-YY.')
            valid = False
        elif int(year+month+day) < int(current_year+current_month+current_day):
            form.date.errors.append('Please pick a date in the future for booking.')
            valid = False
        else:
            date = year+"-"+month+"-"+day
            time = form.time.data
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM tables')
            tables = cur.fetchall()
            
            day = datetime(2000+int(year), int(month), int(day)).weekday()
            days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
            cur.execute('SELECT * FROM shift_requirements WHERE day = %s',(days[day],))
            hours = cur.fetchall()[0]
            if time < hours['opening_time'] and time+2 > hours['closing_time']:
                form.time.errors.append('Invalid time given, please try another!')
                valid = False
            
            cur.execute('SELECT * FROM bookings WHERE time = %s AND date = %s',(time, date))
            hour_1 = cur.fetchall()
            cur.execute('SELECT * FROM bookings WHERE time = %s AND date = %s',(time-1, date))
            hour_0 = cur.fetchall()
            cur.execute('SELECT * FROM bookings WHERE time = %s AND date = %s',(time+1, date))
            hour_2 = cur.fetchall()
        
            if len(hour_1) >= len(tables) or len(hour_2) >= len(tables) or len(hour_0) >= len(tables) and valid:
                form.time.errors.append('We are fully booked at this time, please try another!')
                valid = False
                    
            if valid:
                cur.execute('SELECT * FROM customer WHERE email = %s',(g.user,))
                customer_details = cur.fetchall()
                if len(customer_details) == 0:
                    customer_id = 0
                else:
                    customer_id = customer_details[0]['customer_id']
                    
                table_id = 0
                for table in tables:
                    available = True
                    # reservation is 2 hours
                    for reservations in hour_0: # check is second hour booked
                        if table['table_id'] == reservations['table_id']:
                            available = False
                    for reservations in hour_1: # check is time booked
                        if table['table_id'] == reservations['table_id']:
                            available = False
                    for reservations in hour_2: # check would second hour clash with a booking
                        if table['table_id'] == reservations['table_id']:
                            available = False
                    if available:
                        table_id = table['table_id']
                    
                cur.execute('INSERT INTO bookings(booker_id,table_id,name,date,time) VALUES(%s,%s,%s,%s,%s) ',(customer_id, table_id,name,date,time))
                    
                mysql.connection.commit()
                
                subject = "Booking Confirmation"
                email = customer_details[0]['email']
                message = f"""
                Dear {name}
                
                Thank you for booking with Michelin Star!
                
                Your booking is confirmed for 20{date} at {time}.
                We have you booked for a duration of 2 hours.
                
                We look forward to seeing you!
                """
                msg = Message(subject, sender=credentials.flask_email, recipients=[email])   
                msg.body = f"""
                From: Booking Confirmation no reply <{credentials.flask_email}>
                {message}
                """
                mail.send(msg)

                cur.execute('SELECT booking_id FROM bookings WHERE time = %s AND date = %s AND booker_id = %s',(time, date, customer_id))
                booking = cur.fetchall()
                booking_id = booking[0]['booking_id']

                return redirect(url_for('cancel_bookings'))
    return render_template('customer/booking.html', form=form)

# menu where customers' bookings can be cancelled
@app.route('/cancel_bookings', methods=['GET','POST'])
@customer_only
def cancel_bookings():
    cur = mysql.connection.cursor()
    cur.execute('SELECT customer_id FROM customer WHERE email = %s',(g.user,))
    customer_id = cur.fetchall()[0]['customer_id']
    
    current_day = datetime.now().strftime("%d")
    current_month = datetime.now().strftime("%m")
    current_year = datetime.now().strftime("%Y")
    date = current_year+"-"+current_month+"-"+current_day

    cur.execute('SELECT * FROM bookings WHERE booker_id = %s and date >= %s',(customer_id,date))
    bookings = cur.fetchall()
    return render_template('customer/cancel_booking.html', bookings=bookings)

# cancels a customers' booking
@app.route('/cancel_booking/<int:booking_id>', methods=['GET','POST'])
@staff_only
def cancel_booking(booking_id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM bookings WHERE booking_id = %s',(booking_id,))
    mysql.connection.commit()
    cur.execute("""INSERT INTO notifications (user, title, message)
                        VALUES (%s, "Reservation Cancelled","Your reservation booking ID %s has been cancelled");""", (g.user, booking_id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('cancel_bookings'))

#Allows all staff to view the breaklist for each individual day
@app.route('/breaks', methods=['GET','POST'])
@staff_only
def breakTimes():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM staff')
    staff = cur.fetchall()
    cur.execute("SELECT * FROM roster")
    roster = cur.fetchall()
    now = datetime.now()
    day = (now.strftime("%a")).lower()
    breaksAssigned = {}
    workingToday = {}
    for working in roster:
        if working[day] != '':
            shift = working[day]
            workingToday[working['staff_id']] =shift
    numWorkers = len(workingToday)
    k= 0
    while k <2:
        assigned = 0
        for employee in workingToday:
            if k == 0:
                shift = workingToday[employee]
                hoursWorking= int(shift[0]+shift[1]) - int(shift[6]+shift[7])

                hoursWorking = hoursWorking*-1
                if hoursWorking >4 and hoursWorking >= 8:
                    breaks = 2
                    workingToday[employee] = [shift,breaks]
                elif hoursWorking >4:
                    breaks=1
                    workingToday[employee] = [shift,breaks]
                else: 
                    breaks =0
                    assigned +=1
                    workingToday.append("-")
                start = int(shift[0]+shift[1])
                endShift = int(shift[6] + shift[7])
                proposedBreak = 0
            else:
                start = workingToday[employee][2]
            proposedBreak = 0
            for j in range(4,1,-1):

                if workingToday[employee][1] ==1 and len(working[employee] >=3):
                    break
                proposedBreak = start + j
                if proposedBreak in breaksAssigned: 
                    proposedBreak = 0
                elif proposedBreak  >= endShift or (proposedBreak) >= endShift -1:
                    proposedBreak =0
                else:
                    breaksAssigned[proposedBreak] =1
                    start = start +j
                    endBreak = start +0.45
                    workingToday[employee].append(start)
                    assigned +=1
                    break
        i = 2
        while assigned != len(workingToday):
            for employee in workingToday:
                shift = workingToday[employee][0]
                start = int(shift[0]+shift[1])
                endShift = int(shift[6] + shift[7])
                if k == 1:
                    start = workingToday[employee][2]
                if (len(workingToday[employee]) <3 and k ==0) or (len(workingToday[employee]) <4 and k==1):
                    for j in range(4,1,-1):
                        if workingToday[employee][1] ==1 and len(working[employee] >3): 
                            break
                        proposedBreak = start + j
                        if proposedBreak in breaksAssigned and breaksAssigned[proposedBreak] >=i: 
                            proposedBreak = 0
                        elif proposedBreak  >= endShift or (proposedBreak) >= endShift -1:
                            proposedBreak =0
                        elif proposedBreak == start:
                            proposedBreak = 0
                        else:
                            if proposedBreak not in breaksAssigned:
                                breaksAssigned[proposedBreak] = 1
                            else:
                                breaksAssigned[proposedBreak] +=1
                            start = start +j
                            endBreak = start +0.45
                            workingToday[employee].append(start)
                            assigned +=1
                            break
                        if k ==1:
                            proposedBreak =start+ 0.3 +j
                            if proposedBreak in breaksAssigned and breaksAssigned[proposedBreak] >=i: 
                                proposedBreak = 0
                            elif proposedBreak  >= endShift or (proposedBreak) >= endShift -1:
                                proposedBreak =0
                            elif proposedBreak == start:
                                proposedBreak = 0
                            else:
                                if proposedBreak not in breaksAssigned:
                                    breaksAssigned[proposedBreak] = 1
                                else:
                                    breaksAssigned[proposedBreak] +=1
                                start = proposedBreak
                                endBreak = start +0.45
                                workingToday[employee].append(start)
                                assigned +=1
                                break
            i +=1
        k +=1
    print(workingToday)
    for employee in workingToday:
        if len(workingToday[employee]) >= 3:
            workingToday[employee][2] = str(workingToday[employee][2]) + ":00"

            if len(workingToday[employee]) ==4:
                string =str(workingToday[employee][3])
                print(string)
                if len(string)>2:
                    workingToday[employee][3] = (str(workingToday[employee][3]))[0]  +(str(workingToday[employee][3]))[1] + ":" + (str(workingToday[employee][3]))[3] + "0"
                else:
                    workingToday[employee][3] = str(workingToday[employee][3]) + ":00"
    return render_template("staff/breaks.html",staff=staff, workingToday=workingToday)

if __name__ == '__main__':
    app.run(debug=True)
