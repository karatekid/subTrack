import datetime
import json

from django.db import transaction
from django.contrib.auth.models import User
from django.test import TestCase

from .models import Player, Team, Game

# Create your tests here.
class SubTest(TestCase):
    def setUp(self):
        # Populate database
        with open('teamScheduling/teams.json') as f:
            teams = json.load(f)
            for team in teams:
                Team.objects.create(
                    id=team['id'],
                    name=team['name'])
        with open('teamScheduling/players.json') as f:
            players = json.load(f)
            for player in players:
                try:
                    user = User.objects.create(
                        username=player['email'],
                        password='test')
                    team = Team.objects.get(name=player['team'])
                    Player.objects.create(
                        number=player['number'],
                        rating=player['rating'],
                        draft=player['draft'],
                        phone=player['phone'],
                        team=team)
                except:
                    pass
        with open('teamScheduling/schedule.json') as f:
            schedule = json.load(f)
            time_dict = {}
            i = 0
            for event in schedule:
                print i
                dt = datetime.datetime(
                    year=int(event['date']['year']),
                    month=int(event['date']['month']),
                    day=int(event['date']['day']),
                    hour=int(event['time']['hour']),
                    minute=int(event['time']['minute']))
                team = Team.objects.get(id=int(event['team']))
                if dt in time_dict:
                    # Join games to form game and remove from dict
                    Game.objects.create(
                        time=dt,
                        teamA=time_dict[dt],
                        teamB=team)
                    time_dict.pop(dt)
                else:
                    # add dictionar entry
                    time_dict[dt] = team

    def test_something(self):
        raise Exception()
