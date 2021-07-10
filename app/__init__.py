import os
from flask import Flask
import pymongo

app = Flask(__name__)
app.secret_key = "testing"



# Import configuration profile based on FLASK_ENV variable - defaults to Production
if os.environ.get('FLASK_ENV') == 'development':
    app.config.from_object('config.DevelopmentConfig')
elif os.environ.get('FLASK_ENV') == 'testing':
    app.config.from_object('config.TestingConfig')
else:
    app.config.from_object('config.ProductionConfig')
    
# client = pymongo.MongoClient('localhost', 27017)
# client = pymongo.MongoClient("mongodb://fynmn:October05@cluster0-shard-00-00.2fb7q.mongodb.net:27017,cluster0-shard-00-01.2fb7q.mongodb.net:27017,cluster0-shard-00-02.2fb7q.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-192j1z-shard-0&authSource=admin&retryWrites=true&w=majority")
client = pymongo.MongoClient("mongodb://fynmn:October05@cluster0-shard-00-00.2fb7q.mongodb.net:27017,cluster0-shard-00-01.2fb7q.mongodb.net:27017,cluster0-shard-00-02.2fb7q.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-192j1z-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.get_database('election-system-test')
user_records = db.users
admins_records = db.admins
candidates_records = db.candidates
posts_records = db.posts
user_records = db.users
votes_records = db.votes
voting_status = db.voting_status

# Import routes here
from app.routes import *

# Import all packages
# from app import forms
# from app import helpers
from app.models import *
# from app import settings
