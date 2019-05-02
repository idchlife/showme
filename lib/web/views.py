from flask import render_template, redirect
from werkzeug.exceptions import NotFound
from flask_login import login_user, login_required
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired
from .flask_app import app
from .tools import validate_user, User, find_log_file_by_id, get_all_log_files


@app.route("/")
@login_required
def index():
  logs = get_all_log_files()
  return render_template("index.html", logs=logs)


@app.route("/log/<id>")
def log(id: int):
  log = find_log_file_by_id(id)

  if not log:
    raise NotFound()

  return render_template("log.html", log=log)


class LoginForm(FlaskForm):
  username = StringField(validators=[DataRequired()])
  password = PasswordField(validators=[DataRequired()])


@app.route("/login", methods=["GET", "POST"])
def login():
  form = LoginForm()

  error = None

  if form.validate_on_submit():
    user: User = validate_user(form.username.data, form.password.data)
    if user:
      login_user(user)
      return redirect("/")
    error = "Username or password incorrect"
  elif form.is_submitted():
    error = form.errors
    
  return render_template("login.html", form=form, error=error)
