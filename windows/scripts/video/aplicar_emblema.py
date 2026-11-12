"""Cola o emblema original no peito do personagem, seguindo o movimento do torso.

O emblema nunca vai para a IA (ela o redesenha); o vídeo vem do Flow com o peito liso e o
emblema entra aqui, por rastreio de um trecho texturizado da camisa (gola + aba do bolso).

uso: python aplicar_emblema.py entrada.mp4 saida.mp4 --centro X Y --diam D --modelo X0 Y0 X1 Y1
  --centro  centro do emblema no 1º quadro (px)
  --diam    diâmetro do emblema (px)
  --modelo  caixa do trecho rastreado no 1º quadro (deve conter a gola/aba do bolso, não a mão)
"""
import argparse, subprocess, sys
import cv2, numpy as np

EMBLEMA = r"..\emblemas_metalizados\emblema-coruja-3d-unidade-mg.png"


def emblema_rgba(diam, brilho):
    img = cv2.imread(EMBLEMA, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    cv2.circle(mask, (w // 2, h // 2), int(min(w, h) * 0.495), 255, -1, cv2.LINE_AA)
    img = cv2.resize(img, (diam, diam), interpolation=cv2.INTER_AREA)
    mask = cv2.resize(mask, (diam, diam), interpolation=cv2.INTER_AREA)
    img = cv2.GaussianBlur(img, (0, 0), 0.6)  # casa com a maciez do vídeo 720p
    return (img.astype(np.float32) * brilho), mask.astype(np.float32) / 255


def colar(frame, emb, alfa, cx, cy):
    d = emb.shape[0]
    x0, y0 = int(round(cx - d / 2)), int(round(cy - d / 2))
    fh, fw = frame.shape[:2]
    ax0, ay0, ax1, ay1 = max(x0, 0), max(y0, 0), min(x0 + d, fw), min(y0 + d, fh)
    if ax0 >= ax1 or ay0 >= ay1:
        return
    e = emb[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0]
    a = alfa[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0, None]
    roi = frame[ay0:ay1, ax0:ax1].astype(np.float32)
    frame[ay0:ay1, ax0:ax1] = np.clip(roi * (1 - a) + e * a, 0, 255).astype(np.uint8)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("entrada"); p.add_argument("saida")
    p.add_argument("--centro", nargs=2, type=float, required=True)
    p.add_argument("--diam", type=int, required=True)
    p.add_argument("--modelo", nargs=4, type=int, required=True)
    p.add_argument("--brilho", type=float, default=0.85)
    p.add_argument("--busca", type=int, default=60, help="raio de busca do rastreio (px)")
    p.add_argument("--suave", type=float, default=0.5, help="0 = sem suavização, 0.9 = muito suave")
    p.add_argument("--ref", help="vídeo já medido: --centro/--diam/--modelo valem para ele e são "
                                 "transferidos para a entrada por busca em várias escalas")
    a = p.parse_args()

    cap = cv2.VideoCapture(a.entrada)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    clahe = cv2.createCLAHE(3.0, (8, 8))
    prep = lambda f: clahe.apply(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))

    ok, f0 = cap.read()
    if a.ref:
        _, r0 = cv2.VideoCapture(a.ref).read()
        rx0, ry0, rx1, ry1 = a.modelo
        rt = prep(r0)[ry0:ry1, rx0:rx1]
        g0, best = prep(f0), (-1, 0, 0, 1)
        for s in np.arange(0.6, 1.61, 0.05):  # ponytail: busca exaustiva em escala; basta p/ 1 quadro
            t = cv2.resize(rt, None, fx=s, fy=s)
            if t.shape[0] >= h or t.shape[1] >= w:
                continue
            _, sc, _, lc = cv2.minMaxLoc(cv2.matchTemplate(g0, t, cv2.TM_CCOEFF_NORMED))
            if sc > best[0]:
                best = (sc, lc[0], lc[1], s)
        sc, nx, ny, s = best
        a.centro = [nx + (a.centro[0] - rx0) * s, ny + (a.centro[1] - ry0) * s]
        a.diam = max(8, round(a.diam * s))
        a.modelo = [nx, ny, nx + round((rx1 - rx0) * s), ny + round((ry1 - ry0) * s)]
        print(f"ref: escala={s:.2f} correlacao={sc:.2f} centro={a.centro[0]:.0f},{a.centro[1]:.0f} diam={a.diam}")
    x0, y0, x1, y1 = a.modelo
    tpl = prep(f0)[y0:y1, x0:x1]
    off = (a.centro[0] - x0, a.centro[1] - y0)
    emb, alfa = emblema_rgba(a.diam, a.brilho)

    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                           "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-i", a.entrada,
                           "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "16",
                           "-pix_fmt", "yuv420p", "-c:a", "copy", a.saida], stdin=subprocess.PIPE)
    px, py, piores = float(x0), float(y0), []
    frame = f0
    while ok:
        g = prep(frame)
        sx0, sy0 = max(int(px) - a.busca, 0), max(int(py) - a.busca, 0)
        sx1, sy1 = min(int(px) + tpl.shape[1] + a.busca, w), min(int(py) + tpl.shape[0] + a.busca, h)
        r = cv2.matchTemplate(g[sy0:sy1, sx0:sx1], tpl, cv2.TM_CCOEFF_NORMED)
        _, score, _, loc = cv2.minMaxLoc(r)
        piores.append(score)
        nx, ny = sx0 + loc[0], sy0 + loc[1]
        px, py = a.suave * px + (1 - a.suave) * nx, a.suave * py + (1 - a.suave) * ny
        colar(frame, emb, alfa, px + off[0], py + off[1])
        ff.stdin.write(frame.tobytes())
        ok, frame = cap.read()
    ff.stdin.close(); ff.wait()
    s = np.array(piores)
    print(f"quadros={len(s)} correlacao min={s.min():.2f} media={s.mean():.2f}  (abaixo de ~0.5 = rastreio duvidoso)")


if __name__ == "__main__":
    sys.exit(main())
