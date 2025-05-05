import json
from django import template
from django.conf import settings
from pathlib import Path

register = template.Library()

@register.simple_tag
def vite_asset_path(path):
    manifest_path = Path(settings.BASE_DIR) / "static" / "build" / ".vite" / "manifest.json"

    if not manifest_path.exists(): return

    with open(manifest_path) as file:
        manifest = json.load(file)
    return "static/build/" + manifest[path]["file"]
