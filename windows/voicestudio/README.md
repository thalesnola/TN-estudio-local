# VoiceStudio local e MCP Codex

Configuração validada: VoiceStudio 0.5.7, Python 3.12, PyTorch 2.8.0+cu128, RTX 2000 Ada com 16 GB. Backend limitado a `127.0.0.1:3917`; nove ferramentas MCP. Fontes: [VoiceStudio](https://github.com/debpalash/VoiceStudio), [OmniVoice](https://huggingface.co/k2-fsa/OmniVoice).

## Estrutura e instalação

Manter o programa oficial fora do Git, em `<RAIZ>/VoiceStudio/`. A configuração testada contém `resources/pyproject.toml`, `uv.lock`, `backend/` e `omnivoice/`. Conferir a versão e os arquivos; não substituir o lockfile por uma resolução genérica de dependências.

```powershell
$mediaRoot = 'C:/Tools/audio-visual' # ajustar
$resourceDir = Join-Path $mediaRoot 'VoiceStudio/resources'
uv sync --project $resourceDir --frozen --no-dev --python 3.12
```

O lockfile da versão testada seleciona CUDA por padrão. Esta receita pode baixar vários GB de dependências e não foi validada para outra GPU/CPU. Não misturar com o ambiente do WanGP.

Criar `<RAIZ>/voice-runtime` e copiar para lá `launcher.py` e `environment.example.json` (renomeado para `environment.json`). Ajustar todos os caminhos do JSON, mantendo a porta 3917. O inicializador resolve a instalação em relação à sua própria pasta: precisa ficar exatamente em `<RAIZ>/voice-runtime/launcher.py`. Criar também `trabalho/voz` e `trabalho/voice-backend`.

## Modelo e licenças

[model.lock.json](model.lock.json) fixa a revisão e os SHA-256 dos dois arquivos de pesos. O download autorizado nesta instalação foi de cerca de 3,3 GB, incluindo tokenizador. Não baixar modelos grandes automaticamente em outra máquina.

Os nove arquivos necessários são: `config.json`, `model.safetensors`, `tokenizer.json`, `tokenizer_config.json`, `chat_template.jinja`, e `audio_tokenizer/{config.json,preprocessor_config.json,model.safetensors,LICENSE}`. Usar `huggingface_hub.snapshot_download` com `repo_id="k2-fsa/OmniVoice"`, a revisão do lock, `allow_patterns` limitado a esses arquivos e `cache_dir=<RAIZ>/voice-runtime/models`. Conferir os hashes e gravar em `OMNIVOICE_MODEL` o caminho do snapshot retornado.

O exemplo já aponta para esse snapshot e ativa `HF_HUB_OFFLINE=1` e `TRANSFORMERS_OFFLINE=1`. Desse modo, a inferência não baixa modelos adicionais. Não ativar o backend antes de concluir o download e ajustar os caminhos.

O aplicativo distingue licença do código e dos pesos. Na versão testada, os pesos OmniVoice são declarados para uso não comercial e o tokenizador tem termos próprios Higgs Audio 2/Meta Llama 3. O VoiceStudio exige confirmação explícita. Em cada instalação, apresentar os termos vigentes e somente registrar aceite depois da autorização do usuário, pela API oficial `/models/licenses/accept`. A autorização obtida na máquina testada não é transferida por este repositório. O inicializador não aceita licenças e não contorna essa verificação.

## Inicializar e conectar

```powershell
& "$resourceDir/.venv/Scripts/python.exe" "$mediaRoot/voice-runtime/launcher.py" --start
```

Abrir `http://127.0.0.1:3917/` ou conferir `/health`. O argumento `--mcp` garante que o backend esteja disponível e inicia o servidor stdio; seu bloco Codex está em [mcp.example.toml](../codex/mcp.example.toml). Logs ficam em voice-runtime; dados, histórico e áudios ficam em trabalho. A saída do MCP usa arquivos, não base64 no contexto.

Teste real concluído nesta instalação: `check_health` e `generate_speech` em português pelo MCP; WAV de 7,927 s a 24 kHz. Transcrição, dublagem, clonagem com amostra do usuário e outros motores não foram validados. O exemplo seleciona ASR PyTorch para evitar a dependência cuDNN 8 dos motores CTranslate2, mas não instala pesos ASR.
