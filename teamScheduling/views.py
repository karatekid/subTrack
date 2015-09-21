from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db.models import Q
import datetime
import json
from teamScheduling.models import *
from django.core import serializers
from django.template.loader import render_to_string
import urllib

# Create your views here.

@login_required(login_url='/signin')	
def home(request):
	if request.user.groups.filter(name='Admins').exists():
		return redirect('/teams')
	return redirect('/next-game')

@login_required(login_url='/signin')	
def team(request):
	if request.user.groups.filter(name='Admins').exists():
		return redirect('/teams')
	player  = Player.objects.get(user = request.user)
	team    = player.team
	players = Player.objects.filter(team__id=team.id).filter(user__is_active=True)
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

@login_required(login_url='/signin')	
def specificTeam(request, teamId):
	if not request.user.groups.filter(name='Admins').exists():
		return redirect('/team')
	team    = Team.objects.get(id=teamId)
	players = Player.objects.filter(team__id=team.id).filter(user__is_active=True)
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



@login_required(login_url='/signin')
def nextGame(request):
	if request.user.groups.filter(name='Admins').exists():
		return redirect('/teams')
	player  = Player.objects.get(user = request.user)
	team    = player.team
	games   = Game.objects.filter(Q(teamA=team) |
			Q(teamB=team)).filter(time__gte=datetime.datetime.now()
			).order_by('time')
	if len(games) > 0:
		return subs(request, team.id, games[0].id)
	else:
		games   = Game.objects.filter(Q(teamA=team) |
				Q(teamB=team)).filter(time__lte=datetime.datetime.now()
				).order_by('-time')
		return subs(request, team.id, games[0].id)


@login_required(login_url='/signin')	
def teams(request):
	if request.user.groups.filter(name='Admins').exists():
		ts = Team.objects.all()
		return render(request, 'teamScheduling/teams.html',
				{'teams':ts})
	else:
		return redirect('/team')

@login_required(login_url='/signin')	
def subs(request,teamId,gameId):
	players = Player.objects.filter(team__id=teamId).filter(user__is_active=True)
	team   = Team.objects.get(id=teamId)
	game   = Game.objects.get(id=gameId)
	params = request.GET.copy()
	params = dict(params.iterlists())
	subs = []
	if 'mp' in params:
		mps = Player.objects.filter(id__in=
				[int(f) for f in params['mp']]).filter(user__is_active=True)
		for player in players:
			if player.id in [int(f) for f in params['mp']]:
				player.selected = True
		subs = getSubs(game, mps)
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



def redirectToTeam(user):
	p = Player.objects.get(user=user)
	if p and p.team:
		teamNum = p.team.id
		return redirect('/team/'+teamNum)
	if user.groups.filter(name='Admins').exists():
		return redirect('/teams')
	return redirect('/')
	'''
	else if 'Admins' in user.groups.all():
		return redirect('/teams/')
	else:
		return redirect('/')
	'''
		

def signin(request):
	if request.user.is_authenticated():
		return redirect('/next-game')
	signinForm = SigninForm()
	if request.method == 'POST':
		signinForm = SigninForm(request.POST)
	if signinForm.is_bound and signinForm.is_valid():
		user = signinForm.get_user()
		login(request, user)
		return redirect('/next-game')
	return render(request, 'teamScheduling/signin.html', {
			'title'  : 'Sign In',
			'form'   : signinForm
			})

def signout(request):
	logout(request)
	return redirect('/')

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
			[int(f) for f in params['mp']]).filter(user__is_active=True)
	subs = getSubs(game, mps)
	print "SUBS", subs
	subs_json = {}
	for i in subs:
		subs_json[i] = serializers.serialize('json',subs[i]) 
	return HttpResponse(json.dumps(subs_json),
			content_type='application/json')
@csrf_exempt
def apiGetSubList(request, teamId, gameId):
	players = Player.objects.filter(team__id=teamId).filter(user__is_active=True)
	team   = Team.objects.get(id=teamId)
	game   = Game.objects.get(id=gameId)
	params = request.GET.copy()
	params = dict(params.iterlists())
	subs = []
	if 'mp' in params:
		mps = Player.objects.filter(id__in=
				[int(f) for f in params['mp']]).filter(user__is_active=True)
		subs = getSubs(game, mps)
		serialSubs = {}
		for r, subArr in subs.iteritems():
			serialSubs[r] = []
			for sub in subArr:
				serialSubs[r].append({
					'name': getPlayerName(sub),
					'email': sub.user.email,
				})
		ratings = {}
		for mp in mps:
			r = str(mp.rating)
			if r in ratings:
				ratings[r].append(getPlayerName(mp))
			else:
				ratings[r] = [getPlayerName(mp),]
		serialOut = {
			'rating_match': ratings,
			'subs': serialSubs,
		}

	return HttpResponse(json.dumps(serialOut),
			content_type='application/json')

MESSAGE_SUBJECT='''
This was a partially automated message from the Arctic Coliseum
'''

MESSAGE_BODY='''
Note: This is an automated email generated by the Arctic Coliseum

Dear valued Arctic Coliseum hockey player,
	 We are running short on players for ((this_game)) and
((this_coach)) is contacting you to see if you'd like to play at
((this_time)) for ((this_team))? Please reply to him if you'd like to
play.
'''
#TODO: Incorporate the actual game, team and captain info
def apiGetMessageInfo(request, teamId, gameId):
	team = Team.objects.get(pk=teamId)
	game = Game.objects.get(pk=gameId)
	body = render_to_string('teamScheduling/msgBody.html',
			{	'team':team,
				'game':game
			})
	subject = render_to_string('teamScheduling/msgSubject.html',
			{	'team':team,
				'game':game
			})
	ps = { 
			'subject': urllib.quote_plus(subject),
			'body':    urllib.quote_plus(body)
	}
	return HttpResponse(json.dumps(ps),
			content_type='application/json')

