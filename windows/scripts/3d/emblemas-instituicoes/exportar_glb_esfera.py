"""GLB da esfera (frente = escudo, costa = INSTITUICAO). blender -b blend/esfera-pf-3d.blend -P scripts/exportar_glb_esfera.py -- PF
   (antes: python scripts/preparar_glb_esfera.py PF). Materiais refeitos em Principled simples; hemisferios reduzidos (Decimate 0,30)."""
import bpy, sys, os
sig = sys.argv[sys.argv.index("--") + 1]
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); F = os.path.join(R, "fontes")
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


fr = bpy.data.objects[f"GEO-Frente-{sig}"]; co = bpy.data.objects["GEO-Costa-INSTITUICAO"]
fr.data.materials[0] = mat(f"GLB-Frente-{sig}", f"{sig}-esf-cor.png", f"{sig}-esf-glb-mr.png")
co.data.materials[0] = mat("GLB-Costa-INSTITUICAO", "INSTITUICAO-glb-cor.png")
for o in (fr, co): d = o.modifiers.new("Leve", "DECIMATE"); d.ratio = 0.30
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type in ('MESH', 'EMPTY'): o.select_set(True)
out = os.path.join(R, "modelo-3d", f"esfera-{sig.lower()}-3d.glb")
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_apply=True, export_animations=False, export_yup=True, export_image_format='AUTO')
print("GLB OK", out, round(os.path.getsize(out) / 1e6, 1), "MB")
