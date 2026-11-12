import bpy, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r"C:\Users\<USUARIO>\Documents\Emblema-INSTITUICAO-Padrao\modelo-3d\emblema-instituicao-3d.glb")
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
print("MALHAS",len(objs),sum(len(o.data.polygons) for o in objs))
mn=Vector((1e9,)*3); mx=Vector((-1e9,)*3)
for o in objs:
    for c in o.bound_box:
        w=o.matrix_world@Vector(c); mn=Vector(map(min,mn,w)); mx=Vector(map(max,mx,w))
print("BBOX",[round(x,3) for x in (mx-mn)])
w=bpy.data.worlds.new("W"); w.use_nodes=True; w.node_tree.nodes["Background"].inputs[0].default_value=(0.6,0.6,0.62,1); w.node_tree.nodes["Background"].inputs[1].default_value=1.0
bpy.context.scene.world=w
bpy.ops.object.light_add(type='AREA',location=(2,-3,3)); l=bpy.context.object; l.data.energy=400; l.data.size=3
l.rotation_euler=(Vector((0,0,0))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-5,0.3)); cam=bpy.context.object; bpy.context.scene.camera=cam
cam.rotation_euler=(Vector((0,0,0.0))-cam.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene; s.render.engine='BLENDER_EEVEE_NEXT'; s.render.resolution_x=s.render.resolution_y=700
for tag,rz in (("verso",math.pi),):
    for o in bpy.context.scene.objects:
        if o.parent is None and o.type in ('EMPTY','MESH'): o.rotation_mode='XYZ'; o.rotation_euler=(0,0,rz)
    s.render.filepath=r"C:\tmp\giro2\glb_%s.png"%tag; bpy.ops.render.render(write_still=True)
