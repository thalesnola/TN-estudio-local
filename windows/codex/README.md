# Codex: MCPs, plugins e skills

O [mcp.example.toml](mcp.example.toml) contém sete ArtCraft, VoiceStudio e WanGP. É um exemplo para mesclar em `~/.codex/config.toml`, nunca uma substituição da configuração inteira. Não copiar tokens, envs privados ou sessões entre máquinas. Reiniciar o Codex ou abrir novo chat depois de registrar os servidores.

## Hyperframes e Higgsfield

Hyperframes foi instalado pelo gerenciador nativo do Codex na revisão abaixo:

```powershell
codex plugin marketplace add heygen-com/hyperframes --ref 9fa02badfc20319a292573333c72da715c263bcf --sparse skills --sparse assets --sparse .codex-plugin --sparse .claude-plugin --json
codex plugin add hyperframes@hyperframes --json
```

O plugin reportou 0.8.230. Oito skills: figma, hyperframes, hyperframes-cli, hyperframes-registry, media-use, remotion-to-hyperframes, reverse-any-video e slideshow. A instalação do plugin não garante CLI, navegador de renderização ou dependências de um projeto. Essas etapas não foram validadas aqui.

Higgsfield CLI oficial: [higgsfield-ai/cli](https://github.com/higgsfield-ai/cli). Versão testada: `@higgsfield/cli@1.2.2`. Antes de instalar, baixar com `npm.cmd pack @higgsfield/cli@1.2.2 --ignore-scripts` e revisar os scripts. O instalador desta versão baixa um binário da release oficial e confere SHA-256. Depois da revisão: `npm.cmd install --global @higgsfield/cli@1.2.2`, seguido de `higgsfield.cmd --version`. Autenticação é individual; não copiar o login da máquina de origem.

Skills Higgsfield preservadas na instalação: brandkit, generate, marketplace-cards, product-photoshoot, soul-id, video-explainer, websites e youtube-thumbnail (todas com prefixo `higgsfield-`). Não foram executadas gerações remotas.

Os pacotes de mídia opcionais foram mantidos com skills desabilitadas por padrão mediante entradas `[[skills.config]]`, com `path` real de cada skill e `enabled = false`. Instalar o plugin sozinho não cria essas desativações. Rever esses caminhos após atualizar a versão.

Skills de mídia/design adicionais: `producao-midia-design`, `apple-hig-designer`, `redesign-existing-projects`. A integração de métodos e scripts está em [producao-midia-design](https://github.com/thalesnola/producao-midia-design). Revisar cada fonte antes de instalar; popularidade não substitui revisão. Não se copiam instruções de acervo ou dados de caso para este repositório.

## Animação estilizada

As skills próprias `animacao-2d-estilizada` e `animacao-3d-estilizada` estão versionadas em [skills-animacao](../skills-animacao/README.md), com instalação para Codex e dez receitas. A integração aproveita as ferramentas existentes sem reativar plugins opcionais.
