# ArtCraft no Codex Windows

Fontes oficiais: [PhotoCraft](https://github.com/storytold/photocraft), [VectorCraft](https://github.com/storytold/vectorcraft), [EffectCraft](https://github.com/storytold/effectcraft), [PdfCraft](https://github.com/storytold/pdfcraft), [LightCraft](https://github.com/storytold/lightcraft), [FilmCraft](https://github.com/storytold/filmcraft), [DesignCraft](https://github.com/storytold/designcraft).

Versões e hashes dos CLIs verificados estão em [versions.json](versions.json). São hashes dos executáveis da instalação testada, não dos ZIPs das releases. Obter os pacotes Windows x64 portáteis nas releases oficiais e conferir sua procedência antes de executar.

Estrutura esperada: `<RAIZ>/ArtCraft/<app>-<versão>-windows-x64-portable/<app>-cli.exe`. Registrar os blocos correspondentes de [mcp.example.toml](../codex/mcp.example.toml) na configuração Codex existente, após ajustar caminhos. Preservar os outros servidores e fazer backup privado antes de editar. Um `.mcp.json` de outro agente não registra MCPs no Codex.

Criar `<RAIZ>/trabalho/entrada`, `saida` e `lightcraft-biblioteca`.

- PhotoCraft, VectorCraft e EffectCraft: leitura em trabalho e escrita em saida, limitadas pelas flags dos CLIs.
- PdfCraft: raiz em trabalho.
- LightCraft: biblioteca própria persistente.
- FilmCraft e DesignCraft: as versões testadas não oferecem o mesmo confinamento de diretórios. Esses limites não substituem uma sandbox do sistema.

O servidor headless não precisa da janela gráfica aberta. O modo bridge/control é outra configuração e não foi utilizado nos testes registrados.
