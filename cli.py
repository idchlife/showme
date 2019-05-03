import traceback
import hashlib
import datetime
from pathlib import Path
import secrets
import clrc
import click
from app.config import LOG_PATH, CONFIG_PATH, DATABASE_PATH
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
  clrc.info("Welcome to ShowMe program, which will output your log files to the browser!")
  clrc.info("To view list of available commands just type `showme` press enter and see the list.")


@click.command()
@click.option("--reinstall/--no-reinstall", default=False)
def init(reinstall: bool):
  if Path(CONFIG_PATH).exists() and not reinstall:
    clrc.info("It seems config file already exists. You either already initialized program, or created config file manually. If you want to reinstall program, use --reinstall flag")
    return

  if Path(CONFIG_PATH).exists() and reinstall:
    click.confirm("You are going to reinstall program configuration. This will stop daemon (if it is working) and wipe database with rows for users and logs (your actual log files won't be affected). Are you sure?", abort=True)

    clrc.info("Stopping daemon...")
    stop_flask_server()

    if Path(CONFIG_PATH).exists():
      Path(CONFIG_PATH).unlink()
      clrc.info("Config file removed...")
    if Path(DATABASE_PATH).exists():
      Path(DATABASE_PATH).unlink()
      clrc.info("Database removed...")

    clrc.success("Done! Now, to initializing program...")

    clrc.info("Initializing...")

  cfg = """SECRET_KEY={0}
HOST=0.0.0.0
PORT=4020
""".format(hashlib.md5(
    (secrets.token_urlsafe(64) + str(datetime.datetime.now())).encode("utf-8")
  ).hexdigest())

  Path(CONFIG_PATH).write_text(cfg)

  clrc.success("Config file created and filled with some default parameters. More information about config parameters you can see at the documentation")

  clrc.info("You can now use `user create` command to create first user, `log create` command to add log and `daemon start` command to start web server")
  clrc.info("Would you like to know more? Use `help` command")
  


@cli.group()
def daemon():
  pass


@click.command()
@click.option("--debug/--no-debug", default=False)
def start(debug: bool):
  start_flask_server(daemonize=True, debug=debug)


@click.command()
def stop():
  stop_flask_server()


@click.command()
@click.option("--debug/--no-debug", default=False)
def restart(debug: bool):
  stop_flask_server()
  start_flask_server(debug=debug)



daemon.add_command(start)
daemon.add_command(stop)
daemon.add_command(restart)


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


@click.command("create")
@click.option("--user", required=False, type=str)
def add_log(user: str):
  if user:
    user = find_user(user)
    if not user:
      clrc.info("User with provided username not found. Aborting")
      return

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

    if not user:
      click.confirm("You are going to add log file for all users, without specifying --user=USERNAME option. It will be accessible by all users. Proceed?", abort=True)
      add_log_file(name, filepath)
      clrc.success("Log file added for everyone")
    else:
      add_log_file(name, filepath, user)
      clrc.success("Log file added for user {0}".format(user.username))


  except:
    clrc.warn("There seems to be the problem with opening file with the provided path. Here is more debug info for you to possibly discover source of the problem:")
    clrc.error(traceback.format_exc())


log.add_command(add_log)


cli.add_command(help)
cli.add_command(init)


if __name__ == "__main__":
  try:
    cli()
  except SystemExit:
    # NOTE: for not logging plain SystemExit, which means well, that cli has ended it's lifecycle. That's all
    pass
  except:
    clrc.warn("Unfortunately, major error occurred while executing command. Here is more info:")
    clrc.error(traceback.format_exc())
