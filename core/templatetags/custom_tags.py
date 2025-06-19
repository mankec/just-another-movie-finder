from django import template
from django.utils.safestring import mark_safe

from core.templatetags.constants import DEFAULT_MESSAGE_TAGS

register = template.Library()


@register.simple_tag
def flash_message(message, tags, with_js=False):
    html = (f"""
        <li
          x-data="{{ show: true }}"
          x-init="setTimeout(() => show = false, 10000);"
          x-show="show"
          x-transition
          class="px-4 py-3 {tags}"
          role="alert"
        >
          <span class="block sm:inline">{message}</span>
          <span class="absolute top-0 bottom-0 right-0 px-4 py-3">
            <svg
              @click="show = false"
              class="{DEFAULT_MESSAGE_TAGS} {_xmark_icon_color(tags)}" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><title>Close</title><path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/>
            </svg>
          </span>
        </li>
    """)

    if with_js:
        return html
    return mark_safe(html)


def _xmark_icon_color(tags):
    if "success" in tags:
        return "text-green-500"
    elif "error" in tags:
        return "text-red-500"
    return ""
