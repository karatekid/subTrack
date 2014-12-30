from django.conf.urls import patterns, include, url
from django.contrib import admin
from teamScheduling import views
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', views.teams),
	url(r'^team/(\d+)$',views.team),
	url(r'^team/(\d+)/game/(\d+)',views.subs),

	url(r'^api/teams',views.apiTeams),
	url(r'^api/games',views.apiGames),
	url(r'^api/players/team-(\d+)',views.apiPlayers),
	url(r'^api/substitutes/game-(\d+)',views.apiSubstitutes),
	url(r'^api/sublist-team-(\d+)-game-(\d+)',views.apiGetSubList),
	url(r'^api/message-info',views.apiGetMessageInfo),
)
