from django import template
register = template.Library()

import phonenumbers

@register.filter(name='filter_phone')
def filter_phone(s):
	if s:
		return phonenumbers.format_number(
			phonenumbers.parse(str(s),"US"),
			phonenumbers.PhoneNumberFormat.NATIONAL)
	return None

