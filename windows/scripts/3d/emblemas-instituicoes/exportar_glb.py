"""GLB universal da moeda (frente = escudo da instituicao, verso = medalhao INSTITUICAO). Material da frente refeito em Principled simples:
   cor (textura) + metal/rugosidade empacotados (G=rugosidade, B=metal) para o exportador reconhecer. Relevo aplicado e malha reduzida.
   blender -b blend/emblema-pf-3d.blend -P scripts/exportar_glb.py -- PF"""
import bpy, sys, os, numpy as np
sig = sys.argv[sys.argv.index("--") + 1]
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
bpy.context.scene.frame_set(1)
rel = bpy.data.objects[f"GEO-Relevo-{sig}"]; body = bpy.data.objects[f"GEO-Escudo-{sig}"]
mf = rel.data.materials[0]
esm = next(n.image for n in mf.node_tree.nodes if n.type == "TEX_IMAGE" and "esmalte" in n.image.name)
cor = next(n.image for n in mf.node_tree.nodes if n.type == "TEX_IMAGE" and n.image.name.endswith("cor.png"))
w, h = esm.size; e = np.array(esm.pixels[:], np.float32).reshape(h, w, 4)[..., 0]
mr = np.ones((h, w, 4), np.float32)
mr[..., 1] = 0.30 - 0.14 * e          # rugosidade
mr[..., 2] = 0.85 - 0.73 * e          # metal
img = bpy.data.images.new(f"{sig}-metal-rugosidade", w, h, alpha=False); img.colorspace_settings.name = "Non-Color"
img.pixels.foreach_set(mr.ravel()); img.pack()
g = bpy.data.materials.new(f"MAT-GLB-Frente-{sig}"); g.use_nodes = True; nt = g.node_tree
pb = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
t1 = nt.nodes.new("ShaderNodeTexImage"); t1.image = cor
t2 = nt.nodes.new("ShaderNodeTexImage"); t2.image = img
sep = nt.nodes.new("ShaderNodeSeparateColor")
nt.links.new(t1.outputs["Color"], pb.inputs["Base Color"]); nt.links.new(t2.outputs["Color"], sep.inputs["Color"])
nt.links.new(sep.outputs["Green"], pb.inputs["Roughness"]); nt.links.new(sep.outputs["Blue"], pb.inputs["Metallic"])
rel.data.materials[0] = g; body.data.materials[0] = g
dec = rel.modifiers.new("Leve", "DECIMATE"); dec.ratio = 0.35
bv = body.modifiers.get("Bisel")
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type in ('MESH', 'EMPTY'): o.select_set(True)
out = os.path.join(R, "modelo-3d", f"emblema-{sig.lower()}-3d.glb")
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_apply=True, export_animations=False, export_yup=True, export_image_format='AUTO')
print("GLB OK", out, round(os.path.getsize(out) / 1e6, 1), "MB")
