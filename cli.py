import traceback
from pathlib import Path
import clrc
import click
from app.config import LOG_PATH
from app.flask_daemon import start_flask_server, stop_flask_server
from app.web.tools import (create_user,
                           User,
                           find_user,
                           get_all_users,
                           add_log_file,
                           get_all_log_files)


@click.group()
def cli():
  pass


@click.command()
def help():
  clrc.info("Help command")


@cli.group()
def daemon():
  pass


@click.command()
def start():
  start_flask_server(daemonize=True)


@click.command()
def stop():
  stop_flask_server()


daemon.add_command(start)
daemon.add_command(stop)


@cli.group()
def user():
  pass


@click.command("create")
def create_user_cmd():
  username: str = click.prompt("Please enter username")

  if not username.strip():
    clrc.info("No username provided")
    return

  existing = find_user(username)

  if existing:
    clrc.info("User already exists")
    return

  password: str = click.prompt("Please enter password", hide_input=True)

  if not password.strip():
    clrc.info("No password provided")
    return

  create_user(username, password)

  clrc.success("User {0} created! User can now login with provided credentials".format(username))


@click.command("list")
def list_users():
  users = get_all_users()

  user: User
  for i, user in enumerate(users):
    clrc.info("{0}: {1}".format(i, user.username))

  clrc.info("Total {0} users".format(len(users)))


@click.command("delete")
def delete_user():
  username: str = click.prompt("Please provide username to delete user")

  if not username.strip():
    clrc.info("No username provided")
    return

  user = find_user(username)

  if not user:
    clrc.info("User not found")
    return

  click.confirm("Are you sure you want to delete user {0}?".format(username), abort=True)
  #TODO: write user deletion

  clrc.success("User deleted!")


user.add_command(create_user_cmd)
user.add_command(delete_user)
user.add_command(list_users)


@cli.group()
def log():
  pass


@click.command("add")
def add_log():
  filepath: str = click.prompt("Please enter absolute path for log file")

  if not filepath.strip():
    clrc.info("No path provided")
    return

  if LOG_PATH == filepath:
    clrc.info("Sorry, you cannot add log file of showme daemon to the logs. It creates eternal recursion, will eat up your space and speed up your fans :D")
    return

  try:
    with open(filepath, "r") as file:
      file.read(1)

    name: str = click.prompt("Please enter name for your log")

    if not name.strip():
      clrc.info("No name provided")
      return

    add_log_file(name, filepath)

    clrc.success("Log file added")

  except:
    clrc.warn("There seems to be the problem with opening file with the provided path. Here is more debug info for you to possibly discover source of the problem:")
    clrc.error(traceback.format_exc())


log.add_command(add_log)


cli.add_command(help)


if __name__ == "__main__":
  try:
    cli()
  except SystemExit:
    # NOTE: for not logging plain SystemExit, which means well, that cli has ended it's lifecycle. That's all
    pass
  except:
    clrc.warn("Unfortunately, major error occurred while executing command. Here is more info:")
    clrc.error(traceback.format_exc())
