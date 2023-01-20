from flask import Flask, render_template, redirect, url_for, session, g, request, make_response
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
#from forms import RegisterForm, LoginForm
from functools import wraps

app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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

@app.route("/take_order", methods=["GET","POST"])
def take_order():   
    if request.cookies.get("order"):
        order = request.cookies.get("order")
        return render_template("take_order.html", order=order)
    return render_template("take_order.html")

@app.route("/take_order/<meal>", methods=["GET","POST"])
def add_order(meal):
    order = []
    if request.cookies.get("order"):
        order = request.cookies.get("order")
    order.append(str(meal))
    
    response = make_response(render_template("take_order.html", order=order))
    response.set_cookie('order', order, max_age=(60*60*24))
    return response


"""

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        surname = form.surname.data
        # if username in database
            form.username.errors.append("Username already taken")
        else:
            # add user to database

            response = make_response(redirect("auto_login_check"))
            response.set_cookie("username",username,max_age=(60*60*24))
            return response
    return render_template("register.html",form=form)


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