from pathlib import Path as _NolaPath
import sys as _nola_sys
_nola_sys.path.insert(0, str(_NolaPath(__file__).resolve().parents[2]))
from nola_paths import media_root, configure_device, asset_id
import bpy
s=bpy.context.scene
s.render.film_transparent=True
s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGBA'
s.render.image_settings.color_depth='8'
