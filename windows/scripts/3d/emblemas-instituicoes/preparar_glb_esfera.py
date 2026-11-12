"""Texturas para o GLB da esfera: metal/rugosidade empacotados (G=rugosidade, B=metal) da frente e cor 'achatada' da costa INSTITUICAO
   (campo preto liso, so o prata usa a textura). python preparar_glb_esfera.py SIGLA"""
import sys, os
import numpy as np, cv2
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fontes"); sig = sys.argv[1]
e = cv2.imread(os.path.join(F, sig + "-esf-esmalte.png"), 0).astype(np.float32) / 255
mr = np.ones(e.shape + (3,), np.float32)          # BGR: B=1 (oclusao), G=rugosidade, R=metal -> em BGR: [0]=B(oclusao) [1]=G [2]=R(metal)
mr[..., 1] = 0.30; mr[..., 2] = 0.85 - 0.73 * e   # cv2 grava BGR: canal R do arquivo = metal; precisamos de B=metal => trocar
out = np.stack([0.85 - 0.73 * e, 0.30 + 0 * e, np.ones_like(e)], 2)    # BGR: B=metal, G=rugosidade, R=1
cv2.imwrite(os.path.join(F, sig + "-esf-glb-mr.png"), (out * 255).astype(np.uint8))
dst = os.path.join(F, "INSTITUICAO-glb-cor.png")
if not os.path.exists(dst):
    c = cv2.imread(os.path.join(F, "INSTITUICAO-cor.png")).astype(np.float32) / 255
    lum = c.mean(2); m = np.clip((lum - 0.35) / (0.52 - 0.35), 0, 1)[..., None]
    cv2.imwrite(dst, (np.clip(c * m + 0.09 * (1 - m), 0, 1) * 255).astype(np.uint8))
print("ok", sig)
