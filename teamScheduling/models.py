from django.db import models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from decimal import Decimal
from generic import *
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
	rating_mp_map = {}
	for mp in missing_players:
		r = str(mp.rating)
		if r not in rating_mp_map:
			rating_mp_map[r] = []
		rating_mp_map[r].append(mp)
	new_subs = []
	for r in rating_mp_map:
		new_sub = Object()
		new_sub.mps = rating_mp_map[r]
		new_sub.subs = subs[r]
		new_subs.append(new_sub)
	return new_subs

def getPlayers(teamId):
	return Player.objects.filter(team__id=teamId)

def getPlayerName(player):
	return player.user.first_name + ' ' + player.user.last_name


