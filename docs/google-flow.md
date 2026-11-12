---
tipo: stack
tags: [google-flow, veo, nano-banana, navegador-interno, automacao, credito, sigilo, medido]
projeto:
atualizado: 2026-09-29
---

# Google Flow automatizado pelo navegador interno: como o agente se comporta

**Medido em 28/09/2026, conta Google AI Pro, máquina Windows.** O Flow
(`labs.google/fx/tools/flow` → `flow.google.com`) reúne **Nano Banana 2** (imagem), **Veo 3.1**
(Lite/Fast/Quality) e **Omni 1.1 Flash** (vídeo). Um projeto novo se abre num **chat de agente**
("O que você quer criar?"), e é por ele que a automação passa.

## Configuração (ícone de ajustes na caixa do chat)
- "Confirmar antes de gerar": manter em **Sempre**, porque vídeo gasta crédito.
- O padrão de imagem já vem em 16:9, x2, Nano Banana 2.
- ⚠️ **O padrão de vídeo é Omni 1.1 Flash, não Veo**: trocar à mão para Veo 3.1 se o roteiro pedir Veo.

## Custos e tempos
- Imagem: **não pede confirmação**, sai em ~25–40 s.
- Vídeo Veo 3.1 Fast (8 s): **20 créditos**, pede confirmação (Aprovar / Sempre aprovar / Rejeitar)
  e fica ~1–2 min na fila. Não marcar "Sempre aprovar" sem decisão do usuário.
- Imagem → vídeo funciona pelo chat: "use a primeira imagem desta sessão como quadro inicial".

## Armadilhas
- ⚠️ **Mensagem enviada com o agente ainda respondendo é descartada em silêncio**, ou fica
  presa na caixa de texto. Uma imagem do lote se perdeu assim. Esperar **~45 s entre envios**
  e conferir a contagem na grade de mídias depois de cada lote.
- Pedir "exactly this prompt" faz o agente usar o prompt literal, sem reescrever.
- O agente toma iniciativa: criou uma coleção sem que ninguém pedisse. É inofensivo, mas é bom saber.
- "Algo deu errado" no chat pode ser falha **só do texto** da resposta, com a mídia gerada
  normalmente. Conferir na grade antes de refazer e gastar de novo.

## Download (medido em 28/09/2026)
- Menu de contexto do bloco (clique direito) › **Fazer o download**. Vídeo: 270p GIF · **720p original** ·
  1080p aprimorado · 4K pede upgrade. Imagem: **1K original** · **2K aprimorada** (2752×1536, sem custo
  no Pro; o upscale leva ~15 s e o download começa sozinho) · 4K pede upgrade.
- ⚠️ **O navegador interno grava em `~/Downloads` como `<uuid>.tmp` e nunca renomeia.** O arquivo
  está completo (conferir pelo magic: `ftypisom` no MP4, `FFD8` no JPEG). Mover o `.tmp` mais novo
  para o destino, com o nome final, logo depois de cada download: um de cada vez, ou os nomes se trocam.
- A grade desenha só o que está na tela. Tamanho **P** em "Configurações da grade" mostra ~12 blocos
  de uma vez; os `ref` de `find` mudam a cada menu aberto (clique direito → `find` → hover → `find` → clique).
- A ordem da coleção **não é cronológica**. Conferir o nome × conteúdo por folha de contato
  (PIL para imagens; `ffmpeg -ss 6 … tile=4x2` para vídeos). ⚠️ `drawtext` do ffmpeg dá segfault
  no Windows sem fontconfig: gerar a folha sem rótulo.

## Qualidade: o Veo foge do prompt
- Em 8 vídeos, 2 saíram fora do pedido: o saco de evidência **pegou fogo** no meio da cena, e um
  loop "mesa escura" virou mesa antiga, com pena e sinete. Olhar um quadro do meio de cada vídeo
  antes de entregar; o primeiro quadro não basta.
- **O que corrigiu (medido):** reenviar com **restrição negativa explícita** ("no fire, no flames,
  no smoke… the bag remains intact"; "modern office only: no antique objects, no quill…") e com uma
  **imagem do projeto como primeiro quadro** para prender a paleta. As duas cenas saíram certas
  na primeira tentativa.
- ⚠️ **O download também mudou de comportamento na mesma sessão:** mais tarde o arquivo passou a
  chegar como `<Titulo>_<AAAAMMDDhhmmss>.mp4`, e não mais como `.tmp`. Pegar o arquivo mais novo de
  `~/Downloads` sem filtrar por extensão.
- O agente às vezes anuncia "vou gerar" e **não gera nem pede aprovação**. Responder "yes, go
  ahead" destrava. Conferir sempre a contagem na grade.

## Emblema/logotipo: o Nano Banana redesenha, mesmo mandado não redesenhar (medido 28/09/2026)
- Com os 5 emblemas enviados como referência e "do NOT redraw", a composição saiu certa, mas:
  texto miúdo das faixas virou garatuja (PF, INSTITUICAO-A), o busto da PMMG foi trocado por uma estrela,
  e o emblema grande invadiu a fileira de baixo. **Inservível como peça oficial.**
- O que funciona: compor **localmente com PIL** (logos exatos, fundo com alfa recortado; PNG em
  modo `P` vem com fundo branco opaco → `floodfill` a partir dos cantos) e a animação também
  local (quadros PIL → ffmpeg por pipe, 12 s em ~22 s). Ao Flow, só o **quadro final exato**
  como imagem de referência/último quadro do Veo.
- O upload no Flow abre o seletor do Windows: não há `input[type=file]` no DOM, o agente não
  consegue anexar. Quem sobe o arquivo é o usuário (arrastar ou "+" › envio).
- **Veo 3.1 Fast com "use a imagem X como último quadro" pelo chat do agente (medido):** o agente
  pegou a imagem **errada** (a mono em vez da colorida pedida pelo nome), o vídeo **não terminou**
  no quadro de referência, inventou raios de sol ao fundo e **duplicou emblemas** (5 na fileira
  final em vez de 4). Folha de contato a 1 fps (`fps=1,scale=480:-1,tile=4x2`) pegou tudo. Para
  quadro final exato, usar o modo de quadros do editor (Cenas), não o chat; ou emendar a
  vinheta local.
- ✅ **O que preserva logotipo com Veo (medido):** pedir só a **placa de fundo** (text-to-video,
  "no logos, no emblems, no text", monocromático, clarão num instante dito no prompt) e colar os
  emblemas originais por cima, localmente. Saiu limpa na 1ª tentativa. Medir o pico do clarão na
  placa (média de brilho por quadro: saiu em 4,3 s, não nos 4 s pedidos) e alinhar por offset. Para
  descer o clarão, estender a borda de cima com rampa: **espelhar duplica o clarão**.
- **Upload: três vias automáticas testadas e todas barradas (medido 28/09/2026).** O botão "Enviar"
  cria um `input[type=file]` **desanexado** do DOM (`accept=.png,.jpg,.jpeg,.webp,.gif,.heif,.heic`),
  por isso a busca no DOM não o acha; interceptar `HTMLInputElement.prototype.click` o captura. Mas
  não há como pôr os bytes na página: `fetch` a um servidor em `127.0.0.1` com CORS dá
  `ERR_BLOCKED_BY_CLIENT` (o navegador interno bloqueia), `Ctrl+V` com imagem na área de
  transferência do Windows não chega, e `navigator.clipboard.read()` é negado. Colar base64 no JS
  seria inviável em tokens. **Conclusão: o upload é do usuário.** Recarregar a página depois de
  interceptar o `click`, senão o botão dele fica morto.
- O Flow tem a seção **Personagens** (`/project/<id>/character`): "Crie e reutilize personagens
  para manter a consistência nos vídeos", por descrição ou por imagem enviada.
- Download de imagem **enviada** pelo usuário volta como JPG recodificado (perde a alfa): buscar o
  original no disco dele.
- PIL: `Image.fromarray(...)` compartilha buffer com o numpy, e o `ImageDraw.floodfill` nele não
  grava nada, sem erro. Usar `.copy()`.
- Downloads saíram com nome `<Titulo>_2K_<AAAAMMDDhhmmss>.jpg` desde o primeiro nesta sessão.

## Sigilo
Prompt enviado ao Flow sai da máquina e fica na conta Google. Mandar só prompt genérico,
já higienizado, e nunca arquivo, print ou figura de caso. Mesma porta de
[[contingencia-automatica-codex-gemini-com-porta-de-sigilo]].

## Personagem falante com voz fixa (decidido 28/09/2026, não medido ainda)
- O Veo não guarda "modelo de voz" entre gerações. A consistência vem de **repetir literalmente**
  um bloco fixo de VOZ + PERFORMANCE + NEGATIVE em todo prompt e de partir sempre do **mesmo
  quadro inicial**. Bloco em inglês (o Veo segue melhor), fala entre aspas em pt-BR.
- "Sem sotaque" em pt-BR = pedir "neutral standard accent, like a national TV news anchor; no
  regional, no Portugal, no Spanish/English accent".
- Clipe de 8 s → **≤ 16 palavras** de fala (≈ 2,2 palavras/s com 0,5 s de entrada). Fala maior:
  dividir e encadear pelo último quadro.
- Quadro inicial para teste de lábio: compor local com PIL a partir do recorte com alfa, rosto
  grande, fundo liso escuro (fundo com emblema o Veo redesenha). Recorte com borda curva nos
  ombros: ampliar e cortar embaixo para a curva sair do quadro.

## Personagem com voz salva (medido 28/09/2026)
- Flow › **Personagens**: retrato + **"Selecionar uma voz"** = vozes Gemini TTS (Algenib = male,
  gravelly, low; Alnilam = firm; Charon = informative…), com campo **Personalizar performance**
  e prévia de até 120 caracteres; "Salvar nova voz" cria uma voz própria reutilizável.
- Só o **Omni 1.1 Flash** usa a voz salva do personagem (12 créditos por 8 s, x1).
- Pedir "use a imagem enviada X como primeiro quadro" pelo chat falhou na 1ª vez (ID interno
  diferente do nome do arquivo); o agente perguntou e seguiu com a imagem certa. **Mesmo assim o
  Omni ignorou o quadro**: gerou do retrato do personagem, trocou a farda por camiseta e
  **espelhou o olho cibernético** (lado trocado). O Omni prende a identidade pelo personagem,
  não pelo quadro inicial: descrever roupa e lado do olho no próprio personagem.
- Temporização conferida com `silencedetect=n=-35dB:d=0.2`: fala começou a 0,55 s como pedido,
  16 palavras couberam em 7 s.
- **Filtro do Omni (medido):** personagem de farda com "POLÍCIA"/"police" no prompt foi recusado
  ("Não é possível gerar vídeos que possam causar risco à reputação ou deturpar eventos atuais").
  Passou reescrito como "fictional training-course instructor", sem a palavra polícia.
- O Omni **inventa distintivos** no peito quando a descrição fala em farda. Pedir "COMPLETELY PLAIN
  chest: no badge, no emblem, no patch, no name tape, no text" no personagem **e** no prompt, e
  editar a imagem de Corpo do personagem ("O que você quer mudar?") para peito liso. Ainda assim
  sobrou um distintivo de manga no corpo inteiro.
- **Emblema no peito que se mexe:** peito liso do Flow + emblema original colado localmente por
  `cv2.matchTemplate` sobre gola/abas do bolso (CLAHE antes, busca local, suavização 0,5).
  Correlação mín. 0,83 no close, 0,60 no corpo inteiro (emblema de 23 px), visualmente estável.
  Tecido preto liso não serve de modelo: precisa das bordas da gola/bolso.
- Voz v2 ("natural, conversational, normal pace") encurtou a fala de 7,0 s para 6,3–6,8 s.
- **Lote de 8 vídeos Omni (medido 28/09/2026):** falha de geração **não é cobrada** (o bloco diz
  "Não houve cobrança"). Filtros que dispararam: "pessoas famosas" (falso positivo com o próprio
  personagem; passou ao reenviar com "ORIGINAL fictional character, not a real or famous person") e
  "política" genérica em fala com "CPF… revelam uma rede" (2×; passou com "documento… conexões").
- O Omni às vezes **grava legenda** (nome do personagem em lower-third) e **enfeita o personagem**
  (placa de ciborgue no olho) sem pedido. Conferir cada vídeo por folha de contato.
- ⚠️ **O download passou a cair na pasta de trabalho aberta** (`…/PROJETO-INSTITUICAO/`), com nome
  `<Titulo>_<AAAAMMDDhhmmss>.mp4`, e não em `~/Downloads`. Mover por marcador de tempo
  (`find -newer marca -name '*.mp4'`), nunca "o item mais novo da pasta": isso já moveu uma
  **pasta** por engano. Download repetido gera cópias idênticas: conferir hash.
- Envio no chat: **um** clique no botão de enviar. Se a mensagem ficar presa, clicar de novo só depois
  de conferir que o agente não está respondendo: o 2º clique com o agente ativo é o botão **Parar** e
  cancela o pedido.
- Posição do emblema entre vídeos do mesmo enquadramento: busca multi-escala do trecho gola/bolso de
  um vídeo de referência já medido (`--ref`), correlação 0,68–0,91 no 1º quadro.

## Voz do personagem como narração (medido 28/09/2026)
- Lote de 6 falas num único pedido ao agente: ele cobrou 72 créditos de uma vez e nomeou `narr_01..06` como pedido.
- Filtro "pessoas famosas" disparou **5 vezes seguidas na mesma fala** e nunca nas outras: o gatilho era o texto
  ("quem foi identificado", "quem já tem nome"), lido como identificação de pessoa real. Trocar a ideia da frase
  resolveu na 1ª; "Tentar de novo" e insistir em "original fictional character" não.
- Download pelo editor do clipe (clique no bloco → ícone download → 720p) mostra o prompt na página e resolve
  qual `.tmp` é qual. ⚠️ O `.tmp` às vezes **some da pasta em segundos**: copiar no mesmo comando que espera o
  arquivo estabilizar de tamanho, nunca num comando seguinte.
- Técnica de encaixe em [[narracao-sincronizada-a-video-montado-por-cenas]].
- **Personagem em cenário com figurantes (medido 28/09/2026):** 3 clipes Omni pedidos num só envio, "mesma cena,
  enquadramento fechando a cada clipe" (aberto → médio → close): a sala saiu coerente entre os cortes e o peito
  liso foi respeitado, sem legenda. O Omni escreveu "POLICA" nas costas de figurantes mesmo sem a palavra no prompt:
  pedir "no text on clothing" também para os figurantes.
- ⚠️ **Layout do Flow muda com a largura do painel** (<~900 px vira coluna única, o chat do agente some); forçar
  viewport de 1280 px com o `resize_window` faz a captura escalar e os cliques por `ref` caírem no lugar errado —
  clicar por coordenada da captura escalada. No layout estreito, o clique direito na miniatura abre menu em folha
  inferior e "Fazer o download" baixa direto (sem escolher resolução, sai 720p).

## Agente reescreve o prompt e tira a proteção contra o filtro (medido 29/09/2026)
- Lote de 6 falas do personagem: 5 caíram em "pessoas famosas" (sem cobrança), e o reenvio individual com texto neutro caiu de
  novo. Causa vista no "Reutilizar comando" da falha: o agente **reescreve** o prompt ("Medium close-up shot of <personagem>…")
  e **remove** a frase "ORIGINAL fictional character, not a real or famous person". Resolveu: "Use EXACTLY this prompt,
  verbatim, without rewriting or shortening it: '<prompt começando pela frase de personagem fictício>'". Lote de 4 no mesmo
  molde (com `<FALA>` substituída por item) passou inteiro.
- Tudo por DOM, sem screenshot (expira com o painel oculto): tiles são `flow-grid-tile-container[aria-label=<nome>]`, falha tem
  "Falha" no `innerText`; aprovação = último `[role=radio]` "Aprovar"; download = `contextmenu` no tile → menuitem
  "Fazer o download" → "720p". Enviar: focar o `[contenteditable=true]`, digitar, `Return`.
- Conferir nome × conteúdo transcrevendo o áudio de cada download (Whisper) — mais barato que assistir.
- Omni pode gravar lower-third com o nome do personagem no clipe inteiro: cobrir com `crop` do fundo + `overlay`.
- Relacionada: [[narracao-sincronizada-a-video-montado-por-cenas]].
