from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm, LoginForm


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)



@app.route("/")
def homepage():
    """Displays home page"""

    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def registration_page():
    """Displays registration page"""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()

        session['username'] = new_user.username
        
        return redirect("/secret")
    else: 
        return render_template('registration.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login_page():
    """Displays login page"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        # raise ValueError(user)
        if user:
            session['username'] = user.username 
            # raise ValueError(session['username'])
            return redirect('/secret')  
        else:
            form.username.errors =  ["Bad username/password"]
    return render_template("login.html", form=form)

@app.route("/secret")
def secret_page():
    """Displays secret page"""
    if "username" not in session:
        flash("Please login to continue!")
        return redirect("/")

    else:
        return("You made it!!!")
    
@app.route('/logout')
def logout_user(): 
    """Logs user out"""
    session.pop('username')
    return redirect('/')
    