from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import AdminTextInputWidget
from django.utils.safestring import mark_safe
import teamScheduling.models as ts

# Register your models here.
admin.site.register(ts.Player)
admin.site.register(ts.Game)

class TeamAdminWidget(AdminTextInputWidget):
	def render(self, name, value, attrs=None):
		s = super(AdminTextInputWidget, self).render(name,value, attrs)
		team = ts.Team.objects.get(name=value)
		players = ts.Player.objects.filter(team=team)
		html = '<br/><ul>'
		for p in players:
			html += '<li style="list-style:none"><a href="/admin/teamScheduling/player/%s">%s %s: %s</a></li>\n' % (
				str(p.id),
				p.user.first_name,
				p.user.last_name,
				str(p.rating),
			)
		html += '</ul>'
		return mark_safe(s+html)

class TeamAdminForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(TeamAdminForm, self).__init__(*args,**kwargs)
		self.fields['name'].widget = TeamAdminWidget()

class TeamAdmin(admin.ModelAdmin):
	form = TeamAdminForm
		
admin.site.register(ts.Team, TeamAdmin)
