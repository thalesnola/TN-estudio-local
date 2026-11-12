from pathlib import Path as _NolaPath
import sys as _nola_sys
_nola_sys.path.insert(0, str(_NolaPath(__file__).resolve().parents[2]))
from nola_paths import media_root, configure_device, asset_id
"""Insumos da ESFERA de uma projeto pessoal: o escudo (ja preparado por preparar.py) e colado, centralizado, numa tela QUADRADA
   cujo circulo inscrito cobre o hemisferio da frente (projecao azimutal equidistante: raio na esfera = angulo/90 graus).
   Fora do escudo a tela e metal na cor da moldura. Usar DEPOIS de preparar.py.   python preparar_esfera.py SIGLA"""
import sys, os, json
import numpy as np, cv2
sig = asset_id(sys.argv[1]); F = str(media_root()/"fontes")
J = json.load(open(os.path.join(F, sig + "-contorno.json")))
cor = cv2.imread(os.path.join(F, sig + "-cor.png")); H, W = cor.shape[:2]
m = cv2.imread(os.path.join(F, sig + "-mascara.png"), 0)
h = cv2.imread(os.path.join(F, sig + "-altura16.png"), -1).astype(np.float32)
e = cv2.imread(os.path.join(F, sig + "-esmalte.png"), 0).astype(np.float32)
esc = J["esc"]
R = max(np.hypot(x, y) for x, y in J["poly"]) * 1.04          # raio (m) do circulo que contem o escudo inteiro
S = max(int(np.ceil(2 * R / esc)), W, H); S += S % 2
# A tela precisa comportar também o padding da imagem recortada.
R = S * esc / 2
rim = (np.array(J["rim_rgb"][::-1]) * 255).astype(np.float32)   # BGR
# degrade suave na moldura (evita tela chapada): levemente mais escuro nas bordas
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32); rr = np.hypot(xx - S / 2, yy - S / 2) / (S / 2)
tela = np.empty((S, S, 3), np.float32); tela[:] = rim
tela *= (1.04 - 0.14 * rr ** 2)[..., None]
x0 = (S - W) // 2; y0 = (S - H) // 2
a = cv2.GaussianBlur(cv2.erode(m, np.ones((3, 3), np.uint8)).astype(np.float32) / 255, (0, 0), 1.2)
a = np.zeros((S, S), np.float32); a[y0:y0 + H, x0:x0 + W] = cv2.GaussianBlur(cv2.erode(m, np.ones((3, 3), np.uint8)).astype(np.float32) / 255, (0, 0), 1.2)
paste = np.zeros((S, S, 3), np.float32); paste[y0:y0 + H, x0:x0 + W] = cor
out = paste * a[..., None] + tela * (1 - a[..., None])
cv2.imwrite(os.path.join(F, sig + "-esf-cor.png"), np.clip(out, 0, 255).astype(np.uint8))
hp = np.zeros((S, S), np.float32); hp[y0:y0 + H, x0:x0 + W] = h
cv2.imwrite(os.path.join(F, sig + "-esf-altura16.png"), hp.astype(np.uint16))
ep = np.zeros((S, S), np.float32); ep[y0:y0 + H, x0:x0 + W] = e
cv2.imwrite(os.path.join(F, sig + "-esf-esmalte.png"), ep.astype(np.uint8))
print(sig, "tela", S, "raio m %.3f" % R, "escudo ocupa %.0f%% da largura do hemisferio" % (100 * J["largura_m"] / (2 * R)))
