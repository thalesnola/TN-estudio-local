"""Esfera 3D de uma instituicao: hemisferio da FRENTE = escudo (projecao azimutal equidistante, relevo por mapa de altura),
   hemisferio da COSTA = medalhao INSTITUICAO [UNIDADE]. Faixa de metal no equador. Gira no GIRO do mestre INSTITUICAO v7 (camera, luzes, mundo).
   uso: blender -b blend/_mestre-instituicao.blend -P scripts/construir_esfera.py -- SIGLA   (antes: preparar.py e preparar_esfera.py)"""
import bpy, bmesh, json, sys, os, numpy as np
sig = sys.argv[sys.argv.index("--") + 1]
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
F = os.path.join(R, "fontes")
J = json.load(open(os.path.join(F, sig + "-contorno.json")))
RELEVO = 0.035
SEG, RINGS = 1440, 720

for o in list(bpy.data.objects):
    if o.name.startswith(("GEO-", "MED-")): bpy.data.objects.remove(o, do_unlink=True)
giro = bpy.data.objects["GIRO"]


def img(nome, cs):
    i = bpy.data.images.load(os.path.join(F, nome), check_existing=True); i.colorspace_settings.name = cs; return i


def arr(i):
    w, h = i.size; return np.array(i.pixels[:], np.float32).reshape(h, w, 4)[..., 0], w, h


def amostra(a, w, h, u, v):   # bilinear; u,v em [0,1], v para cima
    x = np.clip(u * (w - 1), 0, w - 1); y = np.clip(v * (h - 1), 0, h - 1)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); x1 = np.minimum(x0 + 1, w - 1); y1 = np.minimum(y0 + 1, h - 1)
    fx = x - x0; fy = y - y0
    return (a[y0, x0] * (1 - fx) * (1 - fy) + a[y0, x1] * fx * (1 - fy) + a[y1, x0] * (1 - fx) * fy + a[y1, x1] * fx * fy)


def material(nome, cor, esm=None, metal_fixo=None):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree
    pb = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    c = nt.nodes.new("ShaderNodeTexImage"); c.image = img(cor, "sRGB"); c.extension = 'EXTEND'; c.location = (-900, 200)
    bc = nt.nodes.new("ShaderNodeBrightContrast"); bc.location = (-600, 200)
    bc.inputs["Bright"].default_value = 0.02; bc.inputs["Contrast"].default_value = 0.15
    nt.links.new(c.outputs["Color"], bc.inputs["Color"]); nt.links.new(bc.outputs["Color"], pb.inputs["Base Color"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.location = (-900, -500); nz.inputs["Scale"].default_value = 180; nz.inputs["Detail"].default_value = 4
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY_ADD'; mu.location = (-380, -450); mu.inputs[1].default_value = 0.16
    nt.links.new(nz.outputs["Fac"], mu.inputs[0])
    ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'ADD'; ad.location = (-200, -450); ad.inputs[1].default_value = -0.07
    nt.links.new(mu.outputs["Value"], ad.inputs[0]); nt.links.new(ad.outputs["Value"], pb.inputs["Roughness"])
    if esm:
        e = nt.nodes.new("ShaderNodeTexImage"); e.image = img(esm, "Non-Color"); e.extension = 'EXTEND'; e.location = (-900, -200)
        mt = nt.nodes.new("ShaderNodeMapRange"); mt.location = (-600, -100)
        mt.inputs["To Min"].default_value = 0.85; mt.inputs["To Max"].default_value = 0.12
        nt.links.new(e.outputs["Color"], mt.inputs["Value"]); nt.links.new(mt.outputs["Result"], pb.inputs["Metallic"])
        rg = nt.nodes.new("ShaderNodeMapRange"); rg.location = (-600, -350)
        rg.inputs["To Min"].default_value = 0.30; rg.inputs["To Max"].default_value = 0.30
        nt.links.new(e.outputs["Color"], rg.inputs["Value"]); nt.links.new(rg.outputs["Result"], mu.inputs[2])
        cw = nt.nodes.new("ShaderNodeMath"); cw.operation = 'MULTIPLY'; cw.inputs[1].default_value = 0.25; cw.location = (-380, -600)
        nt.links.new(e.outputs["Color"], cw.inputs[0]); nt.links.new(cw.outputs["Value"], pb.inputs["Coat Weight"])
        pb.inputs["Coat Roughness"].default_value = 0.08
        rg.inputs["To Max"].default_value = 0.30; rg.inputs["To Min"].default_value = 0.30
    else:
        pb.inputs["Metallic"].default_value = metal_fixo
        # campo escuro = preto acetinado liso; so o prata da arte usa a textura (evita manchas da iluminacao embutida na imagem)
        bw = nt.nodes.new("ShaderNodeRGBToBW"); bw.location = (-750, -100); nt.links.new(c.outputs["Color"], bw.inputs["Color"])
        mk = nt.nodes.new("ShaderNodeMapRange"); mk.location = (-600, -100); mk.clamp = True
        mk.inputs["From Min"].default_value = 0.10; mk.inputs["From Max"].default_value = 0.24
        nt.links.new(bw.outputs["Val"], mk.inputs["Value"])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.location = (-420, 300)
        mx.inputs["A"].default_value = (0.022, 0.022, 0.024, 1)
        nt.links.new(mk.outputs["Result"], mx.inputs["Factor"]); nt.links.new(c.outputs["Color"], mx.inputs["B"])
        nt.links.new(mx.outputs["Result"], bc.inputs["Color"])
        rr = nt.nodes.new("ShaderNodeMapRange"); rr.location = (-600, -300)
        rr.inputs["To Min"].default_value = 0.55; rr.inputs["To Max"].default_value = 0.28
        nt.links.new(mk.outputs["Result"], rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], mu.inputs[2])
    return m


def hemisferio(nome, frente, imgcor, imgalt, centro, k, mat):
    """k = raio do circulo no mapa (fracao da largura do mapa); centro = (u,v) do mapa. Malha gerada direto em numpy (polo + aneis)."""
    N = RINGS // 2
    th_r = np.arange(1, N + 1) / N * (np.pi / 2); ph_r = np.arange(SEG) / SEG * 2 * np.pi
    TH, PH = np.meshgrid(th_r, ph_r, indexing="ij")
    th = np.r_[0.0, TH.ravel()]; ph = np.r_[0.0, PH.ravel()]
    sgn = 1.0 if frente else -1.0
    d = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), sgn * np.cos(th)], 1)
    r = 0.5 * (np.sin(th) + th / (np.pi / 2))  # mistura ortografica (emblema 'de frente') e equidistante (menos esticado no limbo)
    sx = 1.0 if frente else -1.0                                   # costa vista de tras: espelha u
    u = centro[0] + k * r * np.cos(ph) * sx; v = centro[1] + k * r * np.sin(ph)
    a_, w, h = arr(imgalt); alt = amostra(a_, w, h, u, v)
    co = (d * (1.0 + RELEVO * alt)[:, None]).astype(np.float32)
    idx = lambda i, j: 1 + i * SEG + (j % SEG)
    J_ = np.arange(SEG)
    tri = np.stack([np.zeros(SEG, int), idx(0, J_), idx(0, J_ + 1)], 1)                  # leque no polo
    I, Jg = np.meshgrid(np.arange(N - 1), J_, indexing="ij"); I = I.ravel(); Jg = Jg.ravel()
    A, B_, C, D_ = idx(I, Jg), idx(I, Jg + 1), idx(I + 1, Jg + 1), idx(I + 1, Jg)
    quad = np.stack([A, D_, C, B_], 1)
    if not frente: tri = tri[:, ::-1]; quad = quad[:, ::-1]
    # quads -> 2 triangulos nao: manter ngons de 4 e triangulos juntos
    me = bpy.data.meshes.new(nome)
    nv = len(co); me.vertices.add(nv); me.vertices.foreach_set("co", co.ravel())
    nl = len(tri) * 3 + len(quad) * 4; npoly = len(tri) + len(quad)
    me.loops.add(nl); me.polygons.add(npoly)
    me.loops.foreach_set("vertex_index", np.r_[tri.ravel(), quad.ravel()].astype(np.int32))
    starts = np.r_[np.arange(len(tri)) * 3, len(tri) * 3 + np.arange(len(quad)) * 4].astype(np.int32)
    me.polygons.foreach_set("loop_start", starts); me.polygons.foreach_set("loop_total", np.r_[np.full(len(tri), 3), np.full(len(quad), 4)].astype(np.int32))
    me.polygons.foreach_set("use_smooth", np.ones(npoly, bool)); me.update(calc_edges=True)
    uvl = me.uv_layers.new(name="UVMap")
    li = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", li)
    uvl.data.foreach_set("uv", np.stack([u[li], v[li]], 1).astype(np.float32).ravel())
    me.materials.append(mat)
    ob = bpy.data.objects.new(nome, me); bpy.context.collection.objects.link(ob)
    ob.parent = giro; ob.rotation_euler = (1.5707963, 0, 0)
    return ob


# ---- frente: escudo na tela quadrada (circulo inscrito = hemisferio)
mat_f = material(f"MAT-Frente-{sig}", f"{sig}-esf-cor.png", esm=f"{sig}-esf-esmalte.png")
hemisferio(f"GEO-Frente-{sig}", True, None, img(f"{sig}-esf-altura16.png", "Non-Color"), (0.5, 0.5), 0.5, mat_f)
# ---- costa: medalhao INSTITUICAO (disco centrado em (621,610) px, raio 572 px na tela de 1254)
mat_b = material("MAT-Costa-INSTITUICAO", "INSTITUICAO-cor.png", metal_fixo=1.0)
hemisferio("GEO-Costa-INSTITUICAO", False, None, img("INSTITUICAO-altura16.png", "Non-Color"), (621 / 1254, 1 - 610 / 1254), 572 / 1254, mat_b)
# ---- faixa de metal no equador (cobre a emenda)
bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.016, major_segments=360, minor_segments=24)
t = bpy.context.object; t.name = "GEO-Equador"; t.parent = giro; t.rotation_euler = (1.5707963, 0, 0)
t.data.materials.append(bpy.data.materials["MAT-Metal"]); t.data.polygons.foreach_set("use_smooth", np.ones(len(t.data.polygons), bool))

bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.context.scene.frame_set(1)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R, "blend", f"esfera-{sig.lower()}-3d.blend"))
print("SALVO", sig)
