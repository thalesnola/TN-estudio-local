---
tipo: padrao
tags: [video, narracao, ffmpeg, sincronia, flow, omni, voz]
projeto: producao-midia-design
atualizado: 2026-09-28
---

# Narração sincronizada a vídeo montado por cenas

Vídeo feito de clipes concatenados (ex.: 6 × 8 s do Veo) se narra **uma fala por cena**, não um texto corrido.

1. Achar os cortes: `ffmpeg -i v.mp4 -vf "select='gt(scene,0.25)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*"`.
   Transição suave pode escapar ao limiar: conferir pela duração dos clipes de origem.
2. Folha de contato (`-vf "fps=1/2,scale=320:-1,tile=6x4" -frames:v 1`) para descrever o que cada cena mostra.
3. Fala de cada cena ≤ 16 palavras (≈2,2 palavras/s, 0,5 s de entrada, termina antes de 7,5 s), para a
   frase fechar junto com o corte.
4. A última fala faz a ponte para o slide seguinte.
5. Voz salva no Flow só existe no **Omni** (gera vídeo do personagem): gerar um clipe por fala e aproveitar
   só o áudio, posicionado com `adelay`; trilha original rebaixada por baixo; remux com `-c:v copy`.
6. Texto que vai ao Flow: sem nome, cidade, telefone, processo; ter frases reserva para o filtro de política.

Relacionadas: [[google-flow-automatizado-pelo-navegador-interno]], [[midia-de-fundo-em-deck-gerado-por-pptxgenjs]].

## Armadilha medida
- `loudnorm` do ffmpeg sobe a saída para **96 kHz** sem avisar; terminar a cadeia com `aresample=48000`.
- Para emendar um trecho novo **antes** de um vídeo já narrado: concatenar por filtro (não por `-c copy`), fade só
  na junção, e trocar também o quadro de capa do vídeo no `.pptx` (`image-N-x.png` ligado ao `p:pic` da mídia).
