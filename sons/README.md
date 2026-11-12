# Som: efeitos, trilha e conferência de áudio (terceiros, auditados)

Duas skills de terceiros para o áudio dos vídeos. **Não são vendorizadas**: o repo guarda a auditoria, o commit verificado, as correções aplicadas e a receita. Auditoria estática em 06/11/2026 (leitura e grep; nada executado antes da decisão), uma por repo.

| Skill | Origem (commit auditado) | Licença | Veredito | Faz |
|---|---|---|---|---|
| `openverse-sfx` | [Varnan-Tech/opendirectory](https://github.com/Varnan-Tech/opendirectory) `caac7cd`, pasta `skills/openverse-sfx` | MIT | Com ressalvas; nota 3/5; **instalada com correções** | Busca efeitos e música CC0/CC-BY/domínio público no Openverse, baixa, normaliza, alinha à batida e mede o MP4 |
| `earshot` | [Leonxlnx/earshot](https://github.com/Leonxlnx/earshot) v0.4.1 `4ac3d2a` | MIT | Com ressalvas; nota 4/5; **instalada** | "Ouvidos" para o agente: mede loudness e true peak, compara, ranqueia, acha o melhor trecho, diz se o som parece real ou sintético, critica o áudio de um vídeo e traz um banco de 252 efeitos gerados por código |
| `real-sound` (mesmo repo do earshot) | idem | MIT | Nota 3/5; **não instalada** | Trilha com gravações reais licenciadas |

`realsfx`, citado no pedido, não existe como repo: foi tratado como a `real-sound` do `earshot`.

## openverse-sfx

**Seguro:** única chamada fixa `api.openverse.org`, anônima, só com o termo de busca; sem chave; sem hooks nem instalação automática.

**Falhas achadas e corrigidas na cópia local**
- `sfx_fetch.py` aceitava qualquer URL (`file://`, redirecionamento, IP interno), sem teto de tamanho, sem checar o tipo, com `--name` sem sanitização (`../`) e a atribuição do autor passada na linha de comando. Agora: `--id` do resultado salvo pela busca (`sfx/last_search.json`), https só em `freesound.org` e `jamendo.com` com redirecionamentos conferidos, teto de 50 MB, `audio/*`, nome `[\w-]{1,64}`, extensões de áudio apenas. Testado com 5 recusas (`file://`, host fora da lista, `.exe`, `../`, id inexistente).
- Receitas ffmpeg: `loudnorm` sem `-ar 48000` pode sair a 192 kHz e quebrar o AAC; o ducking atingia também os efeitos; `adelay` só funcionava em estéreo. Corrigidos.
- Scripts no Windows: `encoding="utf-8", errors="replace"` nos subprocessos e checagem do `rfind("Summary:")`.
- `python3` trocado por `python`; dependências em venv com `requirements.lock.txt`.

**Licença e crédito (crítico para publicar):** o filtro (`cc0,by,pdm`, fontes freesound/jamendo) exclui NC, ND e SA. O `credits.txt` agora leva atribuição, página de origem e a nota "modified". **Colar o `credits.txt` na descrição do vídeo** e abrir a página de origem de cada faixa CC-BY para confirmar a licença. Faixas do Jamendo podem gerar reclamação de direitos (Content ID) no YouTube. A busca devolve prévias em mp3, não o original.

**Conflito:** a skill proíbe sintetizar áudio, o oposto da `soundtrack`; não competem pelo mesmo gatilho (uma busca som real de terceiros, a outra sintetiza).

## earshot

**Seguro:** subprocess só `ffmpeg`/`ffprobe` em lista; `np.load` com `allow_pickle=False`; modelos CLAP e AST em safetensors com revisão fixada; sem telemetria; nenhum áudio commitado (o banco de efeitos é gerado por código, 15 deles ajustados a gravações CC0).

**Custo e rede:** torch só CPU (~200 MB) e ~1,1 GB de modelos do Hugging Face, baixados uma vez; depois roda 100% offline com `EARSHOT_OFFLINE=1`. Cerca de 10 s por chamada de CLI; para lote, usar script Python.

**Ressalvas aplicadas**
- Comando `earshot llm` (Gemini) **envia o áudio ao Google**: nunca usar, não definir `GEMINI_API_KEY`, nunca com material de caso.
- Instalado sem os extras `[mcp,llm]`, sem registrar servidor MCP global (a instrução `claude mcp add --scope user` do `SKILL.md` foi removida).
- `description` da skill reescrita para não disputar gatilho com a `soundtrack` (composição) e a `openverse-sfx` (download): só ouvir, medir, comparar e o banco de efeitos.
- Dependências sem pino no `pyproject.toml`: `pip freeze` salvo em `requirements.lock.txt`.
- Alpha (Development Status 3). A nota de realismo (`p_real`) não é prova de origem: sons sintéticos limpos podem ler-se como reais ou o contrário.

**Medido aqui (Windows, CPU):** `doctor` saudável (252 sons no banco); `sfx render click/double` + `sfx check` limpos; `measure` em 10 s e `realness` em 9 s com `EARSHOT_OFFLINE=1`.

**Por que não a `real-sound`:** proíbe sintetizar som, o contrário do fluxo de efeitos e trilha em código; exige baixar áudio de Freesound/Mixkit com auditoria de licença e orquestra vários subagentes (custo alto de tokens).

## Instalação usada (Windows)

```bash
# openverse-sfx: copiar só a pasta da skill; venv e dependências fixadas
cp -r opendirectory/skills/openverse-sfx ~/.claude/skills/openverse-sfx   # sem README.md nem package.json
python -m venv ~/.claude/skills/openverse-sfx/.venv
~/.claude/skills/openverse-sfx/.venv/Scripts/python.exe -m pip install librosa matplotlib numpy scipy soundfile
# earshot: commit auditado, venv com torch CPU, modelos em cache próprio
git clone https://github.com/Leonxlnx/earshot ~/tools/earshot && git -C ~/tools/earshot checkout 4ac3d2a
py -3.12 -m venv ~/tools/earshot/.venv
~/tools/earshot/.venv/Scripts/python.exe -m pip install "torch>=2.6" --index-url https://download.pytorch.org/whl/cpu
~/tools/earshot/.venv/Scripts/python.exe -m pip install -e ~/tools/earshot
EARSHOT_HOME=~/tools/earshot-cache ~/tools/earshot/.venv/Scripts/python.exe -m earshot doctor --fetch
cp -r ~/tools/earshot/skills/earshot ~/.claude/skills/earshot   # e editar description e Setup como acima
```

Depois de instalar, confira `earshot doctor` e fixe as versões com `pip freeze`. Saída gerada é rascunho até conferência humana.
