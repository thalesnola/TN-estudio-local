# Google Flow: Nano Banana 2 e Veo 3.1

Medido em conta Google AI Pro, Windows, 28/09–15/10/2026. Endereço: `flow.google.com`. Um projeto novo abre num **chat de agente**; a automação passa por ele.

## Configuração
- "Confirmar antes de gerar": **Sempre**.
- Padrão de imagem: 16:9, x2, Nano Banana 2.
- ⚠️ **O padrão de vídeo é o Omni, não o Veo.** Trocar à mão para Veo 3.1 quando o roteiro pedir Veo.

## Custos e tempos
- Imagem: sem confirmação, ~25–40 s.
- Veo 3.1 Fast, 8 s: 20 créditos, pede aprovação, 1–2 min de fila.
- Imagem → vídeo: "use a primeira imagem desta sessão como quadro inicial".
- Falha não é cobrada.

## Armadilhas
- Mensagem enviada com o agente respondendo é **descartada em silêncio**. Esperar ~45 s entre envios e contar os blocos na grade depois de cada lote.
- O agente às vezes anuncia "vou gerar" e não gera nem pede aprovação: responder "yes, go ahead".
- "Algo deu errado" pode ser falha só do texto da resposta; a mídia pode ter sido gerada. Conferir a grade antes de refazer.
- Prompt literal: "Use EXACTLY this prompt, verbatim, without rewriting or shortening it". Sem isso o agente reescreve e remove proteções contra filtro.
- O agente renomeia blocos de lote, às vezes abreviando: usar o `aria-label` real.
- O layout muda com a largura do painel (< ~900 px vira coluna única e o chat some).

## Qualidade
- O Veo foge do prompt (objeto pegou fogo, ambiente trocado de época). Reenviar com **restrição negativa** e **imagem do projeto como primeiro quadro**.
- Quadro final exato: usar o modo de quadros do editor de **Cenas**, não o chat (o chat pegou a imagem errada e não terminou no quadro pedido).
- Marca/emblema: pedir só a **placa de fundo** ("no logos, no emblems, no text") e compor o original por cima, localmente.

## Download
- Vídeo: 270p GIF · 720p original · 1080p aprimorado · 4K pede upgrade. Imagem: 1K original · 2K aprimorada (sem custo no Pro) · 4K pede upgrade.
- O arquivo pode chegar como `<uuid>.tmp` (completo; conferir o magic number) ou como `<Titulo>_<AAAAMMDDhhmmss>.mp4`, e a pasta de destino varia. Mover por **marcador de tempo**, nunca "o item mais novo". Download repetido gera cópia idêntica: conferir hash.
- Imagem por DOM: `fetch` da URL trocando o sufixo `=s…-rw` por `=s0` (com credenciais) → blob → `<a download>`. Um arquivo por chamada.
- A ordem da coleção não é cronológica: casar nome × conteúdo por folha de contato ou por transcrição do áudio.

## Upload
O botão "Enviar" abre o seletor do sistema; não há `input[type=file]` acessível e as vias automáticas foram barradas. **Quem sobe o arquivo é o usuário.** Imagem enviada volta como JPG recodificado (perde alfa): usar o original do disco.

## Personagens
Seção **Personagens**: retrato + voz (Gemini TTS, com campo de performance). Fala e voz em [omni.md](omni.md).

## Filtros observados
Recusas por "pessoas famosas", "política" e reputação de instituição disparam por **texto** (falso positivo com personagem fictício). Reescrever a ideia da frase resolve; insistir não. Vestimenta mínima em vídeo é barrada com frequência, mesmo instrucional; imagem passa mais.
