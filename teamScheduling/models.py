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

class Player(models.Model):
	user   = models.OneToOneField(User)
	number = models.PositiveSmallIntegerField(null=True)
	rating = models.DecimalField(max_digits=4, decimal_places=2,null=True)
	draft  = models.PositiveSmallIntegerField(null=True)
	team   = models.ForeignKey('Team', null=True)
	phone  = models.CharField(max_length=20, null=True)

	def __str__(self):
		if self.rating:
			return "%s's profile: rank=%d" % (self.user, self.rating)
		else:
			return "%s's profile: rank=NA" % self.user

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
	return getSubsForRatingFromList(player.rating, player_list)

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
		r = str(mp.rating)
		if r in subs:
			continue
		else:
			subs[r] = getSubsForRatingFromList(Decimal(r),free_players)
			for i in xrange(len(subs[r])):
				s = subs[r][i]
				if s.team in team_game_map:
					print team_game_map[s.team], s.team
					subs[r][i].game = team_game_map[s.team]
	rating_mp_map = {}
	for mp in missing_players:
		r = str(mp.rating)
		if r not in rating_mp_map:
			rating_mp_map[r] = []
		rating_mp_map[r].append(mp)
	new_subs = []
	for r in rating_mp_map:
		new_sub = object()
		new_sub.mps = rating_mp_map[r]
		new_sub.subs = subs[r]
		new_subs.append(new_sub)
        # Sort subs by time
        return new_subs
        sorted_subs = sorted(
            new_subs,
            cmp=lambda x, y: x < y if x and y else 0,
            key=lambda s: s.game.time)
	return sorted_subs

def getPlayers(teamId):
	return Player.objects.filter(team__id=teamId)

def getPlayerName(player):
	return player.user.first_name + ' ' + player.user.last_name


