from flask import Flask, render_template, redirect, url_for, session, g, request, make_response, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, ContactForm, ReplyForm, EmployeeForm
from functools import wraps
from flask_mysqldb import MySQL 
from flask_mail import Mail, Message
from datetime import datetime
import random
import string

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
    g.user = session.get("email", None)

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

def manager_only(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        g.user = session.get("role", None)
        if g.user != "Manager":
            return redirect(url_for("home"))
        return view(**kwargs)
    return wrapped_view


@app.route("/auto_login_check", methods=["GET","POST"])
def auto_login_check():
    if request.cookies.get("email"):
        session.clear()
        session["email"] = request.cookies.get("email")
        next_page = request.args.get("next")
        if not next_page:
            return redirect("home")
        else:
            return redirect( next_page )
    return redirect( "login" )


@app.route("/delete_cookie/<cookie>",methods=["GET","POST"])
def delete_cookie(cookie):
    response = redirect(url_for('home'))
    response.set_cookie(cookie, '', expires=0)
    return response

@app.route("/logout", methods=["GET","POST"])
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html"),404

@app.route("/", methods=["GET","POST"])
def index():
    """
    start route must be "/", directs straight to home page 
    """
    return redirect("home")

@app.route("/home", methods=["GET","POST"])
def home():     
    return render_template("home.html")

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
        code = "None" # this is for my 'forgot password' idea that I'd upload later

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
            return redirect( url_for("login"))

            response = make_response(redirect("auto_login_check"))
            response.set_cookie("email",email,max_age=(60*60*24))
            return response
    return render_template("accounts/registration.html", form=form, title="Registration")

# Login to account
@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = db.execute("SELECT password FROM login WHERE username = ?",(username,)).fetchone()
        if user is not None:
            if not check_password_hash(user["password"],password ):
                form.password.errors.append("Incorrect password")
            else:
                session.clear()
                session["username"] = username
                next_page = request.args.get("next")
                if not next_page:
                    response = make_response( redirect( url_for('home')) )
                else:
                    response = make_response( redirect(next_page) )
                response.set_cookie("username",username,max_age=(60*60*24*7))
                return response
    return render_template("accounts/login.html", form=form, title="Login")

# Main profile
@app.route("/profile")
@login_required
def profile():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customer WHERE email = %s", (g.user,))
    user = cur.fetchone()
    return render_template("profile.html", title="My Profile", user=user)

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
        date = datetime.now().date()

        cur.execute("""INSERT INTO user_queries (name, email, subject, message, date)
                        VALUES (%s,%s,%s,%s,%s);""", (name, email, subject, message, date))
        mysql.connection.commit()

        msg = Message(subject, sender='no.reply.please.and.thank.you@gmail.com', recipients=['no.reply.please.and.thank.you@gmail.com'])   
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
    return render_template("manager/dashboard.html")

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
        
        # Notify employee's email about their new account
        message = "Please sign into your account with your email and password:" + password
        msg = Message("Welcome on board! We're happy you joined us.", sender='no.reply.please.and.thank.you@gmail.com', recipients=[email])   
        msg.body = f"""{message}"""
        mail.send(msg)
        
        flash ("New employee successfully added!")
        return redirect(url_for("view_all_employees"))
    return render_template("manager/new_staff_form.html", form=form, title="Add New Employee")   

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








if __name__ == '__main__':
    app.run(debug=True)