import datetime
import json

from collections import namedtuple

from django.db import transaction
from django.contrib.auth.models import User
from django.test import TestCase

from .models import Player, Team, Game
from .models import getSubs


_PlayerDict = namedtuple('_PlayerDict', ['name', 'rating', 'draft'])


class _LeagueConfig(object):
    def __init__(self, team_dict):
        self.teams = {}
        self.players = {}
        for team_name, players in team_dict.iteritems():
            team = Team.objects.create(name=team_name)
            self.teams[team_name] = team
            for player_dict in players:
                user = User.objects.create(username=player_dict.name,
                                           password='test')
                player = Player.objects.get(user=user)
                player.rating = player_dict.rating
                player.draft = player_dict.draft
                player.team = team
                player.save()
                self.players[player_dict.name] = player


# Create your tests here.
class SubTest(TestCase):
    def tearDown(self):
        Game.objects.all().delete()
        Team.objects.all().delete()
        Player.objects.all().delete()
        User.objects.all().delete()

    def test_get_subs(self):
        '''
        main_team vs other_team, then
        sub_team_1 vs sub_team_2, then
        sub_team_3 vs sub_team_4

        Each team has one player on it, there's also a free agent team
        '''
        config = _LeagueConfig({
            'main_team': [
                _PlayerDict('user', 1.5, 3),
            ],
            'other': [
                _PlayerDict('other1', 1.5, 4),
            ],
            'free': [
                _PlayerDict('free', 1.5, 5),
            ],
            'sub_team_1': [
                _PlayerDict('sub1', 1.5, 3),
            ],
            'sub_team_2': [
                _PlayerDict('sub2', 1.5, 4),
            ],
            'sub_team_3': [
                _PlayerDict('sub3', 1.5, 1),
            ],
            'sub_team_4': [
                _PlayerDict('sub4', 1.5, 2),
            ],
        })
        mp1 = config.players['user']
        # Games
        game1 = Game.objects.create(
            teamA=config.teams['main_team'],
            teamB=config.teams['other'],
            time=datetime.datetime.today()
        )
        game = game1
        game2 = Game.objects.create(
            teamA=config.teams['sub_team_1'],
            teamB=config.teams['sub_team_2'],
            time=datetime.datetime.today() + datetime.timedelta(hours=2)
        )
        game3 = Game.objects.create(
            teamA=config.teams['sub_team_3'],
            teamB=config.teams['sub_team_4'],
            time=datetime.datetime.today() + datetime.timedelta(hours=4)
        )
        subs = getSubs(game, [mp1,])[0].subs
        for sub in subs:
            if hasattr(sub.game, 'time'):
                print sub.game.time
            print sub, sub.draft
        for i in xrange(1, len(subs)):
            assert(subs[i-1].draft <= subs[i].draft)
        self.assertEquals(len(subs), 5)

    def test_sort_3_by_date(self):
        config = _LeagueConfig({
            'main_team': [
                _PlayerDict('user', 3.0, 3),
            ],
            'other': [
                _PlayerDict('other', 1.5, 15),
            ],
            'sub_team_1': [
                _PlayerDict('sub1', 3.0, 4),
            ],
            'sub_team_2': [
                _PlayerDict('sub2', 3.0, 3),
            ],
            'sub_team_3': [
                _PlayerDict('sub3', 3.0, 2),
            ],
            'sub_team_4': [
                _PlayerDict('sub4', 3.0, 1),
            ],
        })
        mp1 = config.players['user']
        # Games
        game = Game.objects.create(
            teamA=config.teams['main_team'],
            teamB=config.teams['other'],
            time=datetime.datetime.today()
        )
        game2 = Game.objects.create(
            teamA=config.teams['sub_team_1'],
            teamB=config.teams['sub_team_2'],
            time=datetime.datetime.today() + datetime.timedelta(hours=2)
        )
        game2 = Game.objects.create(
            teamA=config.teams['sub_team_3'],
            teamB=config.teams['sub_team_4'],
            time=datetime.datetime.today() + datetime.timedelta(hours=4)
        )
        subs = getSubs(game, [mp1,])[0].subs
        for sub in subs:
            if hasattr(sub.game, 'time'):
                print sub.game.time
            print sub, sub.draft
        for i in xrange(1, len(subs)):
            assert(subs[i-1].game.time <= subs[i].game.time)
        self.assertEquals(len(subs), 4)
