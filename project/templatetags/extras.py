from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def xmark_icon_color(tags):
    if "success" in tags:
        return "text-green-500"
    elif "error" in tags:
        return "text-red-500"
    else:
        # TODO: Create error logger that will show where error happened and why.
        raise ValueError("Hey what color am I? Greetings from project/templatetags/extras.py")
