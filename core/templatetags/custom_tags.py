from pathlib import Path

from django import template
from django.templatetags.static import static
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from core.templatetags.constants import DEFAULT_MESSAGE_TAGS
from core.file.utils import read_json_file
from core.file.utils import read_json_file

register = template.Library()


@register.simple_tag
def vite_asset_path(file_name):
    dist_dir = Path("dist")
    manifest_file = Path("core") / "static" / dist_dir / ".vite" / "manifest.json"
    manifest = read_json_file(manifest_file)
    for _, v in manifest.items():
        if file_name.endswith("css"):
            asset_file = v["css"][0]
        else:
            asset_file = v["file"]
    return static(dist_dir / asset_file)


@register.simple_tag
def flash_message(message):
    html = flash_message_html(message.tags).replace("__MESSAGE__", str(message))
    return mark_safe(html)


@register.simple_tag
def flash_message_html(tags):
    return (f"""
        <div
          id="flash-message"
          x-data="{{ show: true }}"
          x-init="setTimeout(() => show = false, 10000);"
          x-show="show"
          x-transition
          class="relative px-4 py-3 {tags}"
          role="alert"
        >
          <span id="flash-message-text">__MESSAGE__</span>
          <span class="absolute top-0 right-0">
            <svg
              @click="show = false"
              class="{DEFAULT_MESSAGE_TAGS} {_xmark_icon_color(tags)}" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><title>Close</title><path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/>
            </svg>
          </span>
        </div>
    """)


def _xmark_icon_color(tags):
    if "success" in tags:
        return "text-green-500"
    elif "error" in tags:
        return "text-red-500"
    return ""
