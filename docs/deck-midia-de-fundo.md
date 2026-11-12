---
tipo: padrao
tags: [pptx, pptxgenjs, apresentacao, video, imagem, ia, medido]
projeto:
atualizado: 2026-09-28
---

# Mídia de fundo em deck gerado por pptxgenjs

**Quando usar:** ao pôr imagem ou vídeo (ex.: gerados no Google Flow) num deck que é
**gerado por script**. A mídia entra no gerador, e não no .pptx à mão, porque gerar de novo
apagaria a edição manual.

- **Não existe z-order no pptxgenjs.** A ordem de chamada é a pilha: a mídia de fundo entra
  **antes** do texto. Por isso ela vai como parâmetro opcional das funções `capa`/`base`/`divisor`.
- **Transparência medida** (conferida em PDF do PowerPoint):
  - Slide branco com conteúdo: marca d'água `transparency: 92`. Com 88, imagem escura
    compete com os cartões.
  - Slide escuro (capa, divisor): `transparency: 45` sobre o fundo azul-noite.
- **Vídeo:** `addMedia({type:"video", path, cover})`. O `cover` precisa ser **data URI base64**
  (quadro extraído com `ffmpeg -ss 2 -frames:v 1`). O vídeo inicia **com clique ou espaço**, porque
  o pptxgenjs não grava autoplay. Com texto por cima, pôr um véu retangular azul-noite a 40%.
- **Emendar clipes do Veo** de mesmo codec: `ffmpeg -f concat -safe 0 -i lista.txt -c copy`.
  Os caminhos em `lista.txt` são **relativos ao próprio arquivo de lista**.
- **`addNotes` várias vezes concatena, sem separador.** Dá para o helper de mídia acrescentar
  "gerado por IA" às notas do slide. Coloque `\n\n` no fim desse trecho.
- **Imagem com conteúdo no centro ou à direita** (ícones, texto em inglês) colide com título
  longo de divisor. Conferir cada divisor e trocar a imagem por uma abstrata.
- Conferência pelo PowerPoint via COM: ver [[qa-de-pptx-pelo-powerpoint-via-com]] e
  [[deck-de-palestra-sanitizado-confere-texto-e-imagem]].

## Vídeo iniciando sozinho (autoplay)
pptxgenjs só grava "ao clicar" (`hlinkClick action="ppaction://media"`, sem `<p:timing>`).
Solução medida: um pós-processador Python que, em cada slide com vídeo:
1. remove o `hlinkClick`;
2. insere depois de `</p:clrMapOvr>` o `<p:timing>` que o PowerPoint grava para "Iniciar:
   Automaticamente". São um `p:par` com `nodeType="afterEffect"`, `presetClass="mediacall"`,
   `cmd="playFrom(0.0)"` com `dur` em ms (via ffprobe) e um `p:video/p:cMediaNode`. Para loop,
   acrescentar `repeatCount="indefinite"` no `cTn` do `cMediaNode`.

Dentro do pacote a mídia é renomeada (`media-N.mp4`). Para saber qual vídeo é loop,
comparar o **hash do conteúdo** com os arquivos de origem.

Plugar no gerador: um `salvar(pres, nome)` comum que faz `writeFile` e depois
`execFileSync("python", [script, arquivo])`. Assim o autoplay sobrevive quando o deck é gerado de novo.
Conferido pelo COM: `TimeLine.MainSequence(1).Timing.TriggerType = 3` (após anterior) e
`PlaySettings.PlayOnEntry = -1`; `LoopUntilStopped = -1` nos loops.

## Unificar vários decks gerados num só
- Cada gerador troca `new pptxgen()` por `global.__PRES || new pptxgen()`. Um gerador-mestre cria
  a apresentação, liga uma flag global e dá `require()` em cada script, que desenha na
  apresentação compartilhada. Os helpers `abertura()` e `salvar()` viram no-op sob a flag. Os
  decks avulsos continuam funcionando sem mudança.
- Elemento em todos os slides (logotipo de canto): `pres.slides.forEach(s => s.addImage(...))`
  no fim. Como entra por último, fica por cima de tudo.
- ⚠️ **O pptxgenjs não deduplica mídia.** Cada `addImage` embute uma cópia. Um logotipo de 500 KB
  em 90 slides e fundos em 2K levaram o deck a **159 MB**. Com logotipo de 160 px e fundos
  reduzidos a 1920 px JPEG q85, caiu para **53 MB**.
- **Remover duplicados e reordenar** fica depois do `writeFile`, com python-pptx:
  `prs.part.drop_rel(sldId.rId)` e reordenação do `sldIdLst`. Os slides são localizados por
  **(rótulo, título)** com `assert` de uma ocorrência só; se o texto do gerador mudar, o script
  para em vez de apagar o slide errado. As partes órfãs somem no `save`.
- Símbolo institucional com fundo preto quadrado: recortar em círculo com máscara
  supersampleada (4×) e alfa, para servir em slide claro e escuro.
- Via COM, **não chamar `$p.Quit()`** quando o usuário estiver com decks abertos. Fechar só a
  própria cópia. Arquivo aberto no PowerPoint dá `EBUSY` ao ser regravado.

## Lição de erro
Editar JS com Python num heredoc do bash, usando `re.subn(..., '\\1', ...)` numa string com
`\n`, gravou um byte **`\x01`** no lugar do grupo e cortou o começo da linha. O node acusou
`Invalid or unexpected token`. Depois de editar por script, rodar `grep -c $'\x01'` e usar
`r'\g<1>'` no replacement.

## Vinheta de abertura que emenda num slide estático
- Vídeo de abertura que **termina parado no mesmo enquadramento** da imagem do slide seguinte (sem fade
  final) dá passagem sem salto. Nome sem "Loop" → `autoplay_videos.py` marca "uma vez".
- Capa do vídeo: último quadro, `ffmpeg -sseof -0.1 -i v.mp4 -frames:v 1`.
- Ao inserir slides no início de um gerador, revisar todo filtro por índice (ex.: logotipo de canto que
  pula a capa) — os índices se deslocam. Ver [[2026-09-28--INSTITUICAO_identidade]].
- Para provar que uma troca de logotipo alcançou **todos** os slides, contar por hash as cópias em
  `ppt/media/` (o pptxgenjs embute uma por slide): antigo = 0 e novo = nº esperado de slides.
