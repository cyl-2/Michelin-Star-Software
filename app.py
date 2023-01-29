from flask import Flask, render_template, redirect, url_for, session, g, request, make_response, flash, Markup
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, ContactForm, ReplyForm, EmployeeForm, ResetPasswordForm, NewPasswordForm, CodeForm, RosterRequestForm, ProfileForm, RejectRosterRequestForm
from functools import wraps
from flask_mysqldb import MySQL 
from flask_mail import Mail, Message
from datetime import datetime
import random, string, time
from random import sample

app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
app.config['MYSQL_PASSWORD'] = '' # someone's deets
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'world' # someone's deets
app.config['MYSQL_CURSORCLASS']= 'DictCursor'

mysql = MySQL(app)

@app.before_request
def logged_in():
    g.user = "cherrylincyl@gmail.com" #session.get("username", None)
    g.access = session.get("access_level", None)

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("customer_login")) #,next=request.url))
        return view(**kwargs)
    return wrapped_view

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
            flash("Successful Registration! Please login now")
            return redirect( url_for("customer_login"))

            #response = make_response(redirect("auto_login_check"))
            #response.set_cookie("email",email,max_age=(60*60*24))
            #return response
    return render_template("customer/registration.html", form=form, title="Registration")

# Login to customer account
@app.route("/customer_login", methods=["GET", "POST"])
def customer_login():
    cur = mysql.connection.cursor()
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data
        
        cur.execute("SELECT * FROM customer WHERE email = %s", (email,))
        customer = cur.fetchone()

        if 'counter' not in session:
            session['counter'] = 0

        if customer is None:
            form.email.errors.append("Email doesn't exist, please check your spelling")
        elif not check_password_hash(customer["password"], password):
            form.password.errors.append("Incorrect password")
            session['counter'] = session.get('counter') + 1
            if session.get('counter')==3:
                flash(Markup('Oh no, are you having trouble logging in? Sucks to be you')) # reset password link need to go here
                session.pop('counter', None)
        else:
            session.clear()
            session["username"] = email
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

        if 'counter' not in session:
            session['counter'] = 0

        if staff is None:
            form.email.errors.append("Email doesn't exist, please check your spelling")
        elif not check_password_hash(staff["password"], password):
            form.password.errors.append("Incorrect password")
            session['counter'] = session.get('counter') + 1
            if session.get('counter')==3:
                flash(Markup('Oh no, are you having trouble logging in? Click <a href="forgot_password">here</a> to reset your password.')) # reset password link need to go here
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
            cur.execute("""UPDATE staff SET code=%s WHERE email=%s""", (random_code,email))
            mysql.connection.commit()
            msg = Message(f"Hello, {user['first_name']}", sender='no.reply.please.and.thank.you@gmail.com', recipients=[user["email"]])
            msg.body = f"""
            Hello,
            To reset your password, enter this code: 
            {random_code}"""
            mail.send(msg)
            flash("Great news! An email containing a 5 digit code has been sent to your email account. Enter the code below!")
            return redirect(url_for("confirm_code", email=email, random_code=random_code, table=table))
    return render_template("password_management/forgot_password.html", form=form, title= "Forgot Password")

# Checks whether the code the user received corresponds to the one in the database
@app.route("/confirm_code/<email>/<random_code>/<table>", methods=["GET", "POST"])
def confirm_code(email,random_code,table):
    form = CodeForm()
    if form.validate_on_submit():
        code = form.code.data.strip()

        if code != random_code:
            form.code.errors.append("Oh no, that's not the code in your email!")
        else:
            flash("Code correct! Now you can reset your password :)")
            session["username"] = email
            return redirect(url_for("change_password", table=table))
    return render_template("password_management/confirm_code.html", form=form, title= "Confirm code")

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
    cur = mysql.connection.cursor()
    form = ProfileForm()
    profile=None
    if form.validate_on_submit():
        bio = form.bio.data
        address = form.address.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        g.user = 'cherrylincyl@gmail.com'

        cur.execute("""UPDATE staff SET address=%s, bio=%s, first_name=%s, last_name=%s
                            WHERE email=%s;""", (address, bio, first_name, last_name, g.user))
        mysql.connection.commit()
        cur.close()
        flash ("successfully updated!")
    else:
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
        
        cur.execute("""INSERT INTO staff (email, role, access_level, first_name, last_name, password)
                            VALUES (%s,%s,%s,%s,%s,%s);""", (email, role, access_level, first_name, last_name, generate_password_hash(password)))
        mysql.connection.commit()
        '''
        # Notify employee's email about their new account
        message = "Please sign into your account with your email and password:" + password
        msg = Message("Welcome on board! We're happy you joined us.", sender='no.reply.please.and.thank.you@gmail.com', recipients=[email])   
        msg.body = f"""{message}"""
        mail.send(msg)
        '''
        flash ("New employee successfully added!")
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
    return render_template("manager/reply_email.html",form=form, title="Reply", query=query)

# Delete queries from users
#@manager_only
@app.route("/view_inventory")
def view_inventory():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ingredient;")
    inventory = cur.fetchall()
    return render_template("manager/inventory.html", inventory=inventory, title="Inventory List")

if __name__ == "__main__":
    app.run()
