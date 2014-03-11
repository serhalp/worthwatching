import datetime
import pytz
from flask import json
import flask
from mongoengine import *
from models import Game, Review

connect('worthwatching-nhl')

app = flask.Flask('worthwatching')

app.config.update(dict(
    DEBUG = True,
    MONGODB_SETTINGS = { 'DB': 'worthwatching-nhl' },
    SECRET_KEY = 'WhatIsThis'
))

est = pytz.timezone('US/Eastern')

def get_game(gameid):
    return Game.objects(gameid = gameid).first()

def get_todays_games():
    # Rollover at 9 AM EST (2 PM UTC)
    target_date = datetime.datetime.combine(datetime.datetime.utcnow().date(), datetime.time(14))
    next_date = target_date + datetime.timedelta(days = 1)
    return Game.objects(Q(start__gte = target_date) & Q(start__lt = next_date)) \
        .order_by('start')

def annotate(game):
    game.est = pytz.utc.localize(game.start).astimezone(est).time().strftime('%-I:%M %p')
    game.ratings = {
        'avg': int(round(Review.objects(game = game).average('rating')))
    }
    return game

@app.route('/')
def show_games():
    games = get_todays_games()
    return flask.render_template('games.html', games = map(annotate, games))

@app.route('/game/<gameid>')
def show_game(gameid):
    games = [get_game(gameid)]
    return flask.render_template('games.html', games = map(annotate, games))

@app.route('/ratings/<gameid>')
def show_json_ratings(gameid):
    game = annotate(get_game(gameid))
    return flask.jsonify(game.ratings)

@app.route('/review/<gameid>')
def post_review(gameid):
    game = get_game(gameid)
    timespan = flask.request.args.get('timespan')
    rating = flask.request.args.get('rating')
    review = Review(game = game, rating = rating, timespan = timespan).save()
    return flask.jsonify({ 'success': 1 })

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80)
