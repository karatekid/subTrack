from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
import datetime
import json
from teamScheduling.models import *
from django.core import serializers

# Create your views here.

def teams(request):
	ts = Team.objects.all()
	return render(request, 'teamScheduling/teams.html',
			{'teams':ts})
	
def team(request,teamId):
	players = Player.objects.filter(team__id=teamId)
	team    = Team.objects.get(id=teamId)
	games   = Game.objects.filter(Q(teamA=team) |
			Q(teamB=team)).order_by('time')
	for game in games:
		if game.teamA == team:
			game.opponent = game.teamB
		else:
			game.opponent = game.teamA
	return render(request, 'teamScheduling/team.html',
			{'players':players, 
				'team':team,
				'games':games,
			})

def subs(request,teamId,gameId):
	players = Player.objects.filter(team__id=teamId)
	team   = Team.objects.get(id=teamId)
	game   = Game.objects.get(id=gameId)
	params = request.GET.copy()
	params = dict(params.iterlists())
	subs = []
	if 'mp' in params:
		mps = Player.objects.filter(id__in=
				[int(f) for f in params['mp']])
		print mps
		subs = getSubs(game, mps)
		print subs
	if game.teamA == team:
		game.opponent = game.teamB
	else:
		game.opponent = game.teamA
	return render(request, 'teamScheduling/subs.html',
			{'players':players, 
				'team':team,
				'game':game,
				'subs':subs,
			})


def apiTeams(request):
	ts = Team.objects.all()
	teams_json = serializers.serialize('json',ts)
	return HttpResponse(json.dumps(teams_json),
			content_type='application/json')
	
def apiGames(request):
	games = Game.objects.all()
	games_json = serializers.serialize('json',games)
	return HttpResponse(json.dumps(games_json),
			content_type='application/json')

def apiPlayers(request, teamId):
	ps = getPlayers(teamId) 
	ps_json = serializers.serialize('json',ps)
	return HttpResponse(json.dumps(ps_json),
			content_type='application/json')

def apiSubstitutes(request, gameId):
	game = Game.objects.get(id=gameId)
	list_mps = []
	params = request.GET.copy()
	params = dict(params.iterlists())
	mps = Player.objects.filter(id__in=
			[int(f) for f in params['mp']])
	subs = getSubs(game, mps)
	print "SUBS", subs
	subs_json = {}
	for i in subs:
		subs_json[i] = serializers.serialize('json',subs[i]) 
	return HttpResponse(json.dumps(subs_json),
			content_type='application/json')


