from .flask_app import app
from . import views
from . import api
from .login import login_manager
from ..config import SECRET_KEY


app.config['SECRET_KEY'] = SECRET_KEY

login_manager.init_app(app)
