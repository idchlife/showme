import os
import dataset
from pathlib import Path
from passlib.hash import ldap_pbkdf2_sha512
from flask_login import UserMixin
from .database import db


users = db['user']


class User(UserMixin):
  def __init__(self, username: str, password: str):
    self.username = username
    self.password = password

  def get_id(self):
    return self.username


class UserAlreadyExists(Exception):
  pass


def create_user(username: str, raw_password: str):
  existing = find_user(username)
  if existing:
    raise UserAlreadyExists()

  password = ldap_pbkdf2_sha512.hash(raw_password)

  users.insert(dict(username=username, password=password))


def find_user(username: str) -> User:
  data = users.find_one(username=username)

  if data:
    return User(data['username'], data['password'])

  return None


def validate_user(username: str, raw_password: str):
  user = find_user(username)

  if not user:
    return False

  if ldap_pbkdf2_sha512.verify(raw_password, user.password):
    return user

  return False


def get_all_users():
  return [User(u['username'], u['password']) for u in users.all()]


logs = db['log']


class Log:
  def __init__(self, data):
    self.id = data['id']
    self.filepath = data['filepath']
    self.name = data['name']
    self.username = data['username'] if 'username' in data else None


def find_log_file(name: str):
  log = logs.find_one(name=name)

  return Log(log) if log else None


def find_log_file_by_id(id: int) -> Log:
  log = logs.find_one(id=id)

  return Log(log) if log else None

def add_log_file(name: str, filepath: str, user: User = None):
  existing = find_log_file(name)

  if existing:
    raise Exception("Log with this name already exists!")

  if user:
    # Available only to provided user
    logs.insert(dict(username=user.username, name=name, filepath=filepath))
  else:
    # Available for general audience
    logs.insert(dict(name=name, filepath=filepath))


def delete_log_file(name: str):
  pass


def get_all_log_files():
  return [Log(l) for l in logs.all()]
