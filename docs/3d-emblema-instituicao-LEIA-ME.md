# Emblema INSTITUICAO 3D — padrão (v7, aprovado em 07/10/2026)

Moeda 3D girando 360°: **frente** INSTITUICAO · [UNIDADE], **verso** coruja. Este é o **padrão oficial**
da peça. Qualquer nova versão parte do `.blend` mestre, não do zero.

## O que tem aqui

| Pasta / arquivo | Para quê |
|---|---|
| `renders/emblema-instituicao-giro-1080.mp4` | Vídeo 1080×1080, 6 s, 24 fps, em laço, fundo degradê preto→cinza |
| `renders/emblema-instituicao-giro.gif` | **GIF para WhatsApp** (480 px, 15 fps, ~4,6 MB) |
| `renders/emblema-instituicao-giro-whatsapp.mp4` | Mesmo giro em MP4 leve (720 px, ~0,8 MB). Se o GIF vier granulado no WhatsApp, mande este: ele o trata como GIF por não ter áudio |
| `renders/transparente/` | **Fundo transparente** para pôr sobre outros vídeos (ver abaixo) |
| `modelo-3d/emblema-instituicao-3d.glb` | **Modelo 3D universal** (PowerPoint 3D, web/three.js, Unity, Blender, visualizadores) |
| `blend/emblema-instituicao-3d.blend` | **Mestre editável** (texturas empacotadas, 100 MB). Blender 4.5 |
| `fontes/` | Imagens originais do emblema + mapas e contornos usados (a arte-fonte não é redesenhada) |
| `scripts/` | Para refazer tudo: contornos, render, GLB, verificação |

## Especificação do padrão
- **Frente:** letras, aros e pontos **extrudados** (geometria real, chanfro de 0,45 cm, altura 7 cm sobre disco de 2 m). Prata polida/escovada nos elementos altos; campo em preto acetinado com escovado circular.
- **Verso:** relevo da coruja por mapa de altura (8 cm) com metal prata/escuro por máscara.
- **Pontos do anel:** na linha horizontal central da palavra INSTITUICAO (correção da arte-fonte, que os tinha desalinhados). Para abrir espaço, as letras do anel de texto foram rotacionadas ao longo do círculo (arco superior 7% mais apertado, letras 5% menores; inferior 12% mais folgado). **Nenhuma letra foi redesenhada.**
- **Cena:** câmera fixa (0, −4,4, 0,7), giro de 144 quadros em Z, inclinação oscilante ±9° (laço perfeito), fundo radial neutro (preto nas bordas → cinza ~35% no centro) visto só pela câmera, ambiente de reflexo em degradê vertical neutro, 4 softboxes.
- **Render:** Cycles, GPU (OptiX/CUDA), 128 amostras + OpenImageDenoise, 1080×1080. ~10–12 s por quadro na RTX PRO 1000 de 8 GB (~25–30 min o giro completo).

## Fundo transparente — como usar em outros vídeos
Pasta `renders/transparente/`:
- `emblema-instituicao-giro-alpha.mov` (87 MB) — **ProRes 4444 com alfa**: o formato mais seguro em editores (Premiere, DaVinci Resolve, Final Cut, After Effects).
- `emblema-instituicao-giro-alpha.webm` (4 MB) — **VP9 com alfa**: leve; toca em Chrome/Edge e em DaVinci/Resolve recentes. Não funciona no WhatsApp, no CapCut e em alguns players.
- `png/a_0001.png … a_0144.png` — **sequência PNG RGBA**: universal (importe como sequência a 24 fps).
- Os três tiveram o alfa verificado (0–255) e o comando de sobreposição abaixo foi testado.

Com ffmpeg, sobre um vídeo de fundo (emblema no canto, 360 px de largura):
```bash
ffmpeg -i fundo.mp4 -stream_loop -1 -i emblema-instituicao-giro-alpha.mov \
  -filter_complex "[1:v]scale=360:-1[e];[0:v][e]overlay=W-w-40:40:shortest=1" -c:a copy saida.mp4
```

## Refazer / alterar
```bash
# Windows (PowerShell/bash): render completo, fundo degradê
"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" -b blend/emblema-instituicao-3d.blend -P scripts/cycles_gpu.py -o saida/f_ -a
# Fundo transparente: acrescente  -P scripts/render_alpha.py  depois do cycles_gpu.py
```
Para um **quadro único**: troque `-a` por `-f 1`. Para outra duração, mude `frame_end` (e as chaves de rotação em 1→145 mantêm o laço perfeito para 144 quadros).

## Limites conhecidos
- No **verso**, em ângulo muito rasante, o relevo da coruja mostra um efeito de "camadas empilhadas" (limite do relevo por mapa de altura). Dura poucos quadros do giro.
- O **GLB** não leva o escovado (bump/anisotropia): fica prata acetinada lisa. O verso vai com cor e rugosidade assadas em textura, e malha 30% decimada. Para o visual completo, use o `.blend` ou os vídeos.
- O GLB tem **cerca de 635 mil polígonos**: pesado para celular antigo. Para web leve, reduza no Blender (modificador Decimate).
- Renderizar no **Mac** exige trocar `scripts/cycles_gpu.py` por Metal (`compute_device_type='METAL'`) e leva mais tempo.

## Regras
- A arte do emblema vem **dos arquivos em `fontes/`**; não redesenhar por IA. Alterações de arte só quando pedidas e descritas (como as dos pontos e do anel acima).
- `scripts/gerar_contornos_emblema.py` reproduz os contornos corrigidos a partir de `fontes/emblema-3d-unidade-mg.png` (testado: saída idêntica à usada nos vídeos).

- `renders/transparente/emblema-instituicao-giro-alpha-previa.mp4` — **só para assistir**: o alfa composto sobre cinza escuro, em H.264. O Windows (Filmes e TV) não abre o `.mov` ProRes 4444 (erro 0xC00D5212, codec `ap4h`); esse `.mov` é para editores.
