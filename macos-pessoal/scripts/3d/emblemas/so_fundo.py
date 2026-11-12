from pathlib import Path as _NolaPath
import sys as _nola_sys
_nola_sys.path.insert(0, str(_NolaPath(__file__).resolve().parents[2]))
from nola_paths import media_root, configure_device, asset_id
"""Renderiza so o fundo degrade do padrao (geometria oculta), 16 bits, para compor os videos horizontais/verticais com degrade.
   blender -b blend/emblema-nola-macm5-3d.blend -P scripts/so_fundo.py -- LARGURA ALTURA saida.png [vertical]"""
import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]
s = bpy.context.scene
for o in bpy.data.objects:
    if o.type == 'MESH': o.hide_render = True
s.cycles.samples = 16; s.cycles.use_denoising = False
s.render.resolution_x, s.render.resolution_y = int(a[0]), int(a[1]); s.render.resolution_percentage = 100
cam = bpy.data.objects["Camera"]; cam.data.sensor_fit = "HORIZONTAL"
if len(a) > 3:   # vertical: mesmos ajustes do render_vertical.py
    cam.data.shift_y = -0.035
    for n in s.world.node_tree.nodes:
        if n.type == "MAP_RANGE" and abs(n.inputs["From Min"].default_value - 0.92) < 1e-6: n.inputs["From Min"].default_value = 0.78
s.render.film_transparent = False
s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGB'; s.render.image_settings.color_depth = '16'
s.render.filepath = a[2]; s.frame_set(1); bpy.ops.render.render(write_still=True)
