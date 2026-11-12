# Geração generativa: três ferramentas, um roteiro

Guia de uso das ferramentas de IA generativa (contas Google e ChatGPT; o Omni é acessado pelo Flow, e pelo app e API quando disponível) de imagem e vídeo, e de qual usar em cada etapa. Somente método e lições medidas: sem prompts, mídias, personagens, credenciais ou dados de caso.

| Ferramenta | Papel | Guia |
|---|---|---|
| **Google Flow** | Imagem (Nano Banana 2) e vídeo (Veo 3.1; Fast medido), edição por cenas, personagens | [flow-veo.md](flow-veo.md) |
| **Omni** (Gemini Omni Flash) | Vídeo com voz e sincronia labial (8 s medido na 1.1; 15 s, mais referência e edição por pedido são anúncio da 1.2, a validar) | [omni.md](omni.md) |
| **ChatGPT** (Images 2.6) | Peças gráficas, consistência de layout, edição por máscara, GIF e SVG (tudo anúncio, não medido) | [chatgpt-images.md](chatgpt-images.md) |

## Quem faz o quê

| Preciso de… | Use | Por quê |
|---|---|---|
| Vídeo sem fala, cinematográfico, 8 s | Flow › Veo 3.1 | Controle de quadro inicial/final no editor de Cenas |
| Personagem falando, voz fixa, lábio sincronizado | Omni | Único que usa a voz salva do personagem |
| Corrigir um vídeo sem recomeçar | Omni | Anúncio da 1.2: aceita pedido de mudança sobre o clipe (a validar) |
| Imagem de produto, marca, layout, texto (conferir) | ChatGPT Images | Anúncio: consistência de produto, marca e layout entre peças; conferir texto e logo |
| Corrigir só uma região da imagem | ChatGPT Images (máscara) | Anúncio: marca a área e altera apenas ali |
| Vetor (SVG) ou GIF simples | ChatGPT Images | Anúncio: exporta nos dois formatos em alguns fluxos |
| Imagem-base ou quadro inicial para vídeo | Flow › Nano Banana 2 ou ChatGPT | Quadro inicial vale no Veo (Cenas); no Omni 1.1 é ignorado (1.2 a validar). Upload manual |
| Emblema, brasão ou logotipo exato | **Nenhum modelo** | Compor localmente (PIL/ffmpeg) sobre a placa gerada |

## Regras comuns às três contas

1. **Sigilo.** Todo prompt e todo arquivo enviado sai da máquina e fica na conta. Mandar só texto genérico e higienizado; nunca arquivo, print, rosto, documento ou figura de caso.
2. **Crédito.** Vídeo gasta; no Flow a imagem não pede confirmação (medido; ChatGPT não medido). Manter "confirmar antes de gerar" ligado e não marcar "sempre aprovar" sem decisão do dono da conta. Falha de geração no Flow não é cobrada (medido): conferir o aviso antes de refazer.
3. **Conferir antes de entregar.** O modelo foge do prompt: olhar um quadro do **meio** e do **fim** de cada vídeo (folha de contato), não só o primeiro.
4. **Restrição negativa explícita** ("no text on clothing", "no logos") corrigiu os desvios medidos no Flow/Veo (não validado no ChatGPT); reenviar com ela e com uma imagem de referência.
5. **Identidade institucional é montada fora do modelo.** Brasão, logotipo e texto miúdo saem errados ou redesenhados; gerar só a placa de fundo e compor o original por cima.
6. **Saída é rascunho** até passar pela conferência; registrar de qual conta e modelo veio cada peça.

## Divisão de trabalho entre agentes

O orquestrador (Claude) planeja, escreve os prompts e confere; o braçal é terceirizado:

| Etapa | Quem |
|---|---|
| Plano, roteiro de cenas, escolha da conta, redação dos prompts | Orquestrador |
| Operação do navegador (enviar, aprovar, baixar) | Subagente com navegador, uma conta por vez, ~45 s entre envios |
| Folha de contato, hash, nome × conteúdo, transcrição do áudio | Subagente de leitura ou script local |
| Composição local de logotipo e legenda (PIL/ffmpeg) | Executor |
| Revisão final do lote contra o roteiro | Revisor |

A sessão logada é do usuário; subagentes não recebem credenciais. O upload de arquivo ao Flow é feito pelo usuário (o seletor do sistema não é automatizável).

## Origem das informações

Notas "medido": Flow/Veo em 28/09–15/10/2026; Omni 1.1 em 28–29/09/2026. Os dados de **Omni 1.2 Flash** e **ChatGPT Images 2.6** vêm do anúncio de 06/11/2026 e **não foram medidos** nestas contas: confirmar disponibilidade, limites e custo antes de planejar um lote.
