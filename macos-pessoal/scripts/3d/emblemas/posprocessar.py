from pathlib import Path as _NolaPath
import sys as _nola_sys
_nola_sys.path.insert(0, str(_NolaPath(__file__).resolve().parents[2]))
from nola_paths import media_root, configure_device, asset_id
"""Gera as entregas de video de uma projeto pessoal a partir dos quadros RGBA (renders/_trabalho/SIG/q e /v).
   uso: python scripts/posprocessar.py SIGLA
   Horizontal 1920x1080 = quadro quadrado 1080 centralizado; vertical = quadro 1080x1920 renderizado com camera propria.
   Com degrade: composto sobre o fundo do padrao nola-macm5 (renderizado do proprio mundo do mestre, com dithering).
   Transparente: ProRes 4444 + WebM VP9 alfa + sequencia PNG RGBA; mais uma previa H.264 (alfa sobre cinza)."""
import sys, os, subprocess, shutil, glob
import numpy as np, cv2
sig = asset_id(sys.argv[1]); s = sig.lower(); tipo = os.environ.get("TIPO", "emblema"); RD = "renders-esfera" if tipo == "esfera" else "renders"
R = str(media_root())
T = os.path.join(R, RD, "_trabalho"); Q = os.path.join(T, sig, "q"); V = os.path.join(T, sig, "v")
O = os.path.join(R, RD, sig); TR = os.path.join(O, "transparente")
for d in (O, TR): os.makedirs(d, exist_ok=True)
FF = ["ffmpeg", "-y", "-v", "error"]


def run(*a): subprocess.run(list(a), check=True)


def fundo(nome):   # 16 bits -> 8 bits com dithering triangular (evita faixas no degrade)
    dst = os.path.join(T, "fundos", nome + "-8b.png")
    if not os.path.exists(dst):
        i = cv2.imread(os.path.join(T, "fundos", nome + ".png"), -1).astype(np.float32) / 257.0
        rng = np.random.default_rng(7)
        n = rng.random(i.shape[:2], np.float32) - rng.random(i.shape[:2], np.float32)
        cv2.imwrite(dst, np.clip(np.rint(i + n[..., None] * 0.9), 0, 255).astype(np.uint8))
    return dst


bgh, bgv = fundo("fundo-horizontal"), fundo("fundo-vertical")
nq = len(glob.glob(Q + "/q_*.png")); nv = len(glob.glob(V + "/v_*.png"))
assert nq == 144 and nv == 144, (nq, nv)
qin = ["-framerate", "24", "-i", Q + "/q_%04d.png"]; vin = ["-framerate", "24", "-i", V + "/v_%04d.png"]
H264 = ["-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-r", "24", "-frames:v", "144"]

# ---- com degrade
hor = os.path.join(O, f"{tipo}-{s}-giro-horizontal-1920x1080.mp4")
run(*FF, "-loop", "1", "-i", bgh, *qin, "-filter_complex", "[0:v][1:v]overlay=(W-w)/2:0:shortest=1:format=auto,format=yuv420p", *H264, hor)
ver = os.path.join(O, f"{tipo}-{s}-giro-vertical-1080x1920.mp4")
run(*FF, "-loop", "1", "-i", bgv, *vin, "-filter_complex", "[0:v][1:v]overlay=0:0:shortest=1:format=auto,format=yuv420p", *H264, ver)
# GIF e MP4 leve (quadrado central, para WhatsApp)
sq = "crop=1080:1080:420:0"
gif = os.path.join(O, f"{tipo}-{s}-giro.gif")
run(*FF, "-i", hor, "-vf", f"{sq},fps=15,scale=480:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a", "-loop", "0", gif)
run(*FF, "-i", hor, "-vf", f"{sq},scale=720:-1:flags=lanczos", "-c:v", "libx264", "-crf", "24", "-preset", "slow", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart",
    os.path.join(O, f"{tipo}-{s}-giro-whatsapp.mp4"))

# ---- transparente
hp = os.path.join(TR, "horizontal-png"); vp = os.path.join(TR, "vertical-png")
for d in (hp, vp): os.makedirs(d, exist_ok=True)
run(*FF, *qin, "-vf", "format=rgba,pad=1920:1080:(ow-iw)/2:0:color=black@0", "-start_number", "1", os.path.join(hp, "a_%04d.png"))
for f in glob.glob(V + "/v_*.png"): shutil.copy(f, os.path.join(vp, "a_" + os.path.basename(f)[2:]))
pr = ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-r", "24"]
vp9 = ["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "30", "-auto-alt-ref", "0", "-r", "24"]
for nome, pasta in (("horizontal", hp), ("vertical", vp)):
    inp = ["-framerate", "24", "-i", pasta + "/a_%04d.png"]
    run(*FF, *inp, *pr, os.path.join(TR, f"{tipo}-{s}-giro-{nome}-alpha.mov"))
    run(*FF, *inp, *vp9, os.path.join(TR, f"{tipo}-{s}-giro-{nome}-alpha.webm"))
    run(*FF, *inp, "-f", "lavfi", "-i", "color=c=0x303030:s=%s:r=24" % ("1920x1080" if nome == "horizontal" else "1080x1920"),
        "-filter_complex", "[1:v][0:v]overlay=0:0:shortest=1:format=auto,format=yuv420p", *H264[:-2],
        os.path.join(TR, f"{tipo}-{s}-giro-{nome}-alpha-previa.mp4"))
print("OK", sig)
