---
tipo: stack
tags: [skills, 3d, video, blender, ffmpeg, remotion, seguranca]
projeto: tmp
atualizado: 2026-10-06
---
# Skills de 3D e edição de vídeo: avaliação (06/10/2026)

Busca com `npx skills find` + clone raso e leitura do código (nada executado). Relacionada: [[archify-diagrama-html-licoes-de-uso]].

## Licão de método
- **Contagem de instalações do skills.sh não é confiável**: o mesmo `ai-video-generation` aparece em 5 forks com 200–680 mil. Usar estrelas, licença e código.
- Auditar com `grep` por `subprocess|child_process|curl|rm -rf|http` antes de instalar.

## Veredito
| Skill | Resultado |
|---|---|
| `affaan-m/ecc@video-editing` | só SKILL.md (ffmpeg + Remotion); MIT; local. **Recomendada** |
| `cloudai-x/threejs-skills` | 10 SKILL.md só texto; sem licença no repo; parada desde jan/2026. Segura |
| `roble3/cc-blender-skill` | MIT, 84 estrelas; depende de `blender-mcp`, cujo `execute_blender_code` roda Python arbitrário + telemetria (`disable_telemetry`). Exige Blender >= 4.0 e `uv`; Blender não instalado na Dell Pro Max |
| `remotion-dev/skills` | oficial, só markdown; **Remotion exige licença paga para equipes/empresas grandes** — checar antes de uso institucional |
| `heygen-com/hyperframes` | Apache-2.0; telemetria PostHog **ligada por padrão**; GSAP via CDN jsdelivr; scripts com `child_process`/`rm -rf`. Não usar com material sigiloso |

Regra: nada disso toca dado de caso (ver [[hierarquia-tres-executores]]).

## Instalação (06/10/2026, Dell Pro Max, uso pessoal)
- `npx skills add <repo> --skill '*' -g -a claude-code -y` aceita **um repo por chamada** (vários na mesma linha: só o primeiro instala).
- Instalados: ecc video-editing, threejs (10), remotion (12), cc-blender-skill (30), hyperframes (21). Alertas do instalador em `remotion-docs` (chave pública Algolia) e `threejs-interaction`: falsos positivos.
- Telemetria: `npx hyperframes telemetry disable` (+ `status`); env `HYPERFRAMES_NO_TELEMETRY=1`/`DO_NOT_TRACK=1`. Blender MCP: `DISABLE_TELEMETRY=true` (`setx` + `-e` no `claude mcp add`).
- Blender via `winget install BlenderFoundation.Blender.LTS.4.5` (pede UAC). Escolhida a LTS 4.5, não a 5.2, por compatibilidade com o addon.
- MCP: `claude mcp add blender -s user -e DISABLE_TELEMETRY=true -- uvx mcp-for-blender`. `uvx mcp-for-blender install-addon` falha se o Blender nunca abriu: criar `%APPDATA%\Blender Foundation\Blender.5\scriptsddons` e passar `BLENDERMCP_ADDONS_DIR`; habilitar sem GUI com `blender -b --python-expr "bpy.ops.preferences.addon_enable(module='blender_mcp'); bpy.ops.wm.save_userpref()"`.
- Mitigação do Python arbitrário: regra `ask` para `mcp__blender__execute_blender_code` em `settings.local.json` (por máquina), que vence o `defaultMode: auto`. Ver [[hooks-do-claude-code]].
- Licença Remotion: grátis para pessoa física/≤3 funcionários/ONG; órgão ou empresa maior precisa de licença — trabalho só na Precision ([[maquina-dell-5860-windows]]).

## Teste com o Blender via MCP (06/10/2026)
- ⚠️ **Nunca rodar `bpy.ops.wm.read_factory_settings` pelo MCP**: recarrega as preferências, desliga o addon e **derruba o servidor** (`Connection closed`; `get_addon_status` → "Not connected"). Recuperação: matar o `blender.exe` e abrir de novo (o addon habilitado sobe o servidor sozinho). Para limpar a cena, remover os objetos (`bpy.data.objects.remove`).
- Servidor só sobe com o Blender **aberto**; abrir com `Start-Process ...blender.exe` e esperar ~20 s.
- Moeda de emblema: cilindro (128 vértices), UV planar `x/2+0.5, y/2+0.5`, material 0 = metal (lateral), material 1 = textura na tampa (`normal.z>0.9`); EEVEE = `BLENDER_EEVEE_NEXT` no 4.5. A textura entra do arquivo fornecido, sem redesenho: [[emblema-institucional-nunca-redesenhado-por-ia]].
