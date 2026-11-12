#!/usr/bin/env python3
"""Composição local nola-macm5: rastreio de textura, sem redesenhar a arte fornecida."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
import cv2
import numpy as np


def emblema_rgba(path, diam, brilho):
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f'Não foi possível ler a arte: {path}')
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    h, w = img.shape[:2]
    if img.shape[2] == 4:
        mask = img[..., 3]
        img = img[..., :3]
    else:
        mask = np.zeros((h, w), np.uint8)
        cv2.circle(mask, (w//2, h//2), int(min(w, h)*0.495), 255, -1, cv2.LINE_AA)
    img = cv2.resize(img, (diam, diam), interpolation=cv2.INTER_AREA)
    mask = cv2.resize(mask, (diam, diam), interpolation=cv2.INTER_AREA)
    img = cv2.GaussianBlur(img, (0, 0), 0.6)
    return img.astype(np.float32)*brilho, mask.astype(np.float32)/255


def colar(frame, emb, alfa, cx, cy):
    size = emb.shape[0]
    x0, y0 = int(round(cx-size/2)), int(round(cy-size/2))
    height, width = frame.shape[:2]
    ax0, ay0, ax1, ay1 = max(x0, 0), max(y0, 0), min(x0+size, width), min(y0+size, height)
    if ax0 >= ax1 or ay0 >= ay1:
        return
    e = emb[ay0-y0:ay1-y0, ax0-x0:ax1-x0]
    a = alfa[ay0-y0:ay1-y0, ax0-x0:ax1-x0, None]
    roi = frame[ay0:ay1, ax0:ax1].astype(np.float32)
    frame[ay0:ay1, ax0:ax1] = np.clip(roi*(1-a)+e*a, 0, 255).astype(np.uint8)


def read_first(path):
    cap = cv2.VideoCapture(str(path))
    ok, frame = cap.read()
    if not cap.isOpened() or not ok:
        cap.release()
        raise ValueError(f'Vídeo vazio, inválido ou ausente: {path}')
    return cap, frame


def check_box(box, width, height):
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise ValueError('A caixa --modelo deve ficar dentro do vídeo e ter área positiva.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entrada', type=Path)
    parser.add_argument('saida', type=Path)
    parser.add_argument('--emblema', type=Path, required=True)
    parser.add_argument('--centro', nargs=2, type=float, required=True)
    parser.add_argument('--diam', type=int, required=True)
    parser.add_argument('--modelo', nargs=4, type=int, required=True)
    parser.add_argument('--brilho', type=float, default=0.85)
    parser.add_argument('--busca', type=int, default=60)
    parser.add_argument('--suave', type=float, default=0.5)
    parser.add_argument('--ref', type=Path)
    parser.add_argument('--sobrescrever', action='store_true')
    a = parser.parse_args(argv)
    for key in ('entrada', 'saida', 'emblema', 'ref'):
        if getattr(a, key) is not None:
            setattr(a, key, getattr(a, key).expanduser().resolve())
    if a.saida in (a.entrada, a.emblema, a.ref):
        parser.error('A saída deve ser diferente de todos os arquivos de entrada.')
    if a.saida.suffix.lower() not in ('.mp4', '.mov'):
        parser.error('A saída deve usar .mp4 ou .mov.')
    if a.saida.exists() and not a.sobrescrever:
        parser.error('A saída já existe; use --sobrescrever para substituí-la.')
    if a.diam < 1 or a.busca < 0 or not 0 <= a.suave < 1 or a.brilho < 0:
        parser.error('Exige diam > 0, busca >= 0, 0 <= suave < 1 e brilho >= 0.')
    if shutil.which('ffmpeg') is None:
        parser.error('ffmpeg não encontrado no PATH.')
    cap = None
    try:
        cap, first = read_first(a.entrada)
        h, w = first.shape[:2]
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not np.isfinite(fps) or fps <= 0 or w % 2 or h % 2:
            raise ValueError('H.264 yuv420p exige FPS válido e dimensões pares.')
        clahe = cv2.createCLAHE(3.0, (8, 8))
        def prep(frame):
            return clahe.apply(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        if a.ref:
            refcap, reference = read_first(a.ref)
            refcap.release()
            rh, rw = reference.shape[:2]
            check_box(a.modelo, rw, rh)
            rx0, ry0, rx1, ry1 = a.modelo
            rt = prep(reference)[ry0:ry1, rx0:rx1]
            g0, best = prep(first), (-1, 0, 0, 1)
            for scale in np.arange(0.6, 1.61, 0.05):
                template = cv2.resize(rt, None, fx=scale, fy=scale)
                if template.shape[0] >= h or template.shape[1] >= w:
                    continue
                _, score, _, loc = cv2.minMaxLoc(cv2.matchTemplate(g0, template, cv2.TM_CCOEFF_NORMED))
                if score > best[0]:
                    best = score, loc[0], loc[1], scale
            score, nx, ny, scale = best
            if score < 0:
                raise ValueError('Nenhuma escala da referência cabe no vídeo.')
            a.centro = [nx+(a.centro[0]-rx0)*scale, ny+(a.centro[1]-ry0)*scale]
            a.diam = max(8, round(a.diam*scale))
            a.modelo = [nx, ny, nx+round((rx1-rx0)*scale), ny+round((ry1-ry0)*scale)]
        check_box(a.modelo, w, h)
        x0, y0, x1, y1 = a.modelo
        template = prep(first)[y0:y1, x0:x1]
        offset = a.centro[0]-x0, a.centro[1]-y0
        emb, alpha = emblema_rgba(a.emblema, a.diam, a.brilho)
        a.saida.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='nola-macm5-', dir=a.saida.parent) as temp:
            output = Path(temp)/('video'+a.saida.suffix)
            with (Path(temp)/'ffmpeg.log').open('wb') as errorlog:
                ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                    '-s', f'{w}x{h}', '-r', str(fps), '-i', '-', '-i', str(a.entrada),
                    '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264', '-crf', '16',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', str(output)],
                    stdin=subprocess.PIPE, stderr=errorlog)
                try:
                    px, py, scores = float(x0), float(y0), []
                    ok, frame = True, first
                    while ok:
                        gray = prep(frame)
                        sx0, sy0 = max(int(px)-a.busca, 0), max(int(py)-a.busca, 0)
                        sx1, sy1 = min(int(px)+template.shape[1]+a.busca, w), min(int(py)+template.shape[0]+a.busca, h)
                        match = cv2.matchTemplate(gray[sy0:sy1, sx0:sx1], template, cv2.TM_CCOEFF_NORMED)
                        _, score, _, loc = cv2.minMaxLoc(match)
                        scores.append(score)
                        nx, ny = sx0+loc[0], sy0+loc[1]
                        px, py = a.suave*px+(1-a.suave)*nx, a.suave*py+(1-a.suave)*ny
                        colar(frame, emb, alpha, px+offset[0], py+offset[1])
                        ff.stdin.write(frame.tobytes())
                        ok, frame = cap.read()
                    ff.stdin.close()
                    if ff.wait() != 0:
                        raise ValueError('ffmpeg falhou: '+(Path(temp)/'ffmpeg.log').read_text(errors='replace')[-2000:])
                finally:
                    if ff.poll() is None:
                        ff.kill()
                        ff.wait()
                    if ff.stdin and not ff.stdin.closed:
                        ff.stdin.close()
            output.replace(a.saida)
        print(f'quadros={len(scores)} correlacao min={min(scores):.2f} media={np.mean(scores):.2f}')
        return 0
    except (ValueError, OSError, cv2.error) as error:
        parser.exit(1, str(error)+'\n')
    finally:
        if cap is not None:
            cap.release()


if __name__ == '__main__':
    raise SystemExit(main())
