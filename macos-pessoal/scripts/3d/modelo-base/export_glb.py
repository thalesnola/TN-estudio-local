from pathlib import Path as _NolaPath
import sys as _nola_sys
_nola_sys.path.insert(0, str(_NolaPath(__file__).resolve().parents[2]))
from nola_paths import media_root, configure_device, asset_id
import bpy
D=str(media_root()/"modelo-3d")
s=bpy.context.scene; s.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')

# --- assar cor e rugosidade do verso (a rede de nos nao exporta para GLB)
verso=bpy.data.objects["GEO-FaceVerso"]; mat=verso.data.materials[0]; nt=mat.node_tree
s.render.engine='CYCLES'; configure_device(bpy); s.cycles.samples=16; s.cycles.use_denoising=False
def bake(kind,name,noncolor):
    img=bpy.data.images.new(name,2048,2048,alpha=False)
    if noncolor: img.colorspace_settings.name="Non-Color"
    nd=nt.nodes.new("ShaderNodeTexImage"); nd.image=img; nt.nodes.active=nd
    bpy.context.view_layer.objects.active=verso; verso.select_set(True)
    if kind=='DIFFUSE':
        # metal puro assa difuso = preto: passar a cor-base por uma emissao e assar EMIT
        pbs=next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED"); outn=next(n for n in nt.nodes if n.type=="OUTPUT_MATERIAL")
        src=pbs.inputs["Base Color"].links[0].from_socket
        em=nt.nodes.new("ShaderNodeEmission"); nt.links.new(src,em.inputs["Color"]); nt.links.new(em.outputs["Emission"],outn.inputs["Surface"])
        bpy.ops.object.bake(type='EMIT',margin=8)
        nt.links.new(pbs.outputs["BSDF"],outn.inputs["Surface"]); nt.nodes.remove(em)
    else:
        bpy.ops.object.bake(type='ROUGHNESS',margin=8)
    nt.nodes.remove(nd); verso.select_set(False); img.pack(); return img
cor=bake('DIFFUSE',"verso-cor",False); rug=bake('ROUGHNESS',"verso-rugosidade",True)
simples=bpy.data.materials.new("MAT-Verso-GLB"); simples.use_nodes=True; sn=simples.node_tree
pb=next(n for n in sn.nodes if n.type=="BSDF_PRINCIPLED"); pb.inputs["Metallic"].default_value=1.0
t1=sn.nodes.new("ShaderNodeTexImage"); t1.image=cor
t2=sn.nodes.new("ShaderNodeTexImage"); t2.image=rug
sep=sn.nodes.new("ShaderNodeSeparateColor")
sn.links.new(t1.outputs["Color"],pb.inputs["Base Color"])
sn.links.new(t2.outputs["Color"],sep.inputs["Color"]); sn.links.new(sep.outputs["Green"],pb.inputs["Roughness"])
verso.data.materials[0]=simples
# malha do verso mais leve
dec=verso.modifiers.new("Leve","DECIMATE"); dec.ratio=0.30
# --- exportar so o conjunto da moeda (pose de frente)
for n in ("GIRO","GEO-Base","GEO-Aro","GEO-AroVerso","GEO-FaceLetras","GEO-FaceCampo","GEO-FaceVerso"):
    bpy.data.objects[n].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(_NolaPath(D)/"emblema-nola-macm5-3d.glb"), export_format='GLB', use_selection=True,
    export_apply=True, export_animations=False, export_yup=True, export_image_format='AUTO')
print("GLB OK")
