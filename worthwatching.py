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

ROLLOVER_HOUR = 9

def get_game(gameid):
    return Game.objects(gameid = gameid).first()

def get_games_by_date(date):
    """Get games starting on this date in EST."""
    target_date = est.localize(datetime.datetime.combine(date, datetime.time())) \
        .astimezone(pytz.utc)
    next_date = target_date + datetime.timedelta(days=1)
    return Game.objects(Q(start__gte = target_date) & Q(start__lt = next_date)) \
        .order_by('start')

def annotate(game):
    game.est = pytz.utc.localize(game.start).astimezone(est).time().strftime('%-I:%M %p')
    ratings = Review.objects(game = game)
    game.ratings = {
        'avg': int(round(ratings.average('rating'))) if ratings else None
    }
    return game

@app.route('/')
def show_todays_games():
    now_est = datetime.datetime.now(est)
    now_est = now_est.replace(month=3) # Shift date for offseason development
    today_est = now_est.date()
    if now_est.hour < ROLLOVER_HOUR:
        today_est -= datetime.timedelta(days=1)
    games = get_games_by_date(today_est)
    return flask.render_template('games.html', games = map(annotate, games))

@app.route('/<int:year>/<int:month>/<int:day>')
def show_games(year, month, day):
    games = get_games_by_date(datetime.date(year, month, day))
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
