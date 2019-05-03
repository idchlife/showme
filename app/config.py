import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv
import clrc


HOME_DIR = str(Path.home())

CONFIG_PATH = os.path.join(HOME_DIR, ".showme")


config_exists = Path(CONFIG_PATH).exists()

if config_exists:
  load_dotenv(CONFIG_PATH)

if not config_exists:
  clrc.info(
    "Config file does not exist. Please enter `init` command to initialize config at path: {0}".format(CONFIG_PATH)
  )

def get_env(name: str, default: str, cast_to=None):
  try:
    if not config_exists:
      return default

    value = os.getenv(name, default)

    if cast_to:
      value = cast_to(value)

    return value
  except:
    clrc.warn("Error getting {0} value from config file. Using default value: {1}".format(name, default))
    return default

try:
  PID_PATH = get_env("PID_PATH", os.path.join(HOME_DIR, ".showme.pid"))
  PORT = get_env("PORT", "4020")
  HOST = get_env("HOST", "0.0.0.0")
  DEBUG = get_env("DEBUG", "0", int) == 1
  _SECRET_KEY_DEFAULT = "NOT_SO_SECRET_RIGHT? RIGHT? GUYS?..."
  SECRET_KEY = get_env("SECRET_KEY", _SECRET_KEY_DEFAULT)
  if SECRET_KEY == _SECRET_KEY_DEFAULT:
    clrc.warn("You have default SECRET_KEY value. Please edit this in the config file at {0} to flavour your protection of csrf token".format(CONFIG_PATH))

  DATABASE_PATH = get_env("DATABASE_PATH", os.path.join(HOME_DIR, ".showme.db"))
  LOG_PATH = get_env("LOG_PATH", os.path.join(HOME_DIR, ".showme.log"))
except:
  clrc.error(
    "There was major error reading config file. Cannot continue execution. Maybe this error will give you more information"
  )
  clrc.error(traceback.format_exc())
  sys.exit(1)
