import datetime
import pytz
import flask
from mongoengine import *
from models import Game, Review

app = flask.Flask('worthwatching')

app.config.update(dict(
    DEBUG = True,
    MONGODB_SETTINGS = { 'DB': 'worthwatching-nhl' },
    SECRET_KEY = 'WhatIsThis'
))

est = pytz.timezone('US/Eastern')

db = None

def init_db():
    connect('worthwatching-nhl')

def get_game(gameid):
    return Game.objects(gameid = gameid).first()

def get_todays_games():
    target_date = datetime.datetime.combine(datetime.datetime.utcnow().date(), datetime.time(14))
    print 'target_date:', target_date
    next_date = target_date + datetime.timedelta(days = 1)
    print 'next_date:', next_date
    return Game.objects(Q(start__gte = target_date) & Q(start__lt = next_date))

def annotate(games):
    for game in games:
        game.est = pytz.utc.localize(game.start).astimezone(est).time().strftime('%-I:%M %p')
        game.rating = Review.objects(game = game).average('rating')
    return games

@app.route('/')
def show_games():
    games = get_todays_games()
    return flask.render_template('games.html', games = annotate(games))

@app.route('/game/<gameid>')
def show_game(gameid):
    games = [get_game(gameid)]
    return flask.render_template('games.html', games = annotate(games))

@app.route('/review')
def post_review():
    timespan = flask.request.args.get('timespan')
    game = get_game(flask.request.args.get('gameid'))
    rating = flask.request.args.get('rating')
    review = Review(game = game, rating = rating, timespan = timespan).save()
    return 'done'

if __name__ == '__main__':
    init_db()
    app.run()
