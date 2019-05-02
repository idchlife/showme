from flask import redirect
from flask_login import LoginManager
from .tools import find_user


login_manager = LoginManager()


@login_manager.user_loader
def load_user(username):
  return find_user(username)


@login_manager.unauthorized_handler
def unauthorized():
  return redirect("/login")
