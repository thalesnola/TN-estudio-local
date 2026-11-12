# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["mediapipe==1.2.2", "opencv-python==4.12.0.88", "numpy<3"]
# ///
"""
Extrator de mocap com MediaPipe (API Tasks), para o estúdio local.

Lê um vídeo e grava um JSON com, por quadro:
  - pose_mundo: 33 pontos 3D do corpo em metros, origem no quadril (PoseLandmarker heavy);
  - pose_imagem: os mesmos 33 pontos em coordenadas da imagem (0..1), para enquadramento;
  - blendshapes: os 52 coeficientes faciais no padrão ARKit (FaceLandmarker);
  - cabeca: matriz 4x4 da rotação/posição da cabeça.

Roda isolado, sem tocar no Python do sistema:
    uv run mediapipe_mocap.py video.mp4 [-o saida.json] [--suavizar] [--sem-rosto]

O vídeo nunca sai da máquina: os modelos rodam localmente.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

MODELOS_PADRAO = (
    Path.home() / "Estudio" / "modelos" / "mediapipe"
    if sys.platform == "darwin"
    else Path(r"C:\Ferramentas\Estudio\modelos\mediapipe")
)
MODELO_POSE = "pose_landmarker_heavy.task"
MODELO_ROSTO = "face_landmarker.task"

# Índices da pose usados para recortar o rosto: nariz, olhos, orelhas, boca.
IDX_CABECA = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

vision = mp.tasks.vision
BaseOptions = mp.tasks.BaseOptions


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


class FiltroUmEuro:
    """Filtro One Euro (Casiez et al., 2012): tira tremor sem atrasar movimento rápido."""

    def __init__(self, freq: float, corte_min: float = 1.0, beta: float = 0.3, corte_d: float = 1.0):
        self.freq, self.corte_min, self.beta, self.corte_d = freq, corte_min, beta, corte_d
        self.x_ant = None
        self.dx_ant = None

    @staticmethod
    def _alfa(corte: float, freq: float) -> float:
        tau = 1.0 / (2 * math.pi * corte)
        return 1.0 / (1.0 + tau * freq)

    def __call__(self, x: np.ndarray) -> np.ndarray:
        if self.x_ant is None:
            self.x_ant, self.dx_ant = x, np.zeros_like(x)
            return x
        dx = (x - self.x_ant) * self.freq
        a_d = self._alfa(self.corte_d, self.freq)
        dx_hat = a_d * dx + (1 - a_d) * self.dx_ant
        corte = self.corte_min + self.beta * np.abs(dx_hat)
        a = 1.0 / (1.0 + (1.0 / (2 * math.pi * corte)) * self.freq)
        x_hat = a * x + (1 - a) * self.x_ant
        self.x_ant, self.dx_ant = x_hat, dx_hat
        return x_hat

    def reiniciar(self) -> None:
        self.x_ant = self.dx_ant = None


def caixa_do_rosto(pose_img, largura: int, altura: int, margem: float = 1.8):
    """Quadrado em volta da cabeça, a partir dos pontos da pose. None se a cabeça não aparece."""
    pts = [(pose_img[i].x * largura, pose_img[i].y * altura) for i in IDX_CABECA
           if (pose_img[i].visibility or 0) > 0.3]
    if len(pts) < 4:
        return None
    xs, ys = zip(*pts)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    lado = max(max(xs) - min(xs), max(ys) - min(ys)) * margem
    lado = max(lado, 48)
    x0, y0 = int(max(cx - lado / 2, 0)), int(max(cy - lado / 2, 0))
    x1, y1 = int(min(cx + lado / 2, largura)), int(min(cy + lado / 2, altura))
    if x1 - x0 < 24 or y1 - y0 < 24:
        return None
    return x0, y0, x1, y1


def extrair(video: Path, saida: Path, modelos: Path, suavizar: bool, com_rosto: bool,
            max_quadros: int | None) -> dict:
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise SystemExit(f"Não abriu o vídeo: {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    mp_pose = modelos / MODELO_POSE
    mp_rosto = modelos / MODELO_ROSTO
    for m in (mp_pose, mp_rosto):
        if not m.exists():
            raise SystemExit(f"Modelo ausente: {m}")

    pose = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(mp_pose)),
        running_mode=vision.RunningMode.VIDEO, num_poses=1))
    # Rosto em modo IMAGE sobre o recorte ampliado da cabeça: em plano de corpo inteiro o
    # rosto ocupa poucos pixels e o detector no quadro inteiro não o acha.
    rosto = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(mp_rosto)),
        running_mode=vision.RunningMode.IMAGE, num_faces=1,
        output_face_blendshapes=True, output_facial_transformation_matrixes=True)) if com_rosto else None

    filtro_pose = FiltroUmEuro(fps, corte_min=1.5, beta=0.5)
    filtro_bs = FiltroUmEuro(fps, corte_min=3.0, beta=1.0)
    nomes_bs: list[str] | None = None
    quadros = []
    n_pose = n_rosto = 0
    i = 0
    while True:
        ok, bgr = cap.read()
        if not ok or (max_quadros and i >= max_quadros):
            break
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        ts_ms = int(round(i * 1000.0 / fps))
        q = {"quadro": i, "t": round(i / fps, 4), "pose_mundo": None, "pose_imagem": None,
             "blendshapes": None, "cabeca": None}

        r = pose.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), ts_ms)
        if r.pose_world_landmarks:
            mundo = np.array([[p.x, p.y, p.z] for p in r.pose_world_landmarks[0]], dtype=float)
            vis = [round(p.visibility or 0, 3) for p in r.pose_world_landmarks[0]]
            if suavizar:
                mundo = filtro_pose(mundo)
            q["pose_mundo"] = [[round(float(v), 5) for v in p] + [vis[k]] for k, p in enumerate(mundo)]
            img = r.pose_landmarks[0]
            q["pose_imagem"] = [[round(p.x, 5), round(p.y, 5)] for p in img]
            n_pose += 1

            if rosto is not None:
                caixa = caixa_do_rosto(img, largura, altura)
                if caixa:
                    x0, y0, x1, y1 = caixa
                    rec = cv2.resize(rgb[y0:y1, x0:x1], (384, 384), interpolation=cv2.INTER_LANCZOS4)
                    rr = rosto.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rec)))
                    if rr.face_blendshapes:
                        cats = rr.face_blendshapes[0]
                        if nomes_bs is None:
                            nomes_bs = [c.category_name for c in cats]
                        vals = np.array([c.score for c in cats], dtype=float)
                        if suavizar:
                            vals = np.clip(filtro_bs(vals), 0, 1)
                        q["blendshapes"] = [round(float(v), 4) for v in vals]
                        if rr.facial_transformation_matrixes:
                            q["cabeca"] = np.round(np.asarray(rr.facial_transformation_matrixes[0]), 5).tolist()
                        n_rosto += 1
        else:
            filtro_pose.reiniciar()

        quadros.append(q)
        i += 1
        if i % 60 == 0:
            print(f"  {i}/{total} quadros", end="\r", file=sys.stderr)

    cap.release()
    pose.close()
    if rosto:
        rosto.close()

    dados = {
        "formato": "estudio-mocap/2",
        "metadados": {
            "origem": video.name, "fps": fps, "largura": largura, "altura": altura,
            "quadros": len(quadros), "quadros_com_pose": n_pose, "quadros_com_rosto": n_rosto,
            "suavizado": suavizar, "mediapipe": mp.__version__,
            "modelos": {MODELO_POSE: sha256(mp_pose), MODELO_ROSTO: sha256(mp_rosto)},
            "eixos": "pose_mundo em metros, origem no quadril; x = direita da imagem, y = para baixo, "
                     "z = negativo em direção à câmera",
        },
        "nomes_blendshapes": nomes_bs or [],
        "quadros": quadros,
    }
    saida.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"\n{saida}: {len(quadros)} quadros, pose em {n_pose}, rosto em {n_rosto}", file=sys.stderr)
    return dados


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("-o", "--saida", type=Path)
    ap.add_argument("--modelos", type=Path, default=MODELOS_PADRAO)
    ap.add_argument("--suavizar", action="store_true", help="filtro One Euro na pose e no rosto")
    ap.add_argument("--sem-rosto", action="store_true")
    ap.add_argument("--max-quadros", type=int)
    a = ap.parse_args()
    saida = a.saida or a.video.with_name(a.video.stem + "_mocap.json")
    extrair(a.video, saida, a.modelos, a.suavizar, not a.sem_rosto, a.max_quadros)


if __name__ == "__main__":
    main()
