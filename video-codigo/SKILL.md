---
name: video-codigo
description: Cria vídeo como código — o Claude escreve a animação em um único HTML (GSAP, Canvas, SVG, Three.js, p5.js + p5.brush) e render.mjs grava em MP4 quadro a quadro, com arquivo de marca (BRAND.md) e música própria. Use para motion graphics, explainers, cenas 3D e abertura/vinhetas. Nunca com dado de caso.
---

# Vídeo como código (padrão do repo awesome-opus5-5-videos, adaptado)

Receita: prompt curto → **um HTML** → render determinístico → MP4. Sem editor de vídeo.

## Contrato do HTML (obrigatório, senão o render não funciona)
- Um arquivo, bibliotecas só por CDN com **versão fixa** (cdnjs/jsDelivr), fundo opaco, 1920x1080 salvo pedido.
- Expor `window.__duration` (segundos) e `window.__seek(t)` (síncrono ou Promise nativa; **não retorne o timeline do GSAP** — `tl.time(t)` devolve o timeline e é thenable: use `t => { tl.time(t); }`) que desenha **exatamente** o estado em `t`. Nada de `requestAnimationFrame`/`Date.now` para animar.
- GSAP: um `timeline` pausado; `window.__seek = t => { tl.time(t); }`. p5/Canvas/Three: derivar tudo de `t` (ruído com semente fixa).
- Texto em fonte web carregada antes do seek (`document.fonts.ready`).

## Arquivo de marca ("Brand File")
Antes de criar, leia `BRAND.md` do projeto (cores hex, fontes, logo, tom, margens). Se não existir, copie `BRAND.template.md` desta pasta para o projeto e preencha com o usuário. O HTML deve usar essas variáveis como CSS custom properties no `:root`.

## Efeitos open-source
p5.js + p5.brush (traço/pincel pintado), thinking-orbs (orbes de "pensando"), GSAP, Three.js. Confira o repo de cada um, fixe a versão e prefira CDN. Não reinventar efeito que a biblioteca já traz.

## Música própria
`--audio faixa.mp3` mixa no MP4 com fade-out de 1 s e corta na duração do vídeo. Só faixas que o usuário forneceu (direitos dele).

## Render
```
node ~/.claude/skills/video-codigo/render.mjs animacao.html saida.mp4 [--fps 30] [--audio musica.mp3] [--w 1920 --h 1080]
```
Usa o Edge instalado (sem baixar navegador) e o ffmpeg do PATH. Veja `exemplos/ola.html`.

## Fluxo
1. Pedir/ler o BRAND.md e a duração. 2. Escrever o HTML (prompt-base: "motion graphics de N segundos, mostrando X, usando BRAND.md"). 3. Render de 1 s (`--fps 10`) para conferir. 4. Render final, abrir o MP4 e revisar quadros-chave antes de entregar.
Biblioteca de prompts: `gh repo clone yihui-dev/awesome-opus5-5-videos` (pasta `prompts/`, 703 prompts).
