from django.conf.urls import patterns, include, url
from django.contrib import admin
from teamScheduling import views
admin.autodiscover()

'''
HOME -> (login, register / forwarded to next game)
	login     -> simple username, password [TODO: use email]
	register  -> Name, email, username, password
	[TODO: add way to reset password / contact admin]
	NEXT GAME -> View sub replacement
	GAMES -> View entire schedule

[ADMIN ONLY]
	see all teams

'''

urlpatterns = patterns('',
	url(r'^$', views.home),
	url(r'^next-game/', views.nextGame),
	url(r'^signin/',views.signin),
	url(r'^signout/',views.signout),
	url(r'^teams/', views.teams),
	url(r'^team/$', views.team),
	url(r'^team/(\d+)$',views.specificTeam),
	url(r'^team/(\d+)/game/(\d+)',views.subs),

	url(r'^api/teams',views.apiTeams),
	url(r'^api/games',views.apiGames),
	url(r'^api/players/team-(\d+)',views.apiPlayers),
	url(r'^api/substitutes/game-(\d+)',views.apiSubstitutes),
	url(r'^api/sublist-team-(\d+)-game-(\d+)',views.apiGetSubList),
	url(r'^api/message-info/team/(\d+)/game/(\d+)',views.apiGetMessageInfo),
)
