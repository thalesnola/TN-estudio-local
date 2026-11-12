# Windows (CUDA / NVIDIA)

Tudo aqui pressupõe Windows 11, PowerShell, GPU NVIDIA e caminhos `C:\...`. **Não rodar no Mac.**
O equivalente macOS está em [../macos-pessoal/](../macos-pessoal/README.md).

| Pasta / arquivo | Papel |
|---|---|
| `.mcp.json` | sobe os sete ArtCraft (`*-cli.exe mcp`) em modo headless. Copiar para a raiz do projeto de trabalho no Windows; ajustar `<USUARIO>` |
| `artcraft/` | versões e README dos apps portáteis (`C:\Apps\<app>-<versão>-windows-x64-portable`) |
| `voicestudio/` | backend de voz neural local (CUDA, OmniVoice) |
| `wangp/` | WanGP: geração de vídeo em GPU NVIDIA, lançador `.bat` e `liberar-gpu.ps1` |
| `codex/` | exemplo de MCP para `~/.codex/config.toml` (ArtCraft, VoiceStudio, WanGP) |
| `scripts/3d/` | emblemas 3D no Blender com Cycles/CUDA e suas cadeias de render |
| `scripts/video/aplicar_emblema.py` | rastreio e colagem do emblema (caminhos Windows) |

Documentos de método (`../docs/`, `../metodologia/`) valem nas duas plataformas.
