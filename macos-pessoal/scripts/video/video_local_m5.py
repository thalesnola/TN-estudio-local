#!/usr/bin/env python3
"""
Utilitário unificado de Geração e Processamento de Vídeo/Áudio/Imagem Local no Apple M5 Pro (nola-macm5).

Aproveita os 48 GB de memória unificada, 20 núcleos de GPU Metal 4 (MLX) e Media Engine (VideoToolbox):
  1. Libera automaticamente modelos carregados no Ollama (`ollama ps` -> `ollama stop`) antes de tarefas MLX pesadas;
  2. `video`: gera vídeo T2V ou I2V (com ou sem áudio sincronizado) via `mlx_video` (LTX-2 em MLX Metal);
  3. `imagem`: gera imagem local rápida com `mflux-generate-z-image-turbo` (Z-Image-Turbo 8 passos);
  4. `upscale-img`: super-resolução de imagem/quadro com `mflux-upscale-seedvr2` em MLX;
  5. `upscale-video`: upscale rápido de clipe (720p -> 1080p) com Lanczos + `h264_videotoolbox` ou `prores_videotoolbox`;
  6. `transcrever`: conferência ultrarrápida de fala de clipe em GPU Metal via `mlx_audio.stt.generate` (com filtro de alucinação em clipe mudo).

Uso:
  python3 video_local_m5.py status
  python3 video_local_m5.py liberar-ram
  python3 video_local_m5.py video --prompt "..." [--image quadro0.png] [--com-audio] [-o saida.mp4]
  python3 video_local_m5.py imagem --prompt "..." [-o folha.png] [--width 1280 --height 720]
  python3 video_local_m5.py upscale-img entrada.png [-o saida_2x.png] [--resolution 2x]
  python3 video_local_m5.py upscale-video clipe_720p.mp4 [-o clipe_1080p.mp4] [--prores]
  python3 video_local_m5.py transcrever clipe.mp4 [--idioma pt]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ESTUDIO_DIR = Path.home() / "Estudio"
LTX_BIN = ESTUDIO_DIR / "ltx-venv" / "bin"
IMG_BIN = ESTUDIO_DIR / "imagem-venv" / "bin"
FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"
OLLAMA = "/opt/homebrew/bin/ollama"

ALUCINACOES_WHISPER = (
    "amara.org",
    "legendas pela comunidade",
    "subtitles by",
    "obrigado por assistir",
)


def liberar_ollama() -> list[str]:
    """Descarrega modelos ativos no Ollama da RAM unificada para liberar espaço ao MLX Metal."""
    if not Path(OLLAMA).exists():
        return []
    try:
        out = subprocess.check_output([OLLAMA, "ps"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return []
    linhas = [l.strip() for l in out.splitlines()[1:] if l.strip()]
    parados = []
    for l in linhas:
        modelo = l.split()[0]
        subprocess.run([OLLAMA, "stop", modelo], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        parados.append(modelo)
    if parados:
        print(f"[m5-ram] Modelos Ollama descarregados da memória unificada: {', '.join(parados)}", file=sys.stderr)
    return parados


def lufs_audio(caminho: Path) -> float:
    r = subprocess.run(
        [FFMPEG, "-hide_banner", "-nostats", "-i", str(caminho), "-af", "ebur128", "-f", "null", "-"],
        capture_output=True,
        text=True,
    ).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
    return float(m[-1]) if m else -70.0


def cmd_status(_args: argparse.Namespace) -> None:
    print("=== Estado do Pipeline de Vídeo/Mídia Local (nola-macm5 — M5 Pro 48 GB) ===")
    for nome, p in [
        ("mlx_video.generate (LTX-2)", LTX_BIN / "mlx_video.generate"),
        ("mlx_video.generate_av (LTX-2 + Áudio)", LTX_BIN / "mlx_video.generate_av"),
        ("mlx_audio.stt.generate (STT Metal)", LTX_BIN / "mlx_audio.stt.generate"),
        ("mflux-generate-z-image-turbo", IMG_BIN / "mflux-generate-z-image-turbo"),
        ("mflux-upscale-seedvr2", IMG_BIN / "mflux-upscale-seedvr2"),
        ("ffmpeg (VideoToolbox)", Path(FFMPEG)),
    ]:
        ok = "OK" if p.exists() and os.access(p, os.X_OK) else "AUSENTE"
        print(f"  - {nome}: {ok} ({p})")
    if Path(OLLAMA).exists():
        ps = subprocess.check_output([OLLAMA, "ps"], text=True).strip()
        print(f"\n=== Ollama na memória unificada ===\n{ps}")


def cmd_video(args: argparse.Namespace) -> None:
    liberar_ollama()
    bin_path = LTX_BIN / ("mlx_video.generate_av" if args.com_audio else "mlx_video.generate")
    cmd = [
        str(bin_path),
        "--prompt",
        args.prompt,
        "--width",
        str(args.width),
        "--height",
        str(args.height),
        "--num-frames",
        str(args.frames),
        "--fps",
        str(args.fps),
        "--seed",
        str(args.seed),
        "--output-path",
        str(args.saida),
        "--tiling",
        args.tiling,
    ]
    if args.image:
        cmd += ["--image", str(args.image), "--image-strength", str(args.image_strength)]
    if args.model_repo:
        cmd += ["--model-repo", args.model_repo]
    if args.enhance_prompt:
        cmd.append("--enhance-prompt")
    print("[m5-video] Executando:", " ".join(cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)


def cmd_imagem(args: argparse.Namespace) -> None:
    liberar_ollama()
    bin_path = IMG_BIN / "mflux-generate-z-image-turbo"
    cmd = [
        str(bin_path),
        "--prompt",
        args.prompt,
        "--width",
        str(args.width),
        "--height",
        str(args.height),
        "--steps",
        str(args.steps),
        "--seed",
        str(args.seed),
        "--output",
        str(args.saida),
    ]
    print("[m5-imagem] Executando:", " ".join(cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)


def cmd_upscale_img(args: argparse.Namespace) -> None:
    liberar_ollama()
    bin_path = IMG_BIN / "mflux-upscale-seedvr2"
    cmd = [
        str(bin_path),
        "--image-path",
        str(args.entrada),
        "--resolution",
        args.resolution,
        "--softness",
        str(args.softness),
        "--vae-tiling",
        "--output",
        str(args.saida),
    ]
    if args.quantize:
        cmd += ["--quantize", str(args.quantize)]
    print("[m5-upscale-img] Executando:", " ".join(cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)


def cmd_upscale_video(args: argparse.Namespace) -> None:
    entrada = Path(args.entrada)
    saida = Path(args.saida) if args.saida else entrada.with_name(f"{entrada.stem}_1080p{'.mov' if args.prores else '.mp4'}")
    vf = f"scale={args.width}:{args.height}:flags=lanczos,setsar=1"
    if args.prores:
        vcodec = ["-c:v", "prores_videotoolbox", "-profile:v", "2", "-pix_fmt", "yuv422p10le"]
        acodec = ["-c:a", "pcm_s16le"]
    else:
        vcodec = ["-c:v", "h264_videotoolbox", "-q:v", str(args.qualidade), "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
        acodec = ["-c:a", "aac", "-b:a", "192k"]
    cmd = [FFMPEG, "-v", "error", "-y", "-hwaccel", "videotoolbox", "-i", str(entrada), "-vf", vf] + vcodec + acodec + [str(saida)]
    subprocess.run(cmd, check=True)
    print(f"[m5-upscale-video] OK -> {saida}")


def cmd_transcrever(args: argparse.Namespace) -> None:
    entrada = Path(args.arquivo)
    nivel = lufs_audio(entrada)
    if nivel <= -50.0:
        res = {"arquivo": entrada.name, "lufs": nivel, "mudo": True, "texto": ""}
        print(json.dumps(res, ensure_ascii=False))
        return
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "audio16k.wav"
        subprocess.run(
            [FFMPEG, "-v", "error", "-y", "-i", str(entrada), "-vn", "-ac", "1", "-ar", "16000", str(wav)],
            check=True,
        )
        out_base = Path(tmp) / "transcricao"
        cmd = [
            str(LTX_BIN / "mlx_audio.stt.generate"),
            "--model",
            args.model,
            "--audio",
            str(wav),
            "--output-path",
            str(out_base),
            "--format",
            "txt",
            "--language",
            args.idioma,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        txt_file = out_base.with_suffix(".txt")
        texto = txt_file.read_text(encoding="utf-8").strip() if txt_file.exists() else r.stdout.strip()
        if any(h in texto.lower() for h in ALUCINACOES_WHISPER):
            texto = ""
        res = {"arquivo": entrada.name, "lufs": nivel, "mudo": False, "texto": texto}
        print(json.dumps(res, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Mostra status dos binários MLX/VideoToolbox e RAM do Ollama")
    sub.add_parser("liberar-ram", help="Descarrega modelos ativos do Ollama da memória unificada")

    p_vid = sub.add_parser("video", help="Gera vídeo local com LTX-2 em MLX Metal")
    p_vid.add_argument("--prompt", "-p", required=True)
    p_vid.add_argument("--image", "-i", type=Path, help="Imagem inicial para I2V")
    p_vid.add_argument("--image-strength", type=float, default=0.95)
    p_vid.add_argument("--width", "-W", type=int, default=768)
    p_vid.add_argument("--height", "-H", type=int, default=512)
    p_vid.add_argument("--frames", "-n", type=int, default=97, help="Quadros (8n+1, ex.: 97 = ~4s a 24fps, 193 = ~8s)")
    p_vid.add_argument("--fps", type=int, default=24)
    p_vid.add_argument("--seed", "-s", type=int, default=42)
    p_vid.add_argument("--tiling", default="auto", choices=["auto", "none", "default", "aggressive", "conservative", "spatial", "temporal"])
    p_vid.add_argument("--com-audio", action="store_true", help="Usa mlx_video.generate_av para áudio sincronizado")
    p_vid.add_argument("--enhance-prompt", action="store_true")
    p_vid.add_argument("--model-repo", default=None)
    p_vid.add_argument("-o", "--saida", type=Path, default=Path("saida_ltx2.mp4"))

    p_img = sub.add_parser("imagem", help="Gera imagem local com Z-Image-Turbo em MLX Metal")
    p_img.add_argument("--prompt", "-p", required=True)
    p_img.add_argument("--width", "-W", type=int, default=1280)
    p_img.add_argument("--height", "-H", type=int, default=720)
    p_img.add_argument("--steps", type=int, default=8)
    p_img.add_argument("--seed", "-s", type=int, default=42)
    p_img.add_argument("-o", "--saida", type=Path, default=Path("saida_zimage.png"))

    p_upi = sub.add_parser("upscale-img", help="Super-resolução de imagem local via SeedVR2 em MLX")
    p_upi.add_argument("entrada", type=Path)
    p_upi.add_argument("-o", "--saida", type=Path, default=Path("saida_upscale.png"))
    p_upi.add_argument("--resolution", "-r", default="2x")
    p_upi.add_argument("--softness", type=float, default=0.0)
    p_upi.add_argument("--quantize", "-q", type=int, choices=[3, 4, 5, 6, 8], default=8)

    p_upv = sub.add_parser("upscale-video", help="Upscale rápido de vídeo via Lanczos + VideoToolbox")
    p_upv.add_argument("entrada", type=Path)
    p_upv.add_argument("-o", "--saida", type=Path)
    p_upv.add_argument("--width", type=int, default=1920)
    p_upv.add_argument("--height", type=int, default=1080)
    p_upv.add_argument("--qualidade", type=int, default=78, help="Qualidade h264_videotoolbox (1..100)")
    p_upv.add_argument("--prores", action="store_true", help="Saída em ProRes 422 via prores_videotoolbox")

    p_stt = sub.add_parser("transcrever", help="Conferência rápida de fala em GPU Metal via mlx_audio.stt")
    p_stt.add_argument("arquivo", type=Path)
    p_stt.add_argument("--idioma", default="pt")
    p_stt.add_argument("--model", default="mlx-community/whisper-large-v3-turbo")

    args = ap.parse_args()
    if args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "liberar-ram":
        liberar_ollama()
    elif args.cmd == "video":
        cmd_video(args)
    elif args.cmd == "imagem":
        cmd_imagem(args)
    elif args.cmd == "upscale-img":
        cmd_upscale_img(args)
    elif args.cmd == "upscale-video":
        cmd_upscale_video(args)
    elif args.cmd == "transcrever":
        cmd_transcrever(args)


if __name__ == "__main__":
    main()
