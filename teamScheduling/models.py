from django.db import models
from django.forms import ModelForm
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import Q
from decimal import Decimal
import datetime
# Create your models here.
from .utils import Object

class Player(models.Model):
	user   = models.OneToOneField(User)
	number = models.PositiveSmallIntegerField(null=True)
	rating = models.DecimalField(max_digits=4, decimal_places=2,null=True)
	draft  = models.PositiveSmallIntegerField(null=True)
	team   = models.ForeignKey('Team', null=True)
	phone  = models.CharField(max_length=20, null=True)

	def __str__(self):
		if self.rating and self.draft:
			return "%s's profile: rating=%.1f draft:%d" % (self.user, self.rating, self.draft)
		else:
			return "%s's profile: rank=NA" % self.user

	def is_draft_ordered(self):
		return self.rating > 1.0 and self.rating < 3.0


class SigninForm(forms.Form):
	username = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput())
	def clean_password(self):
		password = self.cleaned_data['password']
		user     = self.get_user()
		if(user is not None):
			if(not user.is_active):
				raise forms.ValidationError("User exists, but not active")
			return password
		else:
			raise forms.ValidationError("User not valid")
	
	def get_user(self):
		password = self.cleaned_data['password']
		username = self.cleaned_data['username']
		user     = authenticate(username = username, password = password)
		return user
	

def create_user_profile(sender, instance, created, **kwargs):
	if created:
		profile, created = Player.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Team(models.Model):
	name  = models.CharField(max_length=100)
	def __str__(self):
		return self.name

class Game(models.Model):
	time  = models.DateTimeField()
	teamA = models.ForeignKey('Team', related_name='teamA')
	teamB = models.ForeignKey('Team', related_name='teamB')
	def __str__(self):
		return "Game @ %s: %s vs %s" % (self.time, self.teamA, self.teamB)

def getGamesOnDay(day):
	return Game.objects.filter(time__range=(day,day+datetime.timedelta(days=1)))

#Subtract by small amount to not get offset hour
GAME_DURATION = datetime.timedelta(hours=1-0.001)

def getGamesAtTime(time):
	return Game.objects.filter(time__range=(time-GAME_DURATION,time+GAME_DURATION))

def getConflictingGames(game):
	return getGamesAtTime(game.time)

def getGameOnSameDay(team, day):
	g = Game.objects.filter(
			time__range=(day-datetime.timedelta(days=1),
				day+datetime.timedelta(days=1))
			).filter(Q(teamA=team) | Q(teamB=team))
	if len(g) > 0:
		g = g[0]
	return g

def getAvailableTeams(game):
	conflict_games = getConflictingGames(game)
	conflict_teams = []
	for i in conflict_games:
		conflict_teams.append(i.teamA)
		conflict_teams.append(i.teamB)
	return Team.objects.exclude(id__in=[t.id for t in conflict_teams])


def getSubsForRatingFromList(rating, player_list):
	EPSILON = Decimal('0.01')
	return player_list.filter(rating__lte=rating+EPSILON,
			rating__gte=rating-EPSILON)

def getSubsForPlayerFromList(player, player_list):
        if player.is_draft_ordered():
            team_players = Player.objects.filter(team__id=player.team.id, user__is_active=True)
            team_draft_nums = {player.draft for player in team_players if player.draft}
            # Go up 4 draft values, excluding own draft numbers
            best_draft = player.draft
            num_increments = 0
            while best_draft > 1 and num_increments < 4:
                best_draft -= 1
                if best_draft not in team_draft_nums:
                    num_increments += 1
            return player_list.filter(draft__gte=best_draft)
        else:
            return getSubsForRatingFromList(Decimal(player.rating), player_list)

def getSubs(game, missing_players):
	free_teams   = getAvailableTeams(game)
	team_game_map  = {}
	for t in free_teams:
		team_game_map[t] = getGameOnSameDay(t, game.time.date())
	free_players = Player.objects.filter(
			team__id__in=[f.id for f in free_teams]
	)
	subs = {}
	for mp in missing_players:
		subs[mp] = getSubsForPlayerFromList(mp, free_players)
		for s in subs[mp]:
			if s.team in team_game_map:
				print team_game_map[s.team], s.team
				s.game = team_game_map[s.team]
	new_subs = []
	for mp, mp_subs in subs.iteritems():
		new_sub = Object()
		new_sub.mps = [mp]
                # Sort subs by time
                def sort_subs(x, y):
                    if x:
                        if y:
                            return cmp(x, y)
                        else:
                            return -1
                    else:
                        if y:
                            return 1
                        else:
                            return 0

                def get_sub_time(s):
                    try:
                        return s.game.time
                    except:
                        return None

                if mp.is_draft_ordered:
                    # Secondary sort by time
                    sorted_subs = sorted(
                        mp_subs,
                        cmp=sort_subs,
                        key=get_sub_time)
                    # Primary sort by draft
                    sorted_subs = sorted(sorted_subs, key=lambda s: s.draft)
                else:
                    # Secondary sort by draft
                    sorted_subs = sorted(mp_subs, key=lambda s: s.draft)
                    # Primary sort by time
                    sorted_subs = sorted(
                        sorted_subs,
                        cmp=sort_subs,
                        key=get_sub_time)

		new_sub.subs = sorted_subs
		new_subs.append(new_sub)
        return new_subs

def getPlayers(teamId):
	return Player.objects.filter(team__id=teamId)

def getPlayerName(player):
	return player.user.first_name + ' ' + player.user.last_name


