import sh
import re
import clrc
from flask import request, jsonify
from werkzeug.exceptions import NotFound
from .flask_app import app
from .tools import find_log_file_by_id


@app.route("/api/read-log/<id>")
def read_log(id: int):
  log = find_log_file_by_id(id)

  if not log:
    raise NotFound()

  filepath = log.filepath

  lines: str = sh.tail("-n200", filepath)

  lines = lines.split("\n")

  ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
  lines = [ansi_escape.sub('', line) for line in lines]

  # clrc.info("Splitted lines: ")
  # clrc.info(lines)

  data = [
    "2019-04-28 13:53:36.694 | INFO     | clrc.printers.loguru_printer:info:15 - SMS COOLDOWN FOR 79964716158 LEFT 0",
    "2019-04-28 12:07:47.668 | SUCCESS  | clrc.printers.loguru_printer:success:9 - Success sending typed email!",
    "2019-04-28 13:53:23.992 | ERROR    | clrc.printers.loguru_printer:error:21 - Traceback (most recent call last):"
  ]

  return jsonify(lines)
