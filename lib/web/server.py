from .flask_app import app
from . import views
from . import api
from .login import login_manager


app.config['SECRET_KEY'] = "super-secret-key"

login_manager.init_app(app)
