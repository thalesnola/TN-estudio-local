# Inventário verificado — Codex Windows, 06/11/2026

Este é um registro da instalação verificada, não uma lista das versões mais recentes. Reproduzir exige ajustar caminhos e conferir novamente a compatibilidade.

| Componente | Versão | Evidência nesta instalação |
|---|---|---|
| PhotoCraft | 0.8.2 | MCP: criar documento e exportar PNG |
| VectorCraft | 0.10.0 | MCP: desenhar forma e exportar PNG/PDF |
| EffectCraft | 0.9.2 | MCP: criar composição e renderizar quadro |
| PdfCraft | 0.7.1 | MCP: abrir PDF, ler metadados e renderizar página |
| LightCraft | 0.7.1 | MCP: importar imagem e renderizar foto |
| FilmCraft | 0.7.2 | MCP: importar mídia e inspecionar projeto; exportação de vídeo não testada |
| DesignCraft | 0.7.1 | MCP: criar documento e exportar PNG |
| Blender | 4.5.10 LTS | Render CPU 64×64 e exportação GLB de cena sintética |
| Kdenlive | 26.08.2 na origem | Programa copiado; edição/exportação pela UI não testadas |
| FFmpeg | 9.0.1 Essentials | Composição real de vídeo sintético concluída |
| VoiceStudio | 0.5.7 | MCP, saúde, interface HTTP e síntese local em português |
| PyTorch do VoiceStudio | 2.8.0+cu128 | CUDA reconhecida em RTX 2000 Ada, 16 GB VRAM |
| Hyperframes | 0.8.230 | Plugin instalado; não foi renderizado vídeo com ele nesta validação |
| Higgsfield CLI | 1.2.2 | Comando de versão; geração remota e autenticação não testadas |
| WanGP | MCP API 2.1 | Servidor configurado no Codex; instalação e lançador já documentados em wangp/ |

Os sete ArtCraft inicializaram e enumeraram 160 ferramentas MCP. Os sete CLIs tiveram seus hashes comparados à instalação de origem e assinaturas Authenticode válidas. As operações usaram somente arquivos sintéticos. Três testes adicionais do conjunto portável de mídia passaram: identificadores, composição de vídeo preservando a fonte e recusando sobrescrita, e preparação de imagem/mapas de altura.

VoiceStudio: `generate_speech` pelo MCP retornou HTTP 200, WAV mono de 7,927 s a 24 kHz, com tempo de geração informado de 6,89 s. Pesos carregados em CUDA com execução offline. Isso comprova execução e integridade do WAV, sem avaliação independente de pronúncia. A amostra e os registros de aceite ficam apenas na máquina local.

O PyTorch 2.8 do VoiceStudio pertence ao seu ambiente isolado. O WanGP usa outro ambiente e outra pilha, conforme seu INSTALL.md. Não compartilhar nem atualizar os dois ambientes como se fossem um só.

Skills de mídia/design instaladas: producao-midia-design, apple-hig-designer e redesign-existing-projects. Os oito pacotes Higgsfield e oito skills Hyperframes foram mantidos opcionais, desabilitados por padrão na configuração realizada. Skills de terceiros não são vendorizadas aqui.

Os scripts históricos de produção 3D dependem de mestres, texturas e assets externos. A instalação de Blender não valida esses renders nem fornece os assets.

## Contas de IA generativa (06/11/2026)

Google Flow (Nano Banana 2, Veo 3.1): medido em 28/09–15/10/2026; Omni 1.1 Flash: 28–29/09/2026. Omni 1.2 Flash e ChatGPT Images 2.6: **apenas anúncio de 06/11/2026, sem teste nestas contas**. Detalhes em [generativo/](../generativo/README.md).

## Skills de animação de terceiros (06/11/2026)

Anidoodle (`4ae27d2`), claude-drawing (`4886ed8`), whiteboard-video (`75c7825`), javascript-animation e soundtrack (`f7d0882`): auditadas por leitura e instaladas em `~/.claude/skills`. Sem geração executada. Detalhes em [skills-animacao/](../skills-animacao/README.md).

Hypit (`2d31e88`, v0.3.2): auditada e instalada **somente a skill**; CLI, ffmpeg, uv e modelos não instalados. Detalhes em [hypit/](../hypit/README.md).

Rhubarb Lip Sync 1.14.0: binário auditado e instalado como skill própria `rhubarb-lipsync`; testado em pt-BR com voz sintética, sem avaliação com voz real. Detalhes em [rhubarb-lipsync/](../rhubarb-lipsync/README.md).

Som (06/11/2026): `openverse-sfx` (`caac7cd`, corrigida) e `earshot` v0.4.1 (`4ac3d2a`, torch CPU, modelos em cache próprio) instaladas; `real-sound` não instalada. Smoke test: `earshot doctor` saudável, render/check/measure/realness offline; busca Openverse real, nenhum áudio baixado. Detalhes em [sons/](../sons/README.md).
