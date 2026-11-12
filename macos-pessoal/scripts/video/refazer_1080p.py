#!/usr/bin/env python3
"""Refaz em 1080p um episódio já montado em 720p, sem refazer a mistura de áudio.

Ideia: o final em 720p é a referência de tempo. Cada clipe baixado do Flow em "1080p aprimorada" é localizado
dentro do final por comparação de quadros (miniaturas em cinza); a imagem do trecho é trocada pela do clipe em
1080p, esticada para ocupar exatamente os mesmos quadros. O que não tiver clipe em 1080p (abertura, cartão de
título, trechos sem correspondência) é ampliado do próprio final (lanczos). O áudio é copiado do final, sem recodificar.

Uso: refazer_1080p.py FINAL_720p.mp4 PASTA_COM_CLIPES_1080p SAIDA.mp4 [--ini 35] [--fim 30]
  --ini / --fim: segundos no começo e no fim que não são corpo (abertura + cartão; abertura final).
  --abertura / --cartao: abertura já remontada em 1080p e imagem do cartão, no lugar da ampliação desses trechos.
Rodar com o Python do venv (precisa de numpy)."""
import sys, os, subprocess, glob, json, argparse
import numpy as np

W, H = 48, 27


def mini(f, extra=()):
    """quadros do vídeo como array (n, H*W) em cinza, 24 fps"""
    cmd = ["ffmpeg", "-v", "error", *extra, "-i", f, "-vf", f"fps=24,scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-"]
    b = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(b, np.uint8).reshape(-1, H * W).astype(np.float32)


def melhor(corpo, q):
    d = ((corpo - q) ** 2).mean(axis=1)
    i = int(d.argmin())
    return i, float(d[i])


def sh(c):
    subprocess.run(c, check=True)


ap = argparse.ArgumentParser()
ap.add_argument("final"); ap.add_argument("pasta"); ap.add_argument("saida")
ap.add_argument("--ini", type=float, default=35.0); ap.add_argument("--fim", type=float, default=30.0)
ap.add_argument("--lim", type=float, default=60.0, help="erro quadrático médio máximo para aceitar um casamento")
ap.add_argument("--so-plano", action="store_true")
ap.add_argument("--abertura", help="abertura de 30 s já em 1080p: usada no começo (fade-out 0,5 s) e no fim (fade-in 0,5 s)")
ap.add_argument("--cartao", help="imagem do cartão de título: ocupa do fim da abertura até --ini (fades de 0,8 s)")
a = ap.parse_args()
a.final, a.pasta, a.saida = (os.path.abspath(x) for x in (a.final, a.pasta, a.saida))

tmp = os.path.splitext(a.saida)[0] + "_tmp"
os.makedirs(tmp, exist_ok=True)
F = mini(a.final)
N = len(F)
i0, i1 = round(a.ini * 24), N - round(a.fim * 24)
corpo = F[i0:i1]
print(f"final: {N} quadros; corpo {i0}..{i1} ({len(corpo)} quadros)")

# 1. localizar cada clipe 1080p dentro do corpo
achados = []
for f in sorted(glob.glob(a.pasta + "/*.mp4")):
    c = mini(f)
    n = len(c)
    if n < 60:
        continue
    ka, kb = 12, n - 20
    pa, ea = melhor(corpo, c[ka]); pb, eb = melhor(corpo, c[kb])
    if ea > a.lim or eb > a.lim or pb <= pa:
        continue
    taxa = (pb - pa) / (kb - ka)                 # quadros do final por quadro do clipe
    if not 0.9 < taxa < 1.35:
        continue
    ini = pa - ka * taxa
    # conferência no meio
    km = n // 2
    em = float(((corpo[min(len(corpo) - 1, max(0, round(ini + km * taxa)))] - c[km]) ** 2).mean())
    if em > a.lim * 1.5:
        continue
    achados.append(dict(f=f, n=n, ini=ini, taxa=taxa, erro=max(ea, eb, em)))
achados.sort(key=lambda x: x["ini"])

# 2. resolver sobreposições (mesmo trecho casado por dois arquivos: fica o de menor erro) e fechar os segmentos
segs = []
for x in achados:
    s = max(0, round(x["ini"])); e = min(len(corpo), round(x["ini"] + (x["n"] + 2) * x["taxa"]))  # +2: o 1080p vem sem os 2 últimos quadros
    if segs and s < segs[-1]["e"] - 12:           # sobrepõe o anterior em mais de meio segundo
        if x["erro"] < segs[-1]["erro"] and abs(s - segs[-1]["s"]) < 24:
            segs[-1] = dict(x, s=segs[-1]["s"], e=e)
        elif abs(s - segs[-1]["s"]) < 24:
            pass
        else:
            segs[-1]["e"] = s; segs.append(dict(x, s=s, e=e))
        continue
    segs.append(dict(x, s=s, e=e))
for k in range(len(segs) - 1):                    # encostar um no outro quando a folga é pequena
    g = segs[k + 1]["s"] - segs[k]["e"]
    if -12 <= g <= 6:
        segs[k]["e"] = segs[k + 1]["s"]
if segs:                                          # sobra de até 3 quadros nas pontas: o clipe vizinho cobre (pedaço de 1 quadro quebra a emenda)
    if 0 < segs[0]["s"] <= 3: segs[0]["s"] = 0
    if 0 < len(corpo) - segs[-1]["e"] <= 3: segs[-1]["e"] = len(corpo)
plano = []                                        # lista final: ("clipe", seg) ou ("final", s, e) em quadros do corpo
pos = 0
for s in segs:
    if s["s"] > pos:
        plano.append(("final", pos, s["s"]))
    plano.append(("clipe", s)); pos = s["e"]
if pos < len(corpo):
    plano.append(("final", pos, len(corpo)))
cob = sum(p[1]["e"] - p[1]["s"] for p in plano if p[0] == "clipe")
print(f"clipes casados: {len(segs)}; cobertura do corpo: {100 * cob / len(corpo):.1f}%")
for p in plano:
    if p[0] == "final":
        print(f"  SEM 1080p: {(i0 + p[1]) / 24:7.2f}s a {(i0 + p[2]) / 24:7.2f}s ({p[2] - p[1]} quadros)")
json.dump([p if p[0] == "final" else ["clipe", {k: (v if not isinstance(v, np.floating) else float(v)) for k, v in p[1].items()}] for p in plano],
          open(tmp + "/plano.json", "w"), indent=1)
if a.so_plano:
    sys.exit(0)

# 3. renderizar os pedaços em 1080p, com o número exato de quadros
ENC = ["-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "24", "-an"]


def do_final(s, e, out, fades=""):                # s, e em quadros absolutos do final
    sh(["ffmpeg", "-v", "error", "-y", "-i", a.final, "-vf",
        f"fps=24,trim=start_frame={s}:end_frame={e},setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos,setsar=1{fades}", *ENC, out])


partes = []
SC = "scale=1920:1080:flags=lanczos,setsar=1"
if a.abertura:
    a.abertura = os.path.abspath(a.abertura)
    sh(["ffmpeg", "-v", "error", "-y", "-i", a.abertura, "-vf", f"fps=24,{SC},trim=end_frame=720,setpts=PTS-STARTPTS,fade=t=out:st=29.5:d=0.5", *ENC, tmp + "/p_ab1.mp4"])
    partes.append(tmp + "/p_ab1.mp4")
    if i0 > 720:
        c = (i0 - 720) / 24
        if a.cartao:
            sh(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "24", "-t", f"{c:.3f}", "-i", os.path.abspath(a.cartao), "-vf",
                f"{SC},format=yuv420p,fade=t=in:st=0:d=0.8,fade=t=out:st={c - 0.8:.2f}:d=0.8", "-frames:v", str(i0 - 720), *ENC, tmp + "/p_cartao.mp4"])
        else:
            do_final(720, i0, tmp + "/p_cartao.mp4")
        partes.append(tmp + "/p_cartao.mp4")
else:
    do_final(0, i0, tmp + "/p_ini.mp4"); partes.append(tmp + "/p_ini.mp4")
D = len(corpo)
for k, p in enumerate(plano):
    out = f"{tmp}/c{k:03d}.mp4"
    if p[0] == "final":
        do_final(i0 + p[1], i0 + p[2], out)
    else:
        s = p[1]; L = s["e"] - s["s"]
        desl = (s["s"] - s["ini"]) / s["taxa"]     # quadros do clipe a pular (quando o trecho começa depois do início do clipe)
        vf = (f"fps=24,trim=start_frame={max(0, round(desl))},setpts=(PTS-STARTPTS)*{s['taxa']:.6f},fps=24,scale=1920:1080:flags=lanczos,setsar=1,"
              f"tpad=stop_mode=clone:stop_duration=2,trim=end_frame={L},setpts=PTS-STARTPTS")
        # fades do corpo (0,5 s na entrada e na saída), como na montagem em 720p
        if s["s"] < 12:
            vf += f",fade=t=in:st=0:d={(12 - s['s']) / 24:.3f}"
        if s["e"] > D - 12:
            vf += f",fade=t=out:st={(D - 12 - s['s']) / 24:.3f}:d=0.5"
        sh(["ffmpeg", "-v", "error", "-y", "-i", s["f"], "-vf", vf, *ENC, out])
    partes.append(out)
if a.abertura and N - i1 == 720:
    sh(["ffmpeg", "-v", "error", "-y", "-i", a.abertura, "-vf", f"fps=24,{SC},trim=end_frame=720,setpts=PTS-STARTPTS,fade=t=in:d=0.5", *ENC, tmp + "/p_fim.mp4"])
else:
    do_final(i1, N, tmp + "/p_fim.mp4")
partes.append(tmp + "/p_fim.mp4")
with open(tmp + "/lista.txt", "w") as f:
    for p in partes:
        f.write(f"file '{p}'\n")
sh(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", tmp + "/lista.txt", "-c", "copy", tmp + "/video.mp4"])
sh(["ffmpeg", "-v", "error", "-y", "-i", tmp + "/video.mp4", "-i", a.final, "-map", "0:v", "-map", "1:a", "-c", "copy", "-movflags", "+faststart", a.saida])

# 4. conferência: o resultado, reduzido, tem de bater quadro a quadro com o final em 720p
R = mini(a.saida)
n = min(len(R), N)
d = ((R[:n] - F[:n]) ** 2).mean(axis=1)
ruins = np.where(d > 150)[0]
print(f"saída: {len(R)} quadros (final: {N}); erro médio {d.mean():.1f}; quadros com erro alto: {len(ruins)}")
if len(ruins):
    blocos = np.split(ruins, np.where(np.diff(ruins) > 12)[0] + 1)
    for b in blocos[:20]:
        print(f"  conferir {b[0] / 24:.2f}s a {b[-1] / 24:.2f}s")
