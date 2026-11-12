"""Vertical 9:16 para escudos: igual ao render_vertical.py do padrao INSTITUICAO, mas a camera se aproxima em proporcao a LARGURA do escudo
   (a moeda de 2,0 m usava 3,42 m; o escudo mais estreito chega mais perto para ocupar ~83% da largura). Variavel de ambiente SIG.
   blender -b blend/emblema-pf-3d.blend -P scripts/cycles_gpu.py -P scripts/render_vertical_inst.py -P scripts/render_alpha.py -o saida/v_ -a"""
import bpy, json, os
from mathutils import Vector
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
J = json.load(open(os.path.join(R, "fontes", os.environ["SIG"] + "-contorno.json")))
k = 1.0 if os.environ.get("TIPO") == "esfera" else J["largura_m"] / 2.0   # esfera de 2 m = padrao INSTITUICAO
s = bpy.context.scene
s.render.resolution_x = 1080; s.render.resolution_y = 1920; s.render.resolution_percentage = 100
cam = bpy.data.objects["Camera"]
cam.location = (0, -3.42 * k, 0.54 * k)
cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.sensor_fit = "HORIZONTAL"; cam.data.shift_y = -0.035
for n in s.world.node_tree.nodes:
    if n.type == "MAP_RANGE" and abs(n.inputs["From Min"].default_value - 0.92) < 1e-6: n.inputs["From Min"].default_value = 0.78
