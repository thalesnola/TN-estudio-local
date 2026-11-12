"""
Importador de mocap para o Blender 4.5 (par do mediapipe_mocap.py).

Cria na cena:
  - coleção "Mocap" com um Empty por ponto da pose (MP_00 ... MP_32) e três pontos médios
    (MP_quadril, MP_ombros, MP_cabeca), todos com keyframes;
  - armature "MocapRig" (bacia, coluna, pescoço, cabeça, braços, antebraços, coxas, canelas, pés)
    que segue os Empties por constraints; com --assar vira só keyframes, sem constraints;
  - Empty "MP_rosto" com uma propriedade por blendshape ARKit (eyeBlinkLeft, jawOpen...) e a
    rotação da cabeça; com --malha, as shape keys de mesmo nome da malha ganham drivers.

Uso no terminal:
  blender -b cena.blend -P blender_apply_mocap.py -- dados_mocap.json [--malha Rosto] [--assar] [--salvar saida.blend]
Uso pelo MCP (execute_blender_code):
  import os, sys; sys.path.append(os.path.expanduser("~/GitHub/estudio-local/scripts/3d"))
  import blender_apply_mocap as m; m.aplicar(".../dados_mocap.json", malha="Rosto")

Eixos: o vídeo vira a vista frontal do Blender (numpad 1). O personagem fica no chão (z = 0)
quadro a quadro, porque a pose do MediaPipe tem origem no quadril e não traz deslocamento.
"""

from __future__ import annotations

import json
import sys

import bpy
from mathutils import Matrix, Vector

# Ossos: nome -> (ponto da cabeça do osso, ponto para onde aponta, pai)
OSSOS = {
    "bacia":      ("MP_quadril", "MP_23", None),
    "coluna":     ("MP_quadril", "MP_ombros", None),
    "pescoco":    ("MP_ombros", "MP_cabeca", "coluna"),
    "cabeca":     ("MP_cabeca", "MP_00", "pescoco"),
    "braco.L":    ("MP_11", "MP_13", "coluna"),
    "antebraco.L": ("MP_13", "MP_15", "braco.L"),
    "braco.R":    ("MP_12", "MP_14", "coluna"),
    "antebraco.R": ("MP_14", "MP_16", "braco.R"),
    "coxa.L":     ("MP_23", "MP_25", "bacia"),
    "canela.L":   ("MP_25", "MP_27", "coxa.L"),
    "pe.L":       ("MP_27", "MP_31", "canela.L"),
    "coxa.R":     ("MP_24", "MP_26", "bacia"),
    "canela.R":   ("MP_26", "MP_28", "coxa.R"),
    "pe.R":       ("MP_28", "MP_32", "canela.R"),
}
PES = (27, 28, 29, 30, 31, 32)
# MediaPipe (x direita, y baixo, z para a câmera negativo) -> Blender vista frontal (x, z, -y)
def _mp_para_blender(p):
    return Vector((p[0], p[2], -p[1]))

# Rosto do MediaPipe (x direita, y cima, z para o espectador) -> Blender (x, -z, y)
_P = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))


def _fcurves(obj):
    """Canal de F-curves do objeto, compatível com as ações em camadas do 4.4+."""
    ad = obj.animation_data
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
        if cb is not None:
            return cb.fcurves
    except (ImportError, AttributeError):
        pass
    return ad.action.fcurves


def _gravar(obj, caminho: str, n_indices: int, quadros: list[int], valores: list[list[float]]):
    """Grava muitos keyframes de uma vez (keyframe_insert quadro a quadro é lento demais)."""
    if not quadros:
        return
    obj.keyframe_insert(caminho, frame=quadros[0])
    fcs = _fcurves(obj)
    for k in range(n_indices):
        fc = fcs.find(caminho, index=k) if n_indices > 1 else (fcs.find(caminho, index=0) or fcs.find(caminho))
        fc.keyframe_points.clear()
        fc.keyframe_points.add(len(quadros))
        co = []
        for q, v in zip(quadros, valores):
            co += [q, v[k]]
        fc.keyframe_points.foreach_set("co", co)
        fc.keyframe_points.foreach_set("interpolation", [1] * len(quadros))  # LINEAR
        fc.update()


def _colecao(nome: str):
    col = bpy.data.collections.get(nome)
    if col is None:
        col = bpy.data.collections.new(nome)
        bpy.context.scene.collection.children.link(col)
    return col


def _empty(nome: str, col, tamanho=0.03, tipo="SPHERE"):
    obj = bpy.data.objects.get(nome)
    if obj is None:
        obj = bpy.data.objects.new(nome, None)
        col.objects.link(obj)
    obj.empty_display_type = tipo
    obj.empty_display_size = tamanho
    if obj.animation_data:
        obj.animation_data_clear()
    return obj


def aplicar(caminho_json: str, malha: str | None = None, assar: bool = False, quadro_inicial: int = 1):
    with open(caminho_json, encoding="utf-8") as f:
        dados = json.load(f)
    meta, quadros = dados["metadados"], dados["quadros"]
    cena = bpy.context.scene
    cena.render.fps = max(1, round(meta["fps"]))
    col = _colecao("Mocap")

    # 1. Pontos da pose, já no chão
    trilhas: dict[str, tuple[list[int], list[list[float]]]] = {}
    def guardar(nome, q, v):
        trilhas.setdefault(nome, ([], []))
        trilhas[nome][0].append(q)
        trilhas[nome][1].append(list(v))

    for item in quadros:
        pts = item.get("pose_mundo")
        if not pts:
            continue
        q = quadro_inicial + item["quadro"]
        bp = [_mp_para_blender(p) for p in pts]
        chao = min(bp[i].z for i in PES)
        bp = [v - Vector((0, 0, chao)) for v in bp]
        for i, v in enumerate(bp):
            guardar(f"MP_{i:02d}", q, v)
        guardar("MP_quadril", q, (bp[23] + bp[24]) / 2)
        guardar("MP_ombros", q, (bp[11] + bp[12]) / 2)
        guardar("MP_cabeca", q, (bp[7] + bp[8]) / 2)

    if not trilhas:
        raise RuntimeError("Nenhum quadro com pose no JSON.")
    empties = {}
    for nome, (qs, vs) in trilhas.items():
        e = _empty(nome, col, 0.05 if nome in ("MP_quadril", "MP_ombros", "MP_cabeca") else 0.025)
        e.location = vs[0]
        _gravar(e, "location", 3, qs, vs)
        empties[nome] = e

    # 2. Armature na pose do primeiro quadro válido
    rig = bpy.data.objects.get("MocapRig")
    if rig is None:
        arm = bpy.data.armatures.new("MocapRig")
        rig = bpy.data.objects.new("MocapRig", arm)
        col.objects.link(rig)
    arm = rig.data
    arm.display_type = "STICK"
    rig.show_in_front = True
    pos0 = {n: Vector(v[1][0]) for n, v in trilhas.items()}
    for o in bpy.context.view_layer.objects.selected:
        o.select_set(False)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for eb in list(arm.edit_bones):
        arm.edit_bones.remove(eb)
    for nome, (ini, fim, pai) in OSSOS.items():
        eb = arm.edit_bones.new(nome)
        eb.head, eb.tail = pos0[ini], pos0[fim]
        if (eb.tail - eb.head).length < 1e-3:
            eb.tail = eb.head + Vector((0, 0, 0.05))
    for nome, (_, _, pai) in OSSOS.items():
        if pai:
            arm.edit_bones[nome].parent = arm.edit_bones[pai]
    bpy.ops.object.mode_set(mode="POSE")
    for nome, (ini, fim, _) in OSSOS.items():
        pb = rig.pose.bones[nome]
        for c in list(pb.constraints):
            pb.constraints.remove(c)
        cl = pb.constraints.new("COPY_LOCATION")
        cl.target = empties[ini]
        dt = pb.constraints.new("DAMPED_TRACK")
        dt.target = empties[fim]

    # 3. Rosto: blendshapes como propriedades + rotação da cabeça
    nomes_bs = dados.get("nomes_blendshapes") or []
    rosto = None
    com_rosto = [it for it in quadros if it.get("blendshapes")]
    if nomes_bs and com_rosto:
        rosto = _empty("MP_rosto", col, 0.12, "ARROWS")
        rosto.parent = None
        rosto.rotation_mode = "XYZ"
        qs = [quadro_inicial + it["quadro"] for it in com_rosto]
        for k, nome in enumerate(nomes_bs):
            if nome.startswith("_"):
                continue
            rosto[nome] = 0.0
            rosto.id_properties_ui(nome).update(min=0.0, max=1.0)
            _gravar(rosto, f'["{nome}"]', 1, qs, [[it["blendshapes"][k]] for it in com_rosto])
        rot_q, rot_v = [], []
        for it in com_rosto:
            if it.get("cabeca"):
                m = Matrix([r[:3] for r in it["cabeca"][:3]])
                rot_q.append(quadro_inicial + it["quadro"])
                rot_v.append(list((_P @ m @ _P.transposed()).to_euler("XYZ")))
        _gravar(rosto, "rotation_euler", 3, rot_q, rot_v)
        cr = rig.pose.bones["cabeca"].constraints.new("COPY_ROTATION")
        cr.target = rosto
        cr.mix_mode = "ADD"
        cr.target_space = cr.owner_space = "LOCAL"

        if malha:
            alvo = bpy.data.objects.get(malha)
            chaves = alvo.data.shape_keys.key_blocks if alvo and alvo.data.shape_keys else {}
            ligadas = 0
            por_nome = {kb.name.lower(): kb for kb in chaves}
            for nome in nomes_bs:
                kb = por_nome.get(nome.lower())
                if kb is None:
                    continue
                kb.driver_remove("value")
                drv = kb.driver_add("value").driver
                drv.type = "AVERAGE"
                var = drv.variables.new()
                var.targets[0].id = rosto
                var.targets[0].data_path = f'["{nome}"]'
                ligadas += 1
            print(f"[mocap] {ligadas} shape keys de '{malha}' ligadas aos blendshapes")
    bpy.ops.object.mode_set(mode="OBJECT")

    ultimo = quadro_inicial + quadros[-1]["quadro"]
    cena.frame_start, cena.frame_end = quadro_inicial, ultimo

    if assar:
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode="POSE")
        bpy.ops.pose.select_all(action="SELECT")
        bpy.ops.nla.bake(frame_start=quadro_inicial, frame_end=ultimo, only_selected=True,
                         visual_keying=True, clear_constraints=True, bake_types={"POSE"})
        bpy.ops.object.mode_set(mode="OBJECT")

    print(f"[mocap] {len(trilhas['MP_00'][0])} quadros de pose, {len(com_rosto)} de rosto, "
          f"quadros {quadro_inicial}-{ultimo}, {cena.render.fps} fps, assado={assar}")
    return rig


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not args:
        print("Uso: blender -b cena.blend -P blender_apply_mocap.py -- dados.json [--malha N] [--assar] [--salvar x.blend]")
        sys.exit(1)
    def opt(nome):
        return args[args.index(nome) + 1] if nome in args else None
    aplicar(args[0], malha=opt("--malha"), assar="--assar" in args)
    if opt("--salvar"):
        bpy.ops.wm.save_as_mainfile(filepath=opt("--salvar"))
