#!/usr/bin/env python3
"""Trata imagens em lote com o Pixelmator Pro (AppleScript). Nunca altera o original.

Uso:
  python3 pixelmator_lote.py --op superres --saida DIR img1.png img2.jpg ...
  python3 pixelmator_lote.py --op removefundo --saida DIR pranchas/3d/*.png

Operacoes (--op, pode repetir; rodam na ordem dada):
  superres     super resolution (3x)
  removefundo  remove background
  denoise      denoise
  enhance      enhance
Saida: DIR/<nome>.png (PNG). Imagem nao sobe a servico externo: tudo local.
"""
import argparse, subprocess, sys
from pathlib import Path

CMD = {"superres": "super resolution d", "removefundo": "remove background d",
       "denoise": "denoise d", "enhance": "enhance d"}


def tratar(src: Path, dst: Path, ops: list[str]) -> str:
    corpo = "\n".join("      " + CMD[o] for o in ops)
    script = f'''
tell application "Pixelmator Pro"
  open POSIX file "{src}"
  set d to front document
  try
{corpo}
    export d to POSIX file "{dst}" as PNG
    set r to (width of d as string)
  on error m
    set r to "ERRO: " & m
  end try
  close d without saving
  return r
end tell'''
    p = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=300)
    return (p.stdout.strip() or p.stderr.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--op", action="append", required=True, choices=CMD)
    ap.add_argument("--saida", required=True)
    ap.add_argument("imagens", nargs="+")
    a = ap.parse_args()
    out = Path(a.saida).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    falhas = 0
    for img in a.imagens:
        src = Path(img).expanduser().resolve()
        dst = out / (src.stem + ".png")
        if dst == src or dst.exists():
            print(f"PULA {src.name}: destino existe ou igual ao original"); continue
        r = tratar(src, dst, a.op)
        ok = dst.exists() and not r.startswith("ERRO")
        falhas += not ok
        print(("OK   " if ok else "FALHA"), src.name, "->", dst.name, r)
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
