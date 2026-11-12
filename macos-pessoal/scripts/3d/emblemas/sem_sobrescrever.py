from pathlib import Path as _NolaPath
import sys as _nola_sys
_nola_sys.path.insert(0, str(_NolaPath(__file__).resolve().parents[2]))
from nola_paths import media_root, configure_device, asset_id
import bpy
bpy.context.scene.render.use_overwrite = False   # permite retomar render interrompido
