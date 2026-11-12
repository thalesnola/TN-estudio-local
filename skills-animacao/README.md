# Skills de animação

## Skills próprias para Codex

| Skill | Estilos |
|---|---|
| [animacao-2d-estilizada](animacao-2d-estilizada/SKILL.md) | Pixel art, quadrinhos, recorte de papel, anime retrô e risografia |
| [animacao-3d-estilizada](animacao-3d-estilizada/SKILL.md) | PS2, brickfilm, massinha, low poly e diorama miniatura |

Cada skill inclui cinco receitas sob demanda, critérios de revisão visual e integração com ferramentas disponíveis. Não instala aplicativos, plugins comerciais ou pesos. ImageGen, WanGP, ArtCraft e HyperFrames são rotas condicionais; não são necessários para descobrir e ler as receitas. Projetos 3D editáveis exigem um aplicativo 3D disponível, como Blender.

### Instalação no Windows

No checkout deste repositório, execute em PowerShell 5.1 ou superior. O comando recusa sobrescrever uma skill existente; revise as diferenças antes de atualizar uma instalação anterior.

```powershell
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
foreach ($name in @('animacao-2d-estilizada', 'animacao-3d-estilizada')) {
    $source = Join-Path (Join-Path $PWD 'skills-animacao') $name
    $destination = Join-Path $skillRoot $name
    if (Test-Path -LiteralPath $destination) { throw "Skill já existe: $destination" }
    Copy-Item -LiteralPath $source -Destination $destination -Recurse
}
```

Abra um novo chat para atualizar a descoberta. Exemplos:

- `Use $animacao-2d-estilizada para criar um loop de pixel art de 3 segundos, resolução lógica 320×180 e entrega 1080p.`
- `Use $animacao-3d-estilizada para criar um diorama de cafeteria e entregar a cena .blend e um vídeo de 5 segundos.`

### Verificação

Na raiz do repo: `python -m unittest discover -s tests -v`. Os testes usam só a biblioteca padrão e verificam integridade do pacote, referências e ausência de caminhos pessoais. Consulte [o registro dos testes](../docs/testes-skills-animacao.md) para os testes de integração e seus limites.

## Skills de animação, motion e estratégia de vídeo de terceiros

Oito pacotes de terceiros para animação, motion design e engenharia de retenção/roteiro. **Não são vendorizados aqui**: o repo guarda só a auditoria, o commit verificado e a receita de instalação. Auditoria estática em 06/11/2026 e 11/11/2026 (leitura e grep; nada executado sem inspeção prévia).

| Skill | Origem (commit auditado) | Licença | Veredito | Faz |
|---|---|---|---|---|
| `anidoodle` | [alexgreensh/anidoodle](https://github.com/alexgreensh/anidoodle) `4ae27d2` | Apache-2.0 | Seguro com ressalvas | Arte e animação em código, 32 estilos, filmes, narração opcional |
| `claude-drawing` | [cloveric/claude-drawing-skill](https://github.com/cloveric/claude-drawing-skill) `4886ed8` | MIT | Seguro | Ilustração procedural (numpy + Pillow) em 77 estilos |
| `whiteboard-video` | [Matteoikarieth96/whiteboard-video-skill](https://github.com/Matteoikarieth96/whiteboard-video-skill) `75c7825` | MIT | Seguro com ressalvas | Vídeo explicativo de quadro branco com voz e legenda |
| `javascript-animation` + `soundtrack` | [iart-ai/javascript-animation-skills](https://github.com/iart-ai/javascript-animation-skills) `f7d0882` v0.4.1 | MIT | Seguro com ressalvas | Animação em canvas 2D → MP4; trilha sintetizada em código |
| `youtube-agent-skill` (`yt-*`) | [Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) `a2feb21` | MIT | Seguro | 11 skills + 6 scripts Python stdlib puros: viralidade por múltiplo da mediana, 21 fórmulas de gancho pontuadas, linter título+thumb, retenção CSV×SRT, EDL de corte de silêncio e capítulos |
| `awesome-ai-motion` | [gongnyang/awesome-ai-motion](https://github.com/gongnyang/awesome-ai-motion) `1e3c249` | MIT | Seguro com ressalvas | 637 técnicas de motion, 128 clipes, 11 receitas e 7 rotas em HTML/SVG/GSAP com parâmetros medidos e render via Playwright + FFmpeg |
| `bang-motion` | [bangtutorial/bang-motion](https://github.com/bangtutorial/bang-motion) `c1aa65e` | MIT | Seguro | Motion graphics cinematográficos (openers, promos, tipografia cinética e 5 estilos de explainer) em `index.html` único |
| `vox-explainer` | [CK42BB/vox-explainer-skill](https://github.com/CK42BB/vox-explainer-skill) `7003225` | MIT | Seguro | Guia e receitas em Markdown para vídeos explicativos no estilo documentário Vox |
| `huashu-art-motion` | [alchaincyf/huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion) `1468196` | MIT | **Bloqueada / Não instalar** | Variante chinesa da `anidoodle`; adiciona `koubo.py` apontando para `openspeech.bytedance.com` e rota `/__file__/` sem restrição de diretório no servidor HTTP local (`qa.py`/`render.py`). Usar `anidoodle`. |

Nenhum dos pacotes aprovados tem hooks maliciosos, `postinstall` oculto, binário executável, ofuscação, telemetria ativa ou leitura de credenciais.

## Ressalvas por skill

**anidoodle**
- `npm install` e download do Chromium (~150 MB) na pasta de trabalho, não em `~/.claude`.
- Download opcional de sons (233–373 MB, SHA-256 conferido) só se o usuário aceitar.
- Narração em nuvem (Gemini, OpenAI, ElevenLabs) é opcional e **envia o texto**: usar só os provedores locais (`say`, `kokoro`, `files`) com material sensível.
- Figma (`FIGMA_TOKEN`) só na rota Figma; o HTML da escuta carrega Google Fonts.
- Exige Node ≥ 22 e ffmpeg para vídeo.

**claude-drawing**
- `SKILL.md` de 629 KB: custo de contexto quando a skill dispara; a descrição longa também aparece na lista de skills.
- Instalar `numpy` e `Pillow` em venv próprio; rodar os scripts com o Python do venv.
- Não clonar o repo inteiro (138 MB de amostras e histórico).

**whiteboard-video**
- Motores de voz `elevenlabs` e `openai` enviam o roteiro e a chave a terceiros; o motor `say` é só macOS. No Windows, com material sensível, usar apenas `engine: files` (gravações próprias).
- `scenes.js` é JavaScript gerado, executado no Chrome headless com `--allow-file-access-from-files`: revisar se o roteiro for de origem não confiável.
- `npm ci` (lockfile fixado); `new_project.sh` pede Git Bash; Chrome em `C:\Program Files\Google\Chrome\Application\chrome.exe` ou `CHROME_PATH`.

**javascript-animation / soundtrack**
- `playwright-core` sem versão fixa e sem lockfile: fixar a versão ao instalar.
- Há um `curl` opcional a openrouter.ai só na documentação: não usar com dado de caso.
- Não renderizar HTML de terceiros com o `render.mjs` dela.
- Sobrepõe a [`video-codigo`](../video-codigo/SKILL.md): mesmo nome `render.mjs`, contrato diferente (`draw(frame)` em vez de `__seek(t)`). Não misturar os scripts; usar `javascript-animation` só para canvas 2D puro.

## Instalação (Windows, cópia seletiva, sem `.git`)

Clonar raso, conferir o commit da tabela e copiar só o necessário para `~/.claude/skills/`:

```bash
git clone --depth 1 https://github.com/alexgreensh/anidoodle && cp -r anidoodle/skills/anidoodle ~/.claude/skills/anidoodle
git clone --depth 1 https://github.com/iart-ai/javascript-animation-skills && cp -r javascript-animation-skills/skills/{javascript-animation,soundtrack} ~/.claude/skills/
# whiteboard-video: scripts assets references examples SKILL.md LICENSE; depois, em scripts/: npm ci --ignore-scripts
# claude-drawing: SKILL.md LICENSE requirements.txt lib/ examples/*.py; venv: python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt
```

Instalada em 06/11/2026 numa estação Windows; nenhuma geração foi executada ainda.

## Regra de sigilo

Qualquer uma que chame API externa (narração, música, Figma) leva o texto e as chaves para fora da máquina: nunca com dado de caso. Saída gerada é rascunho até conferência humana.
