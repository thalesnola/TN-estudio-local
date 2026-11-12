# Instalações do Estúdio Local — MacBook Pro M5 Pro (macOS arm64)

> Atualizado em 11/11/2026. Fotografia do que está instalado e **por que**. Versões medidas na máquina,
> não copiadas de documentação. Só receita e inventário: nenhum peso de modelo, voz clonada, mídia ou
> credencial entra neste repositório. Para o que **foi testado e o resultado**, ver
> [pipeline-video-local.md](pipeline-video-local.md).

## 1. Homebrew

**Fórmulas** (CLI): `ffmpeg` 9.0.2 (+`ffprobe`), `yt-dlp`, `exiftool`, `tesseract` + `tesseract-lang` (`por`),
`graphviz`, `node`, `uv`, `python@3.12` (base dos venvs) e `python@3.15`, `mlx` + `mlx-c`, `ollama`.

**Casks** (apps): `blender` (5.3.0), `kdenlive`, `krita`, `draw-things`, `drawio`, `db-browser-for-sqlite`,
`visual-studio-code`, `tailscale-app`, `claude`, `codex`, `antigravity` / `antigravity-cli`, `opencode-desktop`.

> Cask e instalador do Homebrew pedem senha: esses passos são do usuário. Fórmula não pede.

## 2. Apps Apple (suíte "Creator Studio", `/Applications`)

| App | Versão | Uso no estúdio |
|---|---|---|
| Pixelmator Pro | 4.4 | remoção de fundo e **Super Resolution** em lote por script (`macos-pessoal/scripts/video/pixelmator_lote.py --op removefundo/superres`) |
| Final Cut Pro | 12.4 | montagem manual quando preciso; não é automatizado |
| Motion | 6.4 | títulos/abertura quando o código não resolve |
| Compressor | 5.4 | transcodificação manual |
| Logic Pro | 13.0 | edição/limpeza de áudio manual |
| Keynote | — | decks com mídia |

Automação desses apps por AppleScript/Atalhos tem armadilhas (permissões de Automação, janela em primeiro
plano). Preferir a rota por código (ffmpeg + VideoToolbox) quando o resultado for equivalente.

**Codificação por hardware:** `h264_videotoolbox` / `hevc_videotoolbox` / ProRes. Plano 1080p de 8 s em ~3 s.

## 3. Ferramentas por `uv tool` (isoladas)

`openai-whisper` (CLI `whisper`), `graphifyy` (grafo de código), `mcp-for-blender`, `volatility3`,
`google-colab-cli`, `colab-mcp`.

## 4. Ambientes Python dedicados (venvs, Python 3.12)

| Venv | Conteúdo | Para quê |
|---|---|---|
| `ltx-venv` | `mlx` 0.32.4, `mlx_audio`, `mlx-vlm`, `mlx-video-with-audio` | caminho legado do LTX-2 (arquivo único); ver armadilha de import abaixo |
| `ltx-2-mlx` (projeto `uv`, instalado com `uv sync --frozen --no-dev`) | pipeline `ltx-2-mlx` (MIT, autor `dgrauet`) | **geração de vídeo atual**: text/image/audio → vídeo, `a2v`, `lipdub`, upscale |
| `imagem-venv` | `torch` 2.15, `transformers` 5.22, `mlx`, `opencv-python`, `pillow`, `safetensors` | geração de imagem local (Z-Image-Turbo) e visão |

- ⚠️ O pacote `mlx-video-with-audio` instala o módulo **`mlx_video`**; `import mlx_video_with_audio` falha.
- ⚠️ O `mlx_video` antigo só lê o layout de arquivo único de `Lightricks/LTX-2`. A variante dividida
  `dgrauet/ltx-2.3-mlx-q4` exige o pipeline `ltx-2-mlx`.
- **Auditar antes de instalar código de terceiros:** o `ltx-2-mlx` foi lido no commit fixado (sem `eval/exec`
  fora de testes, `subprocess` só para ffmpeg/ffprobe, rede só para o Hugging Face, lockfile só PyPI). O
  classificador de permissões do Claude Code pode bloquear a 1ª tentativa; instalar com commit fixado.

## 5. Modelos baixados

Cache do Hugging Face (`~/.cache/huggingface`, ~38 GB no total) e pasta de modelos do estúdio.

| Modelo | Tamanho | Onde | Papel |
|---|---|---|---|
| `dgrauet/ltx-2.3-mlx-q4` | ~22 GB | `~/Estudio/modelos-ltx/` | LTX-2.3 quantizado q4, vídeo no Apple Silicon |
| `mlx-community/gemma-3-12b-it-4bit` | 7,5 GB | cache HF | codificador de texto do LTX (`--gemma`) |
| `Tongyi-MAI/Z-Image-Turbo` | cache parcial | cache HF | imagem local rápida |
| `ltx-2.3-22b-ic-lora-dubit-0.9.safetensors` | 2,47 GB | `~/Estudio/modelos-ltx/` | LoRA do `lipdub` (**repositório gated**) |
| MediaPipe (pose/face) | 33 MB | `modelos/mediapipe` | mocap vídeo → armadura 3D |
| Whisper `base` / `small` / `medium` | 0,14 / 0,46 / 1,4 GB | `~/.cache/whisper` | conferir fala; `small` basta para legenda e checagem |
| Ollama: `qwen3.8:27b`, `qwen3-coder:30b`, `gpt-oss:20b`, `nomic-embed-text` | 18 / 18 / 13 / 0,3 GB | Ollama | agentes locais (ver token-router) |

**Download seletivo do LTX** (o repositório `Lightricks/LTX-2` tem 314 GB com todas as variantes): baixar
só o q4 + o Gemma e **pular** `transformer-dev`, `transformer-distilled` e LoRAs. ~15 min a até 7 GB/min.

**LoRA gated sem token:** com a conta já logada no navegador e a licença aceita, o botão de download da
página `/tree/main` baixa o arquivo direto para `~/Downloads`, sem `hf auth login`. Mover para a pasta de
modelos depois. Nenhum token é gravado em arquivo.

## 6. Vozes

| Fonte | Rede | Notas |
|---|---|---|
| Vozes do sistema pt_BR (`say -v '?' \| grep pt_BR`) | local | Eddy, Felipe, Felipe (Enhanced), Fernanda, Fernanda (Enhanced), Flo, Grandma, Grandpa, Luciana (+Enhanced), Reed, Rocko, Sandy, Shelley. Boas para **rascunho e conferência de ritmo**; não são a voz final |
| Gemini TTS (AI Studio, vozes pré-definidas) | nuvem | elenco final do projeto. Estilo em inglês + "Speak Brazilian Portuguese (pt-BR, Sao Paulo accent, never European Portuguese)". Tratamento: trim de silêncio, `highpass 70`, `loudnorm -19`, 48 kHz mono |
| OpenVoice (clonagem) | local | instalado em `.venv` Python 3.12 com PyTorch/MPS e servidor MCP; **geração parada**: o checkpoint V2 oficial respondeu HTTP 404 em 06/11/2026. Não depende de rede para inferir quando há checkpoint |
| VoiceStudio (CUDA) | local, só Windows | ver `windows/voicestudio/`; não roda no Mac |

- ⚠️ **Átona final em pt-BR:** o "o" final sai "u" no TTS (nome próprio terminado em "o" átono lido "…cu"). Corrigir com grafia fonética
  (`…cô`, com acento) **e conferir de ouvido** — o Whisper lê "certo" mesmo quando a pronúncia está errada.
- ⚠️ Vozes de referência de pessoas reais ficam **fora do git** (pasta ignorada).

## 7. Outras ferramentas de apoio

- **Codex** (CLI, modelo de imagem nativo): edição de imagem a partir de uma base (`codex exec -i base.png`).
  **Só gera/edita imagem, não vídeo.** Usado para variantes de pose de boca/olhos de personagens 3D.
- **Blender 5.3** (Metal) com `mcp-for-blender`; scripts de `blender/` foram escritos para 4.5 — conferir.
- **OpenField** (estúdio open source de vídeo sobre ComfyUI): **não instalado**. README declara macOS
  "untested", só NVIDIA testada, 24 GB de VRAM para vídeo, PyTorch com índice CUDA e ~72 GB de modelos.

## 8. Conferência automática

`python3 setup/conferir.py` (no repositório de trabalho do projeto) relê versões, venvs, modelos por
SHA-256 e links quebrados, e regrava o inventário. Não instala nem apaga nada.
