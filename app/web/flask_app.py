import os
from pathlib import Path
from flask import Flask


app = Flask(__name__)


ASSETS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "assets")


def render_asset(filename: str, type: str):
  filepath = os.path.join(ASSETS_DIR, filename)

  if not Path(filepath).exists():
    raise Exception("Asset file {0} does not exist".format(filename))

  contents = Path(filepath).read_text()

  return """
<{0}>
{1}
</{0}>
""".format(type, contents)


@app.context_processor
def inject_add_css():
  def add_css(filename: str):
    return render_asset(filename, "style")
  return dict(add_css=add_css)


@app.context_processor
def inject_add_js():
  def add_js(filename: str):
    return render_asset(filename, "script")
  return dict(add_js=add_js)
