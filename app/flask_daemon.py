import os
import daemon
import signal
import logging
import traceback
import pidlockfile
from pathlib import Path
import psutil
import clrc
from loguru import logger
from .web.server import app
from .config import PORT, HOST, PID_PATH, LOG_PATH, DATABASE_PATH, DEBUG


def _run_flask_app(debug=False):
  if LOG_PATH:
    logger.add(LOG_PATH, colorize=True, rotation="100mb")
    logger.opt(exception=True)

    clrc.config.add_printer(
      clrc.LoguruPrinter(logger)
    )

    clrc.info("Starting flask process..")

  app.run(host=HOST, port=PORT, debug=debug)


def start_flask_server(daemonize=True, debug=True):
  if Path(PID_PATH).exists():
    pid = int(Path(PID_PATH).read_text())

    if pid in psutil.pids():
      clrc.info("It seems daemon is already running. Use restart command to restart it")
      return
    else:
      clrc.warn("It seems daemon was not stopped correctly the last time. PID file exists, and PID inside it do not match any running process. Please remove PID file manually: {0}".format(PID_PATH))
      clrc.info("After removing PID file daemon should start as usual")
      return
      

  if daemonize:
    if debug:
      clrc.info("Information:")
      clrc.info("Database is at: {0}".format(DATABASE_PATH))
      clrc.info("Daemon process PID file is at: {0}".format(PID_PATH))
      if LOG_PATH:
        clrc.info("You specified LOG_PATH. It's at: {0}".format(LOG_PATH))
    if (_can_create_pid_file() and _can_create_logs()):
      clrc.info("Starting daemon...")
      clrc.info("Daemon started successfully. You can access your server at http://{0}:{1}".format(HOST, PORT))
      clrc.info("If you are not able to access the web server and sure this is not a problem with firewall/closed port etc, please check logs here: {0}".format(LOG_PATH))
      logger = logging.getLogger()
      logger.setLevel(logging.DEBUG)
      fh = logging.FileHandler(LOG_PATH)
      logger.addHandler(fh)

      with daemon.DaemonContext(
        pidfile=pidlockfile.PIDLockFile(PID_PATH),
        stdout=fh.stream,
        stderr=fh.stream,
        files_preserve=[
          fh.stream
        ]
      ):
        _run_flask_app()

      clrc.success("Daemon started! You can access server at {0}:{1}".format(HOST, PORT))
  else:
    _run_flask_app(debug=True)


def stop_flask_server():
  if not Path(PID_PATH).exists():
    clrc.info("It seems daemon process is not running. PID file does not exist")
    return

  pid = int(Path(PID_PATH).read_text())

  if pid not in psutil.pids():
    clrc.info("It seems daemon process is not running.")

    Path(PID_PATH).unlink()
  else:
    p = psutil.Process(pid)
    p.terminate()

    Path(PID_PATH).unlink()

    clrc.success("Daemon process stopped")


def _can_create_pid_file() -> bool:
  try:
    with open(PID_PATH, "w") as file:
      pass

    Path(PID_PATH).unlink()

    return True
  except:
    clrc.warn("Error creating pidfile for daemon. This error can give you some thoughts, why the problem appeared:")
    clrc.error(traceback.format_exc())


def _can_create_logs() -> bool:
  if not LOG_PATH:
    return True

  try:
    if Path(LOG_PATH).exists():
      with open(LOG_PATH, "r") as file:
        pass
    else:
      with open(LOG_PATH, "w") as file:
        pass

      Path(LOG_PATH).unlink()
    return True
  except:
    clrc.warn("You provided LOGS_PATH in config file, but it seems it cannot be accessed. Here is more info on the error:")
    clrc.error(traceback.format_exc())
    return False
