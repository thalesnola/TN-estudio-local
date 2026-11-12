"""Monta a moeda 3D de uma instituicao a partir do mestre INSTITUICAO: FRENTE = escudo da instituicao (arte-fonte como textura,
   relevo por mapa de altura), VERSO = medalhao INSTITUICAO [UNIDADE] (geometria extrudada do padrao v7).
   uso: blender -b blend/_mestre-instituicao.blend -P scripts/construir.py -- SIGLA"""
import bpy, json, sys, os, numpy as np
from mathutils import Vector, geometry
sig = sys.argv[sys.argv.index("--") + 1]
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
F = os.path.join(R, "fontes")
J = json.load(open(os.path.join(F, sig + "-contorno.json")))
D = 0.11        # espessura do escudo (m)
RELEVO = 0.05   # altura maxima do relevo da frente (m)

for n in ("GEO-FaceVerso", "GEO-AroVerso", "GEO-Base"):
    bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
giro = bpy.data.objects["GIRO"]


def img(nome, cs):
    i = bpy.data.images.load(os.path.join(F, nome), check_existing=True)
    i.colorspace_settings.name = cs
    return i


def ntex(nt, i, loc):
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = i; t.location = loc; t.extension = 'EXTEND'
    return t


# ---- materiais
mf = bpy.data.materials.new(f"MAT-Frente-{sig}"); mf.use_nodes = True; nt = mf.node_tree
pb = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
cor = ntex(nt, img(f"{sig}-cor.png", "sRGB"), (-900, 200))
esm = ntex(nt, img(f"{sig}-esmalte.png", "Non-Color"), (-900, -200))
bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-600, 200)
bc.inputs["Bright"].default_value = 0.02; bc.inputs["Contrast"].default_value = 0.15
nt.links.new(cor.outputs["Color"], bc.inputs["Color"]); nt.links.new(bc.outputs["Color"], pb.inputs["Base Color"])
mt = nt.nodes.new("ShaderNodeMapRange"); mt.location = (-600, -100)
mt.inputs["To Min"].default_value = 0.85; mt.inputs["To Max"].default_value = 0.12      # esmalte => pouco metal
nt.links.new(esm.outputs["Color"], mt.inputs["Value"]); nt.links.new(mt.outputs["Result"], pb.inputs["Metallic"])
rg = nt.nodes.new("ShaderNodeMapRange"); rg.location = (-600, -350)
rg.inputs["To Min"].default_value = 0.30; rg.inputs["To Max"].default_value = 0.30
nt.links.new(esm.outputs["Color"], rg.inputs["Value"])
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.location = (-900, -500)
nz.inputs["Scale"].default_value = 180; nz.inputs["Detail"].default_value = 4
mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY_ADD'; mu.location = (-380, -450)
mu.inputs[1].default_value = 0.16
nt.links.new(nz.outputs["Fac"], mu.inputs[0]); nt.links.new(rg.outputs["Result"], mu.inputs[2])
ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'ADD'; ad.location = (-200, -450); ad.inputs[1].default_value = -0.07
nt.links.new(mu.outputs["Value"], ad.inputs[0]); nt.links.new(ad.outputs["Value"], pb.inputs["Roughness"])
cw = nt.nodes.new("ShaderNodeMath"); cw.operation = 'MULTIPLY'; cw.inputs[1].default_value = 0.25; cw.location = (-380, -600)
nt.links.new(esm.outputs["Color"], cw.inputs[0]); nt.links.new(cw.outputs["Value"], pb.inputs["Coat Weight"])
pb.inputs["Coat Roughness"].default_value = 0.08

ml = bpy.data.materials.new(f"MAT-Lateral-{sig}"); ml.use_nodes = True
p2 = next(n for n in ml.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
p2.inputs["Base Color"].default_value = (*J["rim_rgb"], 1); p2.inputs["Metallic"].default_value = 1; p2.inputs["Roughness"].default_value = 0.28
campo = bpy.data.materials["MAT-Campo"]

# ---- corpo do escudo (extrusao do contorno; +Z local = frente)
P = [tuple(p) for p in J["poly"]]
if sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P))) < 0:
    P = P[::-1]   # anti-horario
n = len(P)
me = bpy.data.meshes.new(f"Escudo-{sig}")
verts = [(x, y, 0) for x, y in P] + [(x, y, -D) for x, y in P]
tris = geometry.tessellate_polygon([[Vector((x, y, 0)) for x, y in P]])
faces = []; mats = []
for t in tris: faces.append(tuple(t)); mats.append(0)
for t in tris: faces.append((t[0] + n, t[2] + n, t[1] + n)); mats.append(1)
for i in range(n):
    j = (i + 1) % n; faces.append((i, i + n, j + n, j)); mats.append(2)
me.from_pydata(verts, [], faces); me.update()
for f, mi in zip(me.polygons, mats): f.material_index = mi
for mm in (mf, campo, ml): me.materials.append(mm)
uv = me.uv_layers.new(name="UVMap"); W, H = J["largura_m"], J["altura_m"]
for f in me.polygons:
    for li in f.loop_indices:
        v = me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv = (v.x / W + 0.5, v.y / H + 0.5)
body = bpy.data.objects.new(f"GEO-Escudo-{sig}", me); bpy.context.collection.objects.link(body)
body.parent = giro; body.rotation_euler = (1.5707963, 0, 0)
bv = body.modifiers.new("Bisel", "BEVEL"); bv.width = 0.012; bv.segments = 3; bv.limit_method = 'ANGLE'; bv.angle_limit = 0.7
bpy.context.view_layer.objects.active = body; body.select_set(True)
bpy.ops.object.shade_smooth_by_angle(angle=0.6); body.select_set(False)

# ---- malha de relevo (grade recortada pela mascara)
mk = bpy.data.images.load(os.path.join(F, sig + "-mascara-grade.png"), check_existing=True)
ww, hh = mk.size; mk = (np.array(mk.pixels[:], np.float32).reshape(hh, ww, 4)[::-1, :, 0] > 0.5).astype(np.uint8)
step = 0.002; nx = int(W / step) + 1; ny = int(H / step) + 1
xs = np.linspace(-W / 2, W / 2, nx); ys = np.linspace(-H / 2, H / 2, ny)
X, Y = np.meshgrid(xs, ys)
px = np.clip(((X / W + 0.5) * (ww - 1)).round().astype(int), 0, ww - 1)
py = np.clip(((0.5 - Y / H) * (hh - 1)).round().astype(int), 0, hh - 1)
dentro = mk[py, px] > 0
idx = -np.ones(X.shape, np.int64); k = int(dentro.sum()); idx[dentro] = np.arange(k)
a = idx[:-1, :-1]; b = idx[:-1, 1:]; c = idx[1:, 1:]; d = idx[1:, :-1]
ok = (a >= 0) & (b >= 0) & (c >= 0) & (d >= 0)
quads = np.stack([a[ok], b[ok], c[ok], d[ok]], 1).astype(np.int32)
gm = bpy.data.meshes.new(f"Relevo-{sig}")
co = np.zeros((k, 3), np.float32); co[:, 0] = X[dentro]; co[:, 1] = Y[dentro]
gm.vertices.add(k); gm.vertices.foreach_set("co", co.ravel())
gm.loops.add(len(quads) * 4); gm.polygons.add(len(quads))
gm.loops.foreach_set("vertex_index", quads.ravel())
gm.polygons.foreach_set("loop_start", np.arange(0, len(quads) * 4, 4, dtype=np.int32))
gm.polygons.foreach_set("loop_total", np.full(len(quads), 4, np.int32))
gm.polygons.foreach_set("use_smooth", np.ones(len(quads), bool))
gm.update(calc_edges=True)
guv = gm.uv_layers.new(name="UVMap")
uvs = np.stack([co[:, 0] / W + 0.5, co[:, 1] / H + 0.5], 1)[quads.ravel()]
guv.data.foreach_set("uv", uvs.ravel().astype(np.float32))
gm.materials.append(mf)
rel = bpy.data.objects.new(f"GEO-Relevo-{sig}", gm); bpy.context.collection.objects.link(rel)
rel.parent = giro; rel.rotation_euler = (1.5707963, 0, 0); rel.location = (0, -0.0015, 0)   # +Z local = -Y mundo; sobe 1,5 mm
tx = bpy.data.textures.new(f"Altura-{sig}", "IMAGE"); tx.image = img(f"{sig}-altura16.png", "Non-Color")
dm = rel.modifiers.new("Relevo", "DISPLACE"); dm.texture = tx; dm.texture_coords = 'UV'; dm.uv_layer = "UVMap"
dm.strength = RELEVO; dm.mid_level = 0.0; dm.direction = 'NORMAL'

# ---- medalhao INSTITUICAO no verso (+Y mundo)
md = J["medalhao"]; s = 0.90 * md["raio"]   # aro externo do medalhao (raio 1,02 no mestre) = 92% do circulo inscrito
med = bpy.data.objects.new("MED-INSTITUICAO", None); bpy.context.collection.objects.link(med)
med.parent = giro; med.location = (md["x"], D + 0.004, md["y"]); med.rotation_euler = (0, 0, 3.14159265); med.scale = (s, s, s)
for nm in ("GEO-Aro", "GEO-FaceCampo", "GEO-FaceLetras"):
    o = bpy.data.objects[nm]; o.parent = med; o.matrix_parent_inverse.identity()

bpy.ops.outliner.orphans_purge(do_recursive=True)
for o in bpy.data.objects:
    if o.type == 'MESH':
        print("OBJ", o.name, len(o.data.vertices), [round(v, 3) for v in o.dimensions])
bpy.context.scene.frame_set(1)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R, "blend", f"emblema-{sig.lower()}-3d.blend"))
print("SALVO", sig)
