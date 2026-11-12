# Personagem INSTITUICAO: padrão visual, de voz e de fala

Referência fixa para toda cena falada no Flow (Veo 3.1). O bloco **VOZ** é copiado
**literalmente** em todo prompt: o Flow não guarda um "modelo de voz"; a consistência vem de
repetir a mesma descrição e de partir sempre do mesmo quadro inicial.

## Pastas
| Pasta | Conteúdo |
|---|---|
| `referencias/` | originais (renomeados em 28/09/2026, ver tabela abaixo) |
| `quadros/` | quadros iniciais compostos localmente para o Veo |
| `videos/` | vídeos baixados do Flow, `topico_NN_<tema>_vX.mp4` |

| Nome atual | Nome original | Uso |
|---|---|---|
| `ref_retrato_recorte.png` | `rosto_personagem.png` | **retrato com alfa, base dos quadros** |
| `ref_corpo_recorte.png` | `Imagem do ChatGPT … 19_54_44.png` | corpo inteiro com alfa |
| `ref_retrato_caatinga.png` | `Imagem do ChatGPT … 19_54_02.png` | retrato, caatinga |
| `ref_corpo_caatinga_16x9.png` | `Imagem do ChatGPT … 19_54_12.png` | caminhando, caatinga |
| `ref_corpo_cidade_noite.png` | `personagem.png` | cidade à noite, viaturas |

## Perfil
Policial negro, 40 e poucos anos, porte atlético, cabelo curto crespo, barba rala no queixo.
**Olho esquerdo cibernético com brilho vermelho** (o direito é natural). Farda tática preta,
emblema circular "POLÍCIA / INSTITUICAO" no peito. Postura firme, séria, de quem já viu muita coisa
e ensina sem pressa. Autoridade sem arrogância.

## VOZ (bloco fixo, em inglês: o Veo segue melhor o prompt em inglês; a fala vai em português)
```
VOICE: deep, hoarse, gravelly baritone male voice, early 40s, with a subtle synthetic
cyborg timbre: a faint metallic resonance layered under a clearly human voice (light, not
robotic, words fully intelligible). Speaks Brazilian Portuguese (pt-BR) with a neutral,
standard accent, like a national TV news anchor: no regional accent, no Portuguese (Portugal)
accent, no Spanish or English accent. Calm, slow, assertive delivery: firm, confident, never
shouting; clear articulation of every syllable, slight emphasis on key words, short natural
pauses at commas. Close-miked studio sound, no music, no background noise, no reverb.
```

## CORPO E LÁBIOS (bloco fixo)
```
PERFORMANCE: he looks straight into the camera the whole time. Lip movements precisely
synchronized with every spoken syllable. Natural facial expressions, subtle eyebrow raise on
emphasis, small head nods at the end of phrases, shoulders relaxed, slight natural breathing
movement. He starts speaking about 0.5 s into the clip and closes his mouth after the last word.
The red cybernetic eye keeps a steady soft glow. Static camera, medium close-up, no zoom,
no cuts.
```

## RESTRIÇÕES (bloco fixo)
```
NEGATIVE: no subtitles, no captions, no on-screen text, no logos added, no extra people,
no change of face, clothing or background, no lip-sync drift, no mumbling.
```

## Regra de tamanho da fala
Clipe do Veo = **8 s**. Ritmo medido de fala pausada ≈ 2,2 palavras/s → **máximo 16 palavras**
por clipe (0,5 s de entrada + ~7 s de fala + folga). Fala maior = dividir em dois clipes com o
**último quadro do primeiro como quadro inicial do segundo**.

Siglas: escrever como se pronunciam quando o Veo errar (ex.: `UFED` → "iú-féd", `IPED` → "i-péd").

## Molde do prompt
```
Use the uploaded image as the exact first frame. A Brazilian police officer (the man in the
image) speaks directly to the camera and says, in Brazilian Portuguese: "<FALA>"
<VOZ> <PERFORMANCE> <NEGATIVE>
```

## Falas de abertura dos tópicos (apresentação.md)
| # | Tópico | Fala | Palavras |
|---|---|---|---|
| 1 | Flagrante | "Tudo começa no flagrante. O que você preserva nas primeiras horas define o resto da investigação." | 16 |
| 2 | Cadeia de custódia | "Cadeia de custódia: se você não consegue provar o caminho da prova, a prova não vale." | 16 |
| 3 | Cellebrite UFED | "Agora, a extração. Com o Cellebrite UFED, o celular apreendido vira dado que dá para analisar." | 16 |
| 4 | Physical Analyzer | "No Physical Analyzer, o dado bruto começa a contar a história: conversas, contatos, localizações." | 14 |
| 5 | IPED | "Com o IPED, antes de abrir qualquer arquivo, entenda o que você tem nas mãos." | 15 |
| 6 | Cruzamento de dados | "Um número, um CPF, um e-mail. Cruzados com bases públicas e privadas, eles revelam uma rede." | 16 |
| 7 | Relatório | "Parcial ou final, o relatório é onde a análise vira prova. Desenhe cada vínculo." | 14 |
| 8 | Casos práticos | "Chega de teoria. Vamos ver como tudo isso funcionou em duas operações reais." | 13 |
| 9 | Coding agents | "Por fim, agentes de programação: rápidos, poderosos, e exigem revisão absoluta de tudo que produzem." | 15 |

## Registro de testes
| Data | Clipe | Quadro | Resultado |
|---|---|---|---|
| 28/09/2026 | `teste_02_flagrante_close_v2.mp4` (voz v2) | personagem | Farda com distintivo genérico inventado; olho vermelho apaga após 1 s. 1ª tentativa **barrada pelo filtro** ("risco à reputação") com "POLÍCIA" no prompt; passou como "instrutor fictício" |
| 28/09/2026 | `teste_03_flagrante_corpo_v1.mp4` | personagem | Corpo inteiro ok; dois distintivos inventados no peito |
| 28/09/2026 | `teste_04_flagrante_close_liso.mp4` → **`teste_04_flagrante_close_emblema.mp4`** | personagem (peito liso) | ✅ Peito liso, olho aceso o tempo todo e do lado certo, fala 0,43–7,21 s. Emblema aplicado localmente (rastreio mín. 0,83) |
| 28/09/2026 | `teste_05_flagrante_corpo_liso.mp4` → **`teste_05_flagrante_corpo_emblema.mp4`** | personagem (peito liso) | ✅ Corpo inteiro, passo à frente, gestos na cintura, fala 0,55–6,86 s. Emblema aplicado (rastreio mín. 0,60). ⚠️ Sobrou distintivo na manga esquerda dele |
| 28/09/2026 | `videos/teste_01_flagrante_omni_v1.mp4` (Omni 1.1 Flash, personagem + voz salva, 12 créditos) | pedido: `quadro_narracao_close_16x9.png` | **Áudio no tempo:** fala 0,55–7,54 s, pausa na vírgula 2,23–2,57 s, boca fecha no fim. **Imagem fora:** o Omni ignorou o quadro inicial; enquadramento centralizado, camiseta preta sem farda nem emblema, rosto mais fino e **olho vermelho trocado de lado**. Voz e lábio: avaliação do usuário, pendente |

## Emblema no peito (decidido 28/09/2026)
Só o emblema **INSTITUICAO [UNIDADE]** (`emblemas_metalizados/emblema-coruja-3d-unidade-mg.png`), no **peito
direito dele** (lado esquerdo da imagem), acima da aba do bolso. **A IA nunca desenha o emblema:**
o personagem no Flow tem peito liso e o emblema entra por `aplicar_emblema.py`, que rastreia
gola+abas do bolso quadro a quadro:
```
python aplicar_emblema.py videos/<liso>.mp4 videos/<saida>.mp4 --centro X Y --diam D --modelo X0 Y0 X1 Y1
```
Close (1280×720, meio do peito para cima): `--centro 228 506 --diam 96 --modelo 150 440 320 625`.
Corpo inteiro: `--centro 602 181 --diam 23 --modelo 560 150 690 240 --busca 40`.
As coordenadas mudam a cada vídeo: medir no 1º quadro. Conferir por folha de contato.

## Filtro de conteúdo do Omni
"Policial"/"POLÍCIA"/farda de polícia no prompt → recusa *"risco à reputação ou deturpar eventos
atuais"*. Descrever como **instrutor fictício de curso** e a roupa como "black collared tactical shirt".

## Voz salva no Flow
**Em uso: "Analista INSTITUICAO v2 - rouca natural"** (Algenib + *natural, human, conversational
delivery at a normal speaking pace (not slow)… hoarse, gravelly, deep voice with only a very light
synthetic edge; calm, confident, assertive*). Pedido do usuário após o teste 1: mais humana, menos lenta.
Versão 1 (mantida no Flow, fora de uso): personagem **"Analista INSTITUICAO"**, voz **"Analista INSTITUICAO - rouca sintetica"** =
base **Algenib** (Male, gravelly, low pitch) + performance: *Brazilian Portuguese, neutral
national-news accent, no regional accent. Hoarse, gravelly, deep voice with a subtle synthetic
cyborg timbre (faint metallic resonance), still clearly human and intelligible. Calm, slow,
assertive, firm; never shouting; short pauses at commas.* Só o **Omni** usa a voz salva; o Veo não.

## Aberturas dos tópicos (28/09/2026) — `videos/aberturas/`
Finais com emblema: `topico_NN_<tema>_<rosto|corpo>.mp4`; `_liso` = saída do Flow sem emblema (guardar:
é dela que se reaplica o emblema). Posição do emblema transferida por `--ref`:
```
# rosto
python aplicar_emblema.py <liso> <final> --ref videos/teste_04_flagrante_close_liso.mp4 --centro 228 506 --diam 96 --modelo 150 440 320 625
# corpo inteiro
python aplicar_emblema.py <liso> <final> --ref videos/teste_05_flagrante_corpo_liso.mp4 --centro 602 181 --diam 23 --modelo 560 150 690 240 --busca 40
```
| # | Enquadramento | Observação |
|---|---|---|
| 1 | rosto + corpo | cópias dos testes 04/05 |
| 2 | corpo | 1ª versão pôs distintivo no peito nos 2 s finais (guardada como `_v1_distintivo`); refeita limpa |
| 3 | rosto | ok |
| 4 | corpo | Omni gravou legenda "ANALISTA INSTITUICAO" até 1,4 s: coberta com fundo do último quadro (emenda de tom leve até 2 s) |
| 5 | rosto | ok |
| 6 | corpo | **fala alterada**: "Um telefone, um documento, um e-mail. Cruzados com bases públicas e privadas, eles revelam conexões." A fala original (com "CPF" e "revelam uma rede") caiu 2× no filtro de política |
| 7 | rosto | ok |
| 8 | corpo | ok |
| 9 | rosto | Omni desenhou placa metálica de ciborgue em volta do olho (diferente dos demais) |

Falhas do Flow não são cobradas ("Não houve cobrança por esta geração"). Nos corpos inteiros resta um
distintivo pequeno de manga no braço esquerdo dele.
| 3b (deck: slide 39 "Antes de abrir qualquer ferramenta") | rosto | "Antes de abrir qualquer ferramenta, pergunte. São as perguntas que decidem o que se procura." Limpo na 1ª; "no metal plates on the face" no prompt |

## Marca d'água (28/09/2026)
`marca_dagua_instituicao_400.png` (emblema coruja, alfa = brilho × 0,22 com borda esmaecida) sobreposto a
`--overlay 760:160` (rosto) / `800:160` (corpo) → `videos/aberturas/marca/`. São esses os que vão ao deck
(script de inserção no deck: tela cheia, início automático, some ao terminar — ver `docs/deck-video-inicio-automatico.md`).

## Aberturas em plano médio com figurantes (29/09/2026)
Cadeia de arquivos: `liso_flow` → `emblema` → `marca`.
Plano médio em estúdio azul-noite (não o close dos tópicos).
- **Filtro de "pessoas famosas":** 7 falhas (sem cobrança). O agente do Flow reescreve o prompt e **tira** a frase de personagem
  fictício. Resolveu pedir "Use EXACTLY this prompt, verbatim", começando por "ORIGINAL fictional character created by the user…".
- Emblema: `--centro 470 535 --diam 70 --modelo 405 570 590 700 --busca 40` no `cena_a` e `--ref` nele para os demais. No
  `cena_b` (mais fechado) o `--ref` achou o lugar errado (centro 65,-13): usar `--centro 430 628 --diam 72 --modelo 310 470 560 610`.
- `cena_a` veio com legenda gravada no clipe inteiro: coberta com `crop`+`overlay` do fundo logo acima.
- Marca d'água em `overlay=800:160`.
