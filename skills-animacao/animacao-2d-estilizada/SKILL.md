---
name: animacao-2d-estilizada
description: "Criar imagens e animações em pixel art, quadrinhos/cel shading, recorte de papel, anime retrô ou risografia, com receitas de produção e validação usando ferramentas instaladas. Usar quando um desses estilos for solicitado; não para UI nem edição genérica de vídeo."
---

# Animação 2D estilizada

Produza os cinco estilos por construção visual e movimento, sem tratar filtros como substitutos de direção de arte.

## Receitas

Leia apenas o estilo solicitado:

- [pixel art](references/pixel-art.md)
- [comic art](references/comic-art.md)
- [paper cutout](references/paper-cutout.md)
- [retro anime](references/retro-anime.md)
- [risograph](references/risograph.md)

## Execução e integração

1. Identifique entrega (imagem, spritesheet, vídeo ou projeto editável), estilo, referências, duração, resolução, fps de entrega e elementos a preservar. Use os dados do pedido; explicite suposições pequenas sem interromper o trabalho.
2. Leia somente a receita pertinente em `references/`. Defina paleta, escala, câmera e cadência antes de produzir. Fps de entrega e frequência de novas poses são coisas diferentes: 12 poses/s podem ser entregues a 24 ou 30 fps repetindo quadros.
3. Se `$producao-midia-design` estiver instalada, consulte-a para localizar scripts e aplicativos; leia seu inventário local e os documentos do formato usado. Sem essa skill, descubra diretamente os executáveis e conectores disponíveis, sem assumir que existam dependências adicionais. Confira caminhos e recursos em tempo de execução; o inventário histórico não garante disponibilidade atual.
4. Descubra ferramentas MCP por nome/descrição. PhotoCraft serve para imagem; VectorCraft para formas e camadas vetoriais; EffectCraft para composição animada; FilmCraft para montagem. Consulte `command_list` e os schemas antes de comandos; não invente parâmetros nem suponha paridade com Adobe/Fusion. Confirme que o aplicativo realmente exporta o formato pedido antes de montar todo o projeto.
5. Para bitmap gerado ou editado por IA, siga `$imagegen` quando aplicável e autorizado. Para geração local solicitada, descubra `wangp_*`, leia `wangp://guides/agent` usando `mcp_resource`, consulte modelos/templates e disponibilidade local, valide settings com `wangp_validate`, depois submeta e acompanhe o job conforme os schemas. Não baixe pesos grandes automaticamente. Geração neural pode variar contornos e identidade: prefira camadas, rig ou sprites determinísticos quando a continuidade precisar ser exata.
6. HyperFrames é opcional. Use suas skills apenas quando houver necessidade concreta de composição HTML/timeline; leia `$hyperframes:hyperframes` e procure efeitos no registry antes de implementá-los. Não altere configuração global nem reative plugins apenas por esta skill. Não confunda disponibilidade da skill com capacidade de render já testada.
7. Faça primeiro um quadro representativo e um trecho curto que teste o movimento mais difícil, depois produza a entrega solicitada. Preserve fontes e salve em versões. Inspecione início, meio, fim, transições e o movimento em reprodução; corrija defeitos demonstrados. Confirme duração, dimensões, fps e áudio com ffprobe quando disponível. Entregue o arquivo final, fontes editáveis efetivamente produzidas e uma nota breve sobre validação e limites.

## Limites reais

- Localize Blender, FFmpeg e ffprobe no PATH ou na instalação indicada pelo usuário. No PowerShell, use `Get-Command blender,ffmpeg,ffprobe -ErrorAction SilentlyContinue`; Blender portátil pode exigir caminho explícito. A instalação da skill não instala os aplicativos. Não presuma Aseprite, After Effects, Resolve, Dragonframe nem plugins comerciais instalados.
- O material original é referência estética, não inventário de dependências. Para plugin externo indispensável, confira documentação oficial, versão, licença e compatibilidade; se ausente, use alternativa nativa adequada ou relate o bloqueio concreto. Não instale ou compre por inferência.
- Respeite o sigilo do projeto. Dados de caso e derivados ficam na pasta local autorizada; não envie a subagentes, geração remota ou serviços externos. Use a sessão principal ou execução local permitida. Não use a pasta compartilhada de ferramentas como área de caso.
- Preserve emblemas, logotipos e texto fornecidos por composição quando a fidelidade for necessária; não dependa de regeneração por IA para reproduzi-los exatamente.
