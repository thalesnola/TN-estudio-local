# Mídia pessoal nola-macm5

Variante Apple Silicon, independente da configuração profissional. O `.mcp.json`, `scripts/` e métodos legados na raiz do repositório permanecem preservados. Trabalhar no workspace pessoal `~/nola-macm5/midia`: seu `.mcp.json` gerado contém somente as ferramentas pessoais. Não usar o manifesto Windows da raiz neste Mac.

## ArtCraft nativo

| CLI | Versão fixada | Operação real conferida |
|---|---|---|
| PhotoCraft | 0.20.2 | Criar e exportar PNG |
| VectorCraft | 0.21.1 | Desenhar forma e exportar PNG/PDF |
| EffectCraft | 0.21.1 | Criar composição e renderizar quadro PNG |
| PdfCraft | 0.18.2 | Abrir PDF, ler metadados e renderizar página |
| LightCraft | 0.18.1 | Importar PNG e renderizar imagem |
| FilmCraft | 0.17.1 | Importar mídia e inspecionar projeto |
| DesignCraft | 0.17.2 | Criar documento e exportar PNG |

Os CLIs são distribuições oficiais macOS universal com slice arm64, SHA-256 fixado em `artcraft.lock.json`, checksum publicado e assinatura Apple verificados. A instalação é headless (CLI/MCP); não instala os aplicativos gráficos. Fontes: [releases oficiais](https://github.com/storytold/photocraft/releases), [MCP PhotoCraft](https://github.com/storytold/photocraft/blob/main/docs/mcp.md), [FilmCraft](https://github.com/storytold/filmcraft).

```sh
# Da raiz do repositório, conferir plano e depois aplicar:
python3 macos-pessoal/artcraft.py
python3 macos-pessoal/artcraft.py --apply --register
```

Requer macOS arm64, Python 3.11+, acesso às releases GitHub e Codex CLI para `--register`. Não executar os instaladores Windows. As versões permanecem fixadas; atualizar o lock exige conferir assets, hashes, opções MCP e repetir os testes.

- Binários: `~/Applications/nola-macm5/ArtCraft/<app>/<versão>/`.
- MCPs Codex: nomes `nola-macm5-<app>`; outros servidores são preservados.
- Manifesto gerado: `~/.config/nola-macm5/artcraft/mcp.json`, também no workspace pessoal.
- Área pessoal: `~/nola-macm5/midia/{entrada,saida,biblioteca}`.
- Configurações substituídas têm backup em `~/.config/nola-macm5/artcraft/backups/`.

PhotoCraft, VectorCraft, EffectCraft, PdfCraft e DesignCraft leem no workspace e escrevem em `saida/` por flags do próprio CLI. LightCraft usa biblioteca pessoal persistente; LightCraft e FilmCraft não oferecem os mesmos limites de diretório nesta configuração. Isso não é sandbox do sistema.

## Scripts e ambiente Python

Os scripts pessoais e a tabela de portabilidade estão em [SCRIPTS.md](SCRIPTS.md). Não reaproveitar nomes legados em novos arquivos, títulos ou prompts; usar `nola-macm5`. Assets externos precisam ser fornecidos explicitamente; a instalação não inventa nem copia arquivos de produção antigos.

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r macos-pessoal/requirements.lock
.venv/bin/python macos-pessoal/scripts/video/aplicar_emblema.py --help
```

Blender e FFmpeg precisam estar no PATH. A seleção da GPU e as limitações observadas são documentadas em SCRIPTS.md. A adaptação pessoal não muda o ambiente das outras estações.

## Validação

```sh
python3 -m unittest discover -s macos-pessoal -p 'test_artcraft.py' -v
.venv/bin/python macos-pessoal/inspect_mcp.py
.venv/bin/python macos-pessoal/smoke_artcraft.py
.venv/bin/python -m unittest discover -s macos-pessoal/tests -v
```

`inspect_mcp.py` inicializa os sete servidores e enumera as ferramentas. `smoke_artcraft.py` executa operações reais com material sintético, cria uma biblioteca LightCraft isolada para o teste e salva resultados em `saida/nola-macm5-smoke-*/`. FilmCraft foi validado para importação/inspeção; esse teste não comprova exportação de vídeo pela aplicação. Os renders dos arquivos de produção continuam condicionados aos assets fornecidos.

Os arquivos gerados, bibliotecas, downloads, relatórios e mídias ficam fora deste repositório. Abrir um novo chat do Codex para descobrir os novos MCPs registrados.
