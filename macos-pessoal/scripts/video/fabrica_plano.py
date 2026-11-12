#!/usr/bin/env python3
"""Fábrica de planos sem Flow: um JSON por plano -> vídeo 1920x1080 com áudio.

Modos (campo "modo" do JSON):
  B   cutout 2.5D: recortes das pranchas sobre o cenário, fala move o corpo. Render em segundos.
  AB  gera o plano B (só imagem), pega o quadro inicial e o final, e o LTX-2 local anima
      entre os dois (movimento real, rostos e cenário consistentes). Depois amplia a 1080p
      e cola o áudio das falas.

Uso:
  python3 fabrica_plano.py plano.json [--saida DIR]

Exemplo de plano.json (caminhos absolutos ou relativos à pasta do JSON):
{
  "id": "teste01", "duracao": 4, "fps": 24,
  "cenario": "casa.png",              # 16:9 já ampliado, ou 4:3 (corta embaixo)
  "personagens": [{"nome": "personagem_a", "recorte": "personagem_a.png", "x": 560, "y": 930, "altura": 470}],
  "falas": [{"quem": "personagem_a", "audio": "personagem_a.wav", "inicio": 0.4}],
  "modo": "AB",
  "prompt_a": "texto em inglês, movimento muito calmo",
  "trava_final": 1.0                  # força do quadro final no LTX (0 desliga)
}
Requer: ~/nola-macm5/.venv (PIL, numpy), ffmpeg, e para AB o ltx-2-mlx em ~/Estudio/ltx-2-mlx
com os modelos em ~/Estudio/modelos-ltx. Local: nada sai da máquina.
"""
import argparse, json, math, os, subprocess, sys, wave
from pathlib import Path

LTX = Path("~/Estudio/ltx-2-mlx/.venv/bin/ltx-2-mlx").expanduser()
MODELO = Path("~/Estudio/modelos-ltx/ltx-2.3-mlx-q4").expanduser()
GEMMA = "mlx-community/gemma-3-12b-it-4bit"
W, H = 1920, 1080


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        sys.exit(f"ERRO {' '.join(map(str, cmd[:2]))}: {r.stderr[-600:]}")
    return r


def caminho(base: Path, p: str) -> Path:
    q = Path(p).expanduser()
    return q if q.is_absolute() else (base / q)


def mixar_audio(plano, base, saida: Path):
    dur = plano["duracao"]
    ins, filt, labels = [], [], []
    for i, f in enumerate(plano.get("falas", [])):
        ins += ["-i", str(caminho(base, f["audio"]))]
        ms = int(f.get("inicio", 0) * 1000)
        filt.append(f"[{i}]aresample=48000,adelay={ms}:all=1[a{i}]")
        labels.append(f"[a{i}]")
    if not labels:
        sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono", "-t", str(dur), str(saida)])
        return
    filt.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,apad=whole_dur={dur},atrim=0:{dur}[o]")
    sh(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(filt), "-map", "[o]", "-ar", "48000", str(saida)])


def envelope(wav: Path, inicio, fps, n):
    import numpy as np
    w = wave.open(str(wav))
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
    if w.getnchannels() > 1:
        a = a.reshape(-1, w.getnchannels()).mean(axis=1)
    sr = w.getframerate()
    out = np.zeros(n)
    for i in range(n):
        t = i / fps - inicio
        if t < 0:
            continue
        s, e = int(t * sr), int((t + 1 / fps) * sr)
        if e <= len(a):
            out[i] = np.sqrt(np.mean(a[s:e] ** 2))
    return out


def carregar_bocas(c, base: Path):
    """Três sprites do mesmo personagem (fechada/meia/aberta), sem fundo, alinhados à 'fechada' por
    correlação da máscara alfa e escalados juntos para a altura pedida."""
    import numpy as np
    from PIL import Image
    est = {k: Image.open(caminho(base, v)).convert("RGBA") for k, v in c["bocas"].items()}
    ref = est["fechada"]
    a0 = np.asarray(ref.split()[3], dtype=float)[::4, ::4]
    al = {}
    for k, im in est.items():
        if im.size != ref.size:
            im = im.resize(ref.size, Image.LANCZOS)
        a = np.asarray(im.split()[3], dtype=float)[::4, ::4]
        corr = np.fft.ifft2(np.fft.fft2(a0) * np.conj(np.fft.fft2(a))).real
        dy, dx = np.unravel_index(np.argmax(corr), corr.shape)
        dy = dy - a.shape[0] if dy > a.shape[0] // 2 else dy
        dx = dx - a.shape[1] if dx > a.shape[1] // 2 else dx
        al[k] = im.transform(im.size, Image.AFFINE, (1, 0, -dx * 4, 0, 1, -dy * 4), resample=Image.BILINEAR)
    bb = [im.getbbox() for im in al.values()]
    box = (min(b[0] for b in bb), min(b[1] for b in bb), max(b[2] for b in bb), max(b[3] for b in bb))
    s = c["altura"] / (box[3] - box[1])
    out = {k: im.crop(box).resize((int((box[2] - box[0]) * s), c["altura"]), Image.LANCZOS) for k, im in al.items()}
    if "olhos" in out:
        out["_mascara_olhos"] = mascara_olhos(out["fechada"], out["olhos"], c.get("pescoco", 0.35))
    return out


def mascara_olhos(fechada, olhos, pescoco):
    """Máscara (L) da região que muda entre 'fechada' e 'olhos' (as pálpebras), só na parte da cabeça,
    dilatada e suavizada, para colar os olhos fechados sobre qualquer pose de boca."""
    import numpy as np
    from PIL import Image, ImageFilter
    a = np.asarray(fechada.convert("RGB"), dtype=int)
    b = np.asarray(olhos.convert("RGB"), dtype=int)
    d = np.abs(a - b).max(axis=2)
    h = d.shape[0]
    d[int(h * pescoco * 0.75):, :] = 0  # abaixo do nariz/boca não entra (a boca vem da pose escolhida)
    m = Image.fromarray(((d > 28) * 255).astype("uint8"))
    m = m.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
    return m


def forca_piscar(idx, i, fps, n):
    """Força do piscar (0..1) no quadro i: piscadas a cada 2,2–4,6 s, de 4 quadros."""
    import random
    rng = random.Random(idx * 7 + 3)
    t, forca = 0.6 + idx * 0.5, [0.0] * n
    while t * fps < n:
        q = int(t * fps)
        for k, v in enumerate((0.5, 1.0, 1.0, 0.5)):
            if q + k < n:
                forca[q + k] = v
        t += rng.uniform(2.2, 4.6)
    return forca[i]


def mover_cabeca(sprite, pescoco, t, idx, fala):
    """Gira e balança a cabeça (acima do pescoço) em torno da base do pescoço; o corpo fica.
    Corpo e cabeça têm rampas de transparência complementares na junção, sem fantasma da cabeça parada."""
    import numpy as np
    from PIL import Image
    w, h = sprite.size
    cut, mix = int(h * pescoco), max(8, int(h * 0.04))
    rows = np.arange(h)
    rampa_c = np.clip(1 - (rows - cut) / mix, 0, 1)             # cabeça: 1 acima do corte, some em `mix` px
    rampa_b = np.clip((rows - (cut - mix)) / (2 * mix), 0, 1)   # corpo: aparece em torno do corte
    arr = np.asarray(sprite, dtype=float)
    cab, cor = arr.copy(), arr.copy()
    cab[..., 3] *= rampa_c[:, None]
    cor[..., 3] *= rampa_b[:, None]
    cab_im = Image.fromarray(cab.astype("uint8"), "RGBA")
    cor_im = Image.fromarray(cor.astype("uint8"), "RGBA")
    ang = (0.9 + 0.8 * fala) * math.sin(2 * math.pi * (0.23 * t + idx * 0.31)) + 0.4 * math.sin(2 * math.pi * 0.61 * t + idx)
    dy = (1.2 + 2.2 * fala) * math.sin(2 * math.pi * (0.9 * t + idx * 0.17))
    cab_r = cab_im.rotate(ang, center=(w / 2, cut), resample=Image.BILINEAR, translate=(0, dy))
    cor_im.alpha_composite(cab_r)
    return cor_im


def niveis_boca(e, hold=2):
    """Envelope (0..1) -> nível da boca por quadro: 0 fechada, 1 meia, 2 aberta, com permanência mínima."""
    lv, cur, seg = [], 0, hold
    for x in e:
        alvo = 0 if x < 0.12 else (1 if x < 0.42 else 2)
        if alvo != cur and seg >= hold:
            cur, seg = alvo, 0
        seg += 1
        lv.append(cur)
    return lv


def render_b(plano, base: Path, audio_mix: Path, saida: Path):
    """Compõe os quadros e grava `saida` (1920x1080) já com o áudio."""
    import numpy as np
    from PIL import Image, ImageDraw
    fps, dur = plano.get("fps", 24), plano["duracao"]
    n = fps * dur
    bg = Image.open(caminho(base, plano["cenario"])).convert("RGB")
    bw, bh = bg.size
    ch = int(bw * 9 / 16)
    if ch <= bh:
        bg = bg.crop((0, bh - ch, bw, bh))
    bg = bg.resize((int(W * 1.06), int(H * 1.06)), Image.LANCZOS)
    chars = []
    for c in plano["personagens"]:
        if "bocas" in c:
            chars.append((c, carregar_bocas(c, base)))
            continue
        im = Image.open(caminho(base, c["recorte"])).convert("RGBA")
        im = im.crop(im.getbbox())
        s = c["altura"] / im.height
        chars.append((c, im.resize((int(im.width * s), c["altura"]), Image.LANCZOS)))
    env = {}
    for f in plano.get("falas", []):
        e = envelope(caminho(base, f["audio"]), f.get("inicio", 0), fps, n)
        m = e.max()
        env[f["quem"]] = np.maximum(env.get(f["quem"], np.zeros(n)), e / m if m > 0 else e)
    niveis = {nome: niveis_boca(e) for nome, e in env.items()}
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(fps), "-i", "-", "-i", str(audio_mix), "-c:v", "h264_videotoolbox",
                          "-b:v", "12M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(saida)],
                         stdin=subprocess.PIPE)
    for i in range(n):
        t = i / fps
        z = 1 + 0.04 * (t / dur)
        b = bg.resize((int(W * 1.06 * z), int(H * 1.06 * z)), Image.BILINEAR)
        ox, oy = (b.width - W) // 2, (b.height - H) // 2
        frame = b.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
        for idx, (c, im) in enumerate(chars):
            if isinstance(im, dict):  # boca por poses: fechada / meia / aberta, comandada pelo áudio
                lv = niveis.get(c["nome"], [0] * n)[i]
                spr = im[("fechada", "meia", "aberta")[lv]]
                k = forca_piscar(idx, i, fps, n) if "olhos" in im else 0.0
                if k > 0:  # piscar: cola os olhos fechados sobre a pose de boca atual
                    msk = im["_mascara_olhos"].point(lambda v, k=k: int(v * k))
                    spr = Image.composite(im["olhos"], spr, msk)
                im = mover_cabeca(spr, c.get("pescoco", 0.35), t, idx, min(1.0, lv / 2))
                talk = 0.0
            else:
                talk = min(1.0, env.get(c["nome"], np.zeros(n))[i] * 1.6)
            breath = 1 + 0.008 * math.sin(2 * math.pi * (t * 0.35 + idx / 7))
            r = im.resize((int(im.width * (1 - 0.018 * talk)), int(im.height * breath * (1 + 0.035 * talk))), Image.BILINEAR)
            sh_ = Image.new("RGBA", (int(r.width * 0.8), 30), (0, 0, 0, 0))
            ImageDraw.Draw(sh_).ellipse((0, 0, sh_.width, 30), fill=(60, 35, 10, 70))
            frame.alpha_composite(sh_, (c["x"] - sh_.width // 2, c["y"] - 18))
            frame.alpha_composite(r, (c["x"] - r.width // 2, c["y"] - r.height - int(6 * talk)))
        p.stdin.write(frame.convert("RGB").tobytes())
    p.stdin.close()
    if p.wait():
        sys.exit("ERRO no ffmpeg do render B")


def quadro(video: Path, n_quadro: int | None, saida: Path, largura=832, altura=480):
    sel = "select=eq(n\\,{})".format(n_quadro) if n_quadro is not None else "select=eq(n\\,0)"
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf",
        f"{sel},scale={int(altura*16/9+0.5)}:{altura},crop={largura}:{altura}", "-frames:v", "1", str(saida)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plano")
    ap.add_argument("--saida", default=None)
    a = ap.parse_args()
    pj = Path(a.plano).expanduser().resolve()
    plano = json.loads(pj.read_text())
    base = pj.parent
    out = Path(a.saida).expanduser().resolve() if a.saida else base / plano["id"]
    out.mkdir(parents=True, exist_ok=True)
    mix = out / "audio.wav"
    mixar_audio(plano, base, mix)
    b = out / "b.mp4"
    render_b(plano, base, mix, b)
    print("B ok:", b)
    if plano.get("modo", "B") == "B":
        return
    fps, dur = plano.get("fps", 24), plano["duracao"]
    n = fps * dur
    n = -(-(n - 1) // 8) * 8 + 1  # LTX pede 8k+1 quadros: arredonda para cima e corta no fim
    kf, lf = out / "quadro_inicial.png", out / "quadro_final.png"
    quadro(b, 0, kf)
    quadro(b, fps * dur - 1, lf)  # último quadro que o B realmente tem
    if plano.get("modo") == "A2V":  # PADRÃO do estúdio (escolha do usuário, 11/11): o LTX anima ouvindo as falas
        dur_ltx = n / fps
        aud = out / "audio_a2v.wav"
        sh(["ffmpeg", "-v", "error", "-y", "-i", str(mix), "-af", f"apad=whole_dur={dur_ltx},atrim=0:{dur_ltx}",
            "-ar", "48000", "-ac", "1", str(aud)])
        cmd = [str(LTX), "a2v", "-m", str(MODELO), "--gemma", GEMMA, "--distilled", "--audio", str(aud),
               "--image", str(kf), "0", "1.0", "-W", "832", "-H", "480", "-f", str(n), "--frame-rate", str(fps),
               "-s", str(plano.get("seed", 7)), "-p", plano["prompt_a"], "-o", str(out / "a_baixa.mp4")]
    else:
        cmd = [str(LTX), "generate", "-m", str(MODELO), "--gemma", GEMMA, "--distilled", "--image", str(kf), "0", "1.0",
               "-W", "832", "-H", "480", "-f", str(n), "--frame-rate", str(fps), "--no-audio",
               "-s", str(plano.get("seed", 7)), "-p", plano["prompt_a"], "-o", str(out / "a_baixa.mp4")]
        trava = float(plano.get("trava_final", 0))
        if trava > 0:
            cmd[cmd.index("-W"):cmd.index("-W")] = ["--image", str(lf), str(n - 1), str(trava)]
    print("LTX:", " ".join(cmd[:3]), "...")
    sh(cmd)
    final = out / f"{plano['id']}_1080.mp4"
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(out / "a_baixa.mp4"), "-i", str(mix), "-vf",
        f"scale={W}:{H}:flags=lanczos", "-t", str(dur), "-c:v", "h264_videotoolbox", "-b:v", "12M", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(final)])
    print("AB ok:", final)


if __name__ == "__main__":
    main()
