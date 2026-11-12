"""Tria o que chegou em 00-entrada/ e manda cada arquivo para a subpasta certa.

    python3 ferramentas/scripts/triar.py                 (só mostra o que faria)
    python3 ferramentas/scripts/triar.py --mover         (move de verdade)
    python3 ferramentas/scripts/triar.py --de ~/Downloads --so "EP0*"   (triar outra pasta, só o que casar)

Nunca apaga e nunca sobrescreve: se o destino já existe, pula e avisa.
Vídeo abaixo de 1080p é sinalizado (o padrão do estúdio é 1080p).
Só biblioteca padrão; usa ffprobe (se houver) para duração e resolução.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import re
import shutil
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ENTRADA = RAIZ / "00-entrada"
VIDEO = {".mp4", ".mov", ".m4v", ".webm"}
IMAGEM = {".png", ".jpg", ".jpeg", ".webp", ".heic", ".gif"}
TEXTO = {".md", ".txt"}
# nomes típicos de câmera/celular: foto ou vídeo real da família (fica só local, nunca sobe ao Flow)
REAL = re.compile(r"^(IMG_\d+|PXL_|\d{8}_\d{6}|\d{2}\d{2}\d{4}_\d{6})", re.I)


def sonda(p: Path) -> tuple[float | None, int | None]:
    if not shutil.which("ffprobe") or p.suffix.lower() not in VIDEO:
        return None, None
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=height:format=duration", "-of", "json", str(p)],
            capture_output=True, text=True, timeout=30)
        j = json.loads(r.stdout or "{}")
        dur = float(j.get("format", {}).get("duration") or 0) or None
        alt = (j.get("streams") or [{}])[0].get("height")
        return dur, alt
    except Exception:  # noqa: BLE001 — triagem nunca quebra por causa de uma sonda
        return None, None


def destino(p: Path) -> str:
    ext = p.suffix.lower()
    if REAL.match(p.name) or ext == ".heic":
        return "fotos-videos"
    if ext in VIDEO:
        return "clipes-flow"
    if ext in IMAGEM:
        return "imagens-flow"
    if ext in TEXTO:
        return "ideias"
    return "outros"


def episodio(nome: str) -> str | None:
    m = re.search(r"ep0?(\d)", nome, re.I)
    return f"ep0{m.group(1)}" if m else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--de", default=str(ENTRADA), help="pasta a triar (padrão: 00-entrada)")
    ap.add_argument("--so", default="*", help="só arquivos que casem com este padrão")
    ap.add_argument("--mover", action="store_true", help="move de verdade (sem isto, só mostra)")
    a = ap.parse_args()

    origem = Path(a.de).expanduser()
    if not origem.is_dir():
        print(f"Pasta não existe: {origem}")
        return 1
    itens = sorted(p for p in origem.iterdir()
                   if p.is_file() and not p.name.startswith((".", "_")) and fnmatch.fnmatch(p.name, a.so))
    if not itens:
        print("Nada novo para triar.")
        return 0

    log: list[str] = []
    for p in itens:
        sub = destino(p)
        dur, alt = sonda(p)
        notas = []
        if dur:
            notas.append(f"{dur:.1f}s")
        if alt:
            notas.append(f"{alt}p")
            if alt < 1080 and sub == "clipes-flow":
                notas.append("ABAIXO DE 1080p: baixar de novo em '1080p Aprimorada'")
        if sub == "fotos-videos":
            notas.append("real: fica só local, não sobe ao Flow nem a serviço externo")
        ep = episodio(p.name)
        if ep and sub in ("clipes-flow", "imagens-flow"):
            notas.append(f"sugestão: episodios/{ep}/")
        alvo = ENTRADA / sub / p.name
        estado = ""
        if a.mover:
            if alvo.exists():
                estado = " [PULADO: já existe no destino]"
            else:
                alvo.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(p), str(alvo))
                estado = " [movido]"
                log.append(f"- {dt.date.today()} · {p.name} → {sub}/")
        print(f"{p.name:55s} → {sub:13s} {'; '.join(notas)}{estado}")

    if a.mover and log:
        novo = not (ENTRADA / "_triagem.md").exists()
        with open(ENTRADA / "_triagem.md", "a", encoding="utf-8") as f:
            if novo:
                f.write("# Registro da triagem\n\n> Tipo: registro · Status: vigente\n\n")
            f.write("\n".join(log) + "\n")
    elif not a.mover:
        print("\n(simulação: nada foi movido; use --mover)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
