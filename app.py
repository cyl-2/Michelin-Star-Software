from flask import Flask, render_template, redirect, url_for, session, g, request, make_response
from database import get_db,close_db
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
from functools import wraps

app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.teardown_appcontext
def close_db_at_end_of_request(e=None):
    close_db(e)

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

"""

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        surname = form.surname.data
        icon = form.icon.data
        db = get_db()
        if db.execute("SELECT username FROM login WHERE username = ?",(username,)).fetchone() is not None:
            form.username.errors.append("Username already taken")
            db.execute("INSERT INTO errors (username,error) VALUES (NULL,'Username already taken');")
            # Table that holds errors made by users for admin to see
            db.commit()
        else:
            db.execute("INSERT INTO login (username, password, first_name, surname, icon ) VALUES (?,?,?,?,?)",(username, generate_password_hash(password),first_name,surname,icon))
            db.commit()

            response = make_response(redirect("auto_login_check"))
            response.set_cookie("username",username,max_age=(60*60*24*7))
            return response
    return render_template("register.html",form=form)


@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        db = get_db()
        user = db.execute("SELECT password FROM login WHERE username = ?",(username,)).fetchone()
        if user is None:
            form.username.errors.append("Not a valid user")
            db.execute("INSERT INTO errors (username,error) VALUES (NULL,'Not a valid user');")
            db.commit()
        elif not check_password_hash(user["password"],password ):
            form.password.errors.append("Incorrect password")
            db.execute("INSERT INTO errors (username,error) VALUES (?,'Incorrect password');",(g.user,))
            db.commit()
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
    return render_template("login.html",form=form)


@app.route("/auto_login_check", methods=["GET","POST"])
def auto_login_check():
    if request.cookies.get("username"):
        session.clear()
        session["username"] = request.cookies.get("username")
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
"""