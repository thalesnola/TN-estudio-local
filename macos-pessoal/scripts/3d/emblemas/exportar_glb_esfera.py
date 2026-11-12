from pathlib import Path as _NolaPath
import sys as _nola_sys
_nola_sys.path.insert(0, str(_NolaPath(__file__).resolve().parents[2]))
from nola_paths import media_root, configure_device, asset_id
"""GLB da esfera (frente = escudo, costa = nola-macm5). blender -b blend/esfera-nola-macm5-3d.blend -P scripts/exportar_glb_esfera.py -- nola-macm5
   (antes: python scripts/preparar_glb_esfera.py nola-macm5). Materiais refeitos em Principled simples; hemisferios reduzidos (Decimate 0,30)."""
import bpy, sys, os
sig = asset_id(sys.argv[sys.argv.index("--") + 1])
R = str(media_root()); F = os.path.join(R, "fontes")
bpy.context.scene.frame_set(1)


def ld(n, cs):
    i = bpy.data.images.load(os.path.join(F, n)); i.colorspace_settings.name = cs; i.pack(); return i


def mat(nome, cor, mr=None, metal=1.0, rough=0.35):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree
    pb = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = ld(cor, "sRGB"); nt.links.new(t.outputs["Color"], pb.inputs["Base Color"])
    if mr:
        t2 = nt.nodes.new("ShaderNodeTexImage"); t2.image = ld(mr, "Non-Color"); sep = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(t2.outputs["Color"], sep.inputs["Color"])
        nt.links.new(sep.outputs["Green"], pb.inputs["Roughness"]); nt.links.new(sep.outputs["Blue"], pb.inputs["Metallic"])
    else:
        pb.inputs["Metallic"].default_value = metal; pb.inputs["Roughness"].default_value = rough
    return m


fr = bpy.data.objects[f"GEO-Frente-{sig}"]; co = bpy.data.objects["GEO-Costa-nola-macm5"]
fr.data.materials[0] = mat(f"GLB-Frente-{sig}", f"{sig}-esf-cor.png", f"{sig}-esf-glb-mr.png")
co.data.materials[0] = mat("GLB-Costa-nola-macm5", "nola-macm5-glb-cor.png")
for o in (fr, co): d = o.modifiers.new("Leve", "DECIMATE"); d.ratio = 0.30
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type in ('MESH', 'EMPTY'): o.select_set(True)
out = os.path.join(R, "modelo-3d", f"esfera-{sig.lower()}-3d.glb")
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_apply=True, export_animations=False, export_yup=True, export_image_format='AUTO')
print("GLB OK", out, round(os.path.getsize(out) / 1e6, 1), "MB")
