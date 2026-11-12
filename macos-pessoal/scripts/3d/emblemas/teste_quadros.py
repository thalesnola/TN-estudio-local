from pathlib import Path as _NolaPath
import sys as _nola_sys
_nola_sys.path.insert(0, str(_NolaPath(__file__).resolve().parents[2]))
from nola_paths import media_root, configure_device, asset_id
import bpy,sys
s=bpy.context.scene; a=sys.argv[sys.argv.index("--")+1:]
s.render.resolution_x=s.render.resolution_y=int(a[0]); s.cycles.samples=int(a[1])
s.render.filepath=a[2]
for f in a[3:]:
    s.frame_set(int(f)); s.render.filepath=a[2]+"_%03d"%int(f); bpy.ops.render.render(write_still=True)
