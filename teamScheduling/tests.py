import datetime
import json

from django.db import transaction
from django.contrib.auth.models import User
from django.test import TestCase

from .models import Player, Team, Game
from .models import getSubs

# Create your tests here.
class SubTest(TestCase):
    def setUp(self):
        '''
        main_team vs other_team, then
        sub_team_1 vs sub_team_2, then
        sub_team_3 vs sub_team_4

        Each team has one player on it
        '''
        # Teams
        main_team = Team.objects.create(name='main_team')
        other_team = Team.objects.create(name='other')
        # Reverse order to make sure sorting does something
        sub_team_4 = Team.objects.create(name='sub_team_4')
        sub_team_3 = Team.objects.create(name='sub_team_3')
        sub_team_2 = Team.objects.create(name='sub_team_2')
        sub_team_1 = Team.objects.create(name='sub_team_1')
        # Players
        u1 = User.objects.create(username='user', password='test')
        mp1 = Player.objects.get(user=u1)
        mp1.rating=10
        mp1.team=main_team
        mp1.save()
        self.mp1 = mp1
        u2 = User.objects.create(username='other1', password='test')
        op1 = Player.objects.get(user=u2)
        op1.rating=10
        op1.team=other_team
        op1.save()
        u3 = User.objects.create(username='sub1', password='test')
        sp1 = Player.objects.get(user=u3)
        sp1.rating=10
        sp1.team=sub_team_1
        sp1.save()
        u4 = User.objects.create(username='sub2', password='test')
        sp2 = Player.objects.get(user=u4)
        sp2.rating=10
        sp2.team=sub_team_2
        sp2.save()
        u5 = User.objects.create(username='sub3', password='test')
        sp3 = Player.objects.get(user=u5)
        sp3.rating=10
        sp3.team=sub_team_3
        sp3.save()
        u6 = User.objects.create(username='sub4', password='test')
        sp4 = Player.objects.get(user=u6)
        sp4.rating=10
        sp4.team=sub_team_4
        sp4.save()
        # Games
        game1 = Game.objects.create(
            teamA=main_team,
            teamB=other_team,
            time=datetime.datetime.today()
        )
        self.game = game1
        game2 = Game.objects.create(
            teamA=sub_team_1,
            teamB=sub_team_2,
            time=datetime.datetime.today() + datetime.timedelta(hours=2)
        )
        game3 = Game.objects.create(
            teamA=sub_team_3,
            teamB=sub_team_4,
            time=datetime.datetime.today() + datetime.timedelta(hours=4)
        )

    def test_get_subs(self):
        subs = getSubs(self.game, [self.mp1,])[0].subs
        for sub in subs:
            print sub, sub.game.time

        for i in xrange(1, len(subs)):
            assert(subs[i-1].game.time <= subs[i].game.time)
        assert len(subs) == 4
