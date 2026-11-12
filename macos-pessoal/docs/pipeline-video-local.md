# Pipeline de vídeo local no M5 — o que foi testado e decidido (11/11/2026)

Objetivo: produzir episódios de uma série animada 3D **sem gastar crédito de geração de vídeo em nuvem**.
Material de entrada: pranchas 3D aprovadas (nunca foto real), cenários, vozes sintéticas. Instalação e
modelos: [instalacoes-m5.md](instalacoes-m5.md). Scripts: [`macos-pessoal/scripts/video/`](../scripts/video/).

## Os três métodos

| Método | O que faz | Tempo medido | Quando usar |
|---|---|---|---|
| **B — cutout 2.5D** (`fabrica_plano.py`) | recorta personagens (Pixelmator), compõe em PIL, codifica com `h264_videotoolbox` | **~3 s** por plano de 8 s a 1920x1080 | **fala que precisa casar**: a boca troca de pose pelo envelope RMS do áudio |
| **A — LTX-2.3 q4** (`ltx-2-mlx`, `--distilled`) | imagem → vídeo | 4 s em **84 s** (832x480, 97 quadros), pico ~20 GB (RSS 11,8 GB) | movimento e ambiente sem fala |
| **A2V** (`ltx-2-mlx a2v`) | áudio + quadro inicial → vídeo | 4 s em 81 s; 6 s ≈ 120 s; 8 s ≈ 160–180 s; pico ~11,5 GB | **padrão de movimento** (preferência do usuário): suave e harmônico; a boca não casa com as sílabas |
| Método C — Blender rigado | não testado (não há modelos 3D rigados) | — | futuro |

Plano de 8 s com fábrica A+B (3 falas, 193 quadros, `trava_final` 0,7): **166 s**, RSS ~11,9 GB, saída
1920x1080 com 8,0 s de vídeo e de áudio. Rosto, roupa, acessórios e cenário ficaram consistentes nos 8 s.
Uma série de 66 planos de 8 s custaria ≈ **3 h só de A2V**.

**Regra de divisão:** conversa que precisa de sincronia → B com poses de boca. Ação/ambiente → A / A2V.
Não usar o modo `AB` em fala (o LTX reinventa a boca).

## O que não funcionou (para não repetir)

- **`lipdub` (DubIt):** mantém muito bem o visual, mas a sincronia labial é fraca (boca aberta/sorrindo em
  todos os quadros) e piorou frente ao A+B sem DubIt. Exige o LoRA gated e vídeo de referência **com áudio**.
- **A2V para sincronia exata:** suave, mas sem casar sílabas. Métrica grosseira (energia de movimento na
  região da boca × envelope): B r≈0,4–0,5; A2V r≈0,0–0,3 (indício, não prova — a região fixa desalinha
  quando os personagens andam).
- **Quadro final travado com força 1,0** deixa o movimento muito calmo (volta à pose inicial); usar 0,7.
- **Codex gera só imagem**, não vídeo.

## Armadilhas de implementação

- O LTX exige **8k+1 quadros**: arredondar para cima e cortar com `-t` (senão o áudio é cortado).
- O quadro final do método B é o índice `fps*dur-1`, não o `n-1` do LTX (extração vazia → "Cannot decode image").
- Ao cortar 16:9 de cenário 4:3 ampliado, usar `y0 = bh - ch` (não uma fração fixa) ou sobra barra preta.
- Concat por cópia de fluxo com **sobra de 1 quadro** na emenda embaralha a abertura: tolerar até 3 quadros
  nas pontas e conferir **por trecho**, não só pelo erro médio global.
- Julgar remontagem por **mediana e p90** do erro por quadro; a média sobe com os quadros isolados dos cortes.
- "Broken pipe" do ffmpeg leitor ao fim da composição é inofensivo.

## Boca, olhos e cabeça por poses (método B)

1. `gerar_bocas.py` pede ao Codex (`-i base.png`, edição nativa de imagem, **só em prancha 3D**) variantes
   "mesmo personagem, mesma pose, mude SÓ a boca/olhos": estados `fechada`, `meia`, `aberta`, `olhos`.
   ~35–40 s por imagem.
2. `pixelmator_lote.py --op removefundo` recorta os estados.
3. `fabrica_plano.py` alinha os sprites por correlação FFT da máscara alfa, converte o envelope RMS do áudio
   em nível de boca por quadro (limiares 0,12 e 0,42, permanência mínima) e pisca olhos pela diferença
   `fechada` × `olhos`.
4. `mover_cabeca` separa corpo e cabeça no pescoço com rampas de alfa complementares e gira ±~1° (mais
   forte falando) com balanço vertical de 1–3 px. Cabeça peluda é o caso difícil.

## Entrega em 1080p

- Padrão de download do gerador em nuvem: **sempre 1080p** (opção "aprimorada" sem custo; 4K custa crédito).
- `refazer_1080p.py` troca cada tomada 720p pelo clipe 1080p correspondente **por casamento de imagem**
  (miniatura do quadro 60, erro < 30), o que dispensa tabela de nomes.
- Registrar, no dia da geração, em qual projeto cada lote foi criado; sem isso não há como voltar a baixar.
- Antes de declarar que um clipe não existe, olhar também o histórico da **sessão do agente** do projeto.

## Preferências de processo

- Fala e nome próprio: conferir de ouvido, não por Whisper.
- Antes de mover uma pasta: `ls -l` para listar symlinks e usar `mv -n` (um `mv` já sobrescreveu scripts por
  links quebrados).
- Backup e checksum antes de reorganizar; nada apagado direto, foto real só via quarentena.
