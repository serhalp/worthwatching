import sys
import json
import datetime
import pytz
import worthwatching
from models import Game

if len(sys.argv) != 2:
    print 'Usage: python import.py <SeasonSchedule.json>'
    exit(1)

filename = sys.argv[1]
schedule = json.load(open(filename))

worthwatching.init_db()

est = pytz.timezone('US/Eastern')

print 'Importing.'
for game in schedule:
    start = est.localize(datetime.datetime.strptime(game['est'], '%Y%m%d %H:%M:%S')).astimezone(pytz.utc)
    game = Game(gameid = game['id'], start = start, home_team = game['h'], away_team = game['a']).save()
print 'Done.'
