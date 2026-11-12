from pathlib import Path as _NolaPath
import sys as _nola_sys
_nola_sys.path.insert(0, str(_NolaPath(__file__).resolve().parents[2]))
from nola_paths import media_root, configure_device, asset_id
"""Enquadramento vertical 9:16 (stories/reels/status). Usar DEPOIS de cycles_gpu.py:
   blender -b blend/emblema-nola-macm5-3d.blend -P scripts/cycles_gpu.py -P scripts/render_vertical.py -o saida/v_ -a
Moeda ~80% da largura; centro um pouco acima da metade (zonas seguras: ~250 px no topo e ~340 px embaixo ficam livres)."""
import bpy
from mathutils import Vector
s=bpy.context.scene
s.render.resolution_x=1080; s.render.resolution_y=1920; s.render.resolution_percentage=100
cam=bpy.data.objects["Camera"]
cam.location=(0,-3.42,0.54)                      # mesma inclinacao (~9 graus) do padrao, mais perto
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.sensor_fit="HORIZONTAL"             # campo de visao pela LARGURA (padrao); no vertical o Blender usaria a altura
cam.data.shift_y=-0.035                          # sobe o conjunto ~38 px
# degrade mais largo: no quadro alto o halo de 0.92 virava um holofote com borda dura
# ATENCAO: o mundo tem 2 nos MAP_RANGE (fundo da camera e ambiente de reflexo do metal); so mexer no do fundo (From Min 0.92)
for n in s.world.node_tree.nodes:
    if n.type=="MAP_RANGE" and abs(n.inputs["From Min"].default_value-0.92)<1e-6: n.inputs["From Min"].default_value=0.78
