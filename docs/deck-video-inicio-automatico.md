---
tipo: padrao
tags: [pptx, python-pptx, video, animacao, apresentacao, powerpoint, medido]
projeto: personagem
atualizado: 2026-09-28
---

# Vídeo com início automático em .pptx, por Python

**Quando usar:** inserir vídeo num slide existente que deve tocar sozinho quando o slide aparece
(abertura de tópico, vinheta), sem o apresentador clicar.

## O que o python-pptx não faz
`shapes.add_movie()` embute o vídeo (com `p14:media`) mas deixa **clique para reproduzir**. O
início automático é XML de `p:timing` escrito à mão:
- `mainSeq` com o primeiro `par` em `stCondLst` = `delay="indefinite"` + `evt="onBegin"` (`tn val=2`);
- efeito `presetClass="mediacall"`, `nodeType="afterEffect"`, `p:cmd type="call" cmd="playFrom(0.0)"`
  apontando o `spid` do vídeo, `dur` = duração em ms;
- `p:video/p:cMediaNode showWhenStopped="0"` = **ocultar quando não estiver em reprodução** (o vídeo
  em tela cheia some ao terminar e revela o slide de baixo).
- `p:timing` entra **antes de `p:extLst`** (ordem do schema), não no fim do `p:sld`.

## Armadilha
Deck gerado pelo **pptxgenjs** nomeia mídia `ppt/media/media-1-1.mp4`; o python-pptx 1.0.2 quebra
ao numerar mídia nova (`TypeError: '<' not supported between NoneType`). Substituir
`package.next_media_partname` por um gerador de nome próprio (`/ppt/media/aberturaN.mp4`).

## Verificação que vale
Abrir no PowerPoint por COM, somente leitura: `TimeLine.MainSequence.Item(1).Timing.TriggerType = 3`
(após o anterior), `EffectType = 83` (reproduzir mídia),
`AnimationSettings.PlaySettings.HideWhileNotPlaying = -1`. Abrir sem pedido de reparo já valida o XML.
Script de referência: o inserido no deck da apresentação (fora deste repo).
Ver [[google-flow-automatizado-pelo-navegador-interno]] e [[midia-de-fundo-em-deck-gerado-por-pptxgenjs]].
