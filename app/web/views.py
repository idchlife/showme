from flask import render_template, redirect
from werkzeug.exceptions import NotFound, Forbidden
from flask_login import login_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired
from .flask_app import app
from .tools import validate_user, User, find_log_file_by_id, get_all_log_files


@app.route("/")
@login_required
def index():
  logs = get_all_log_files()

  logs = [l for l in logs if not l.username or l.username == current_user.username]

  return render_template("index.html", logs=logs)


@app.route("/log/<id>")
@login_required
def log(id: int):
  log = find_log_file_by_id(id)

  user: User = current_user

  if log.username:
    if log.username != user.username:
      raise Forbidden()

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
