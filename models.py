import datetime
from mongoengine import *

class Game(Document):
    gameid = LongField(required = True) # e.g. 2013020920
    start = DateTimeField(required = True)
    home_team = StringField(required = True)
    away_team = StringField(required = True)

    meta = {
        'allow_inheritance': True,
        'indexes': ['-gameid']
    }

class Review(Document):
    created_at = DateTimeField(default = datetime.datetime.now, required = True)
    timespan = IntField(required = True)
    game = ReferenceField(Game, required = True)
    rating = IntField(required = True)

    meta = {
        'allow_inheritance': True,
        'indexes': ['-game', '-created_at']
    }
