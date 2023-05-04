from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

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
        
        return redirect(f"/users/{new_user.username}")
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
            return redirect(f"/users/{user.username}")  
        # note you neeed to figure out how to put the username into the http string 
        else:
            form.username.errors =  ["Bad username/password"]
    return render_template("login.html", form=form)

@app.route("/users/<username>")
def secret_page(username):
    """Displays secret page"""
    # raise ValueError(user)
    user = User.query.get_or_404(username)
    all_feedback = Feedback.query.all()
    if "username" not in session:
        flash("Please login to continue!", "info")
        # this flash doesnt appear to be working
        return redirect("/")

    else:
        return render_template("user_info.html", username=username, user=user, all_feedback=all_feedback)
    
@app.route('/users/<username>/feedback/add', methods=["GET", "POST"]) 
def add_feedback(username):
    """Displays feedback form"""
    user = User.query.get_or_404(username)
    form = FeedbackForm()
    all_feedback = Feedback.query.all()
    # raise ValueError(all_feedback)
    if "username" not in session:
        flash("Please login to continue!", "danger")
        return redirect("/login")
    if form.validate_on_submit():
        # all_feedback = Feedback.query.all()
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, content=content, username=session["username"])
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback Accepted!', 'success')
        return redirect(f"/users/{user.username}")
    return render_template('feedback.html', form=form, all_feedback=all_feedback)
    
@app.route('/feedback/<feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Displays Update Feedback Form"""
    username = session['username']
    user = User.query.get_or_404(username)
    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash('Update Accepted!', 'success')
        return redirect(f"/users/{user.username}")
    
    return render_template('update.html', form=form)

@app.route('/feedback/<feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Deletes Feedback"""
    feedback = Feedback.query.filter_by(id=feedback_id).first()
    user = feedback.user
    # if "username" not in session:
    if session['username'] != user.username:
    # if I try access this route through the url I just get method not allowed which is not particularly helpful
        # raise ValueError("username")
        flash("Please login to continue!")
        return redirect("/login")
    if session['username'] == user.username:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f"/users/{user.username}")
    flash("You don't have permission to do that!", "danger")
    return redirect(f"/users/{user.username}")

    
    
    
    
@app.route('/logout')
def logout_user(): 
    """Logs user out"""
    session.pop('username')
    return redirect('/')
    