from pathlib import Path as _NolaPath
import sys as _nola_sys
_nola_sys.path.insert(0, str(_NolaPath(__file__).resolve().parents[2]))
from nola_paths import media_root, configure_device, asset_id
import bpy
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(media_root()/"blend/emblema-nola-macm5-3d.blend"), copy=True)
print("PACOTE OK", [i.name for i in bpy.data.images if i.packed_file])
