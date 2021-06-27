import os
from flask import Flask

app = Flask(__name__)
app.secret_key = "testing"

# Import configuration profile based on FLASK_ENV variable - defaults to Production
if os.environ.get('FLASK_ENV') == 'development':
    app.config.from_object('config.DevelopmentConfig')
elif os.environ.get('FLASK_ENV') == 'testing':
    app.config.from_object('config.TestingConfig')
else:
    app.config.from_object('config.ProductionConfig')

# Import routes here
from app.routes import *

# Import all packages
# from app import forms
# from app import helpers
from app.models import *
# from app import settings
