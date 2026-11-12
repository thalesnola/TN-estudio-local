# Hypit (skill de terceiros, auditada)

[hypit-ai/hypit](https://github.com/hypit-ai/hypit) v0.3.2, commit auditado `2d31e88` (06/11/2026). Direção e produção de vídeo por agente: mídia gerada e componentes programáveis (SVML/SVS/SVRun), referências, legendas, variantes. **Não é vendorizado aqui**: só auditoria, limites e receita.

**Veredito: seguro com ressalvas. Instalada somente a skill** (texto, 781 KB). O executável (`@hypit/hypit`), ffmpeg, uv, Chromium e modelos **não** foram instalados.

## Auditoria (leitura e grep, nada executado; duas fatias independentes)
- Sem telemetria, binário commitado, ofuscação, `preinstall`/`postinstall`/`prepare`, leitura de `~/.ssh`/`~/.aws`/perfil de navegador. Lockfile com integridade, sem `git:`/tarball. Processos externos com argumentos em lista, sem shell. Servidores locais só em `127.0.0.1`. WhisperX local, só loopback.
- A skill não tem `curl | sh`, não edita `settings.json`/hooks, não contém prompt injection. Manda o agente instalar `npm i -g @hypit/hypit`, ffmpeg e uv: **aprovar cada passo**.

## Ressalvas
1. **Provedor remoto leva tudo para fora**: `hypit.ai`, tokendance, beatapi, hiapi, pollo, monid, ElevenLabs/Fish. Saem prompts, vídeos e imagens de referência, rostos, amostras de voz e a chave. **Nunca com dado de caso.**
2. **Chromium com `--no-sandbox`** executando JS do projeto (`new Function`): abrir só projetos confiáveis; preferir VM/contêiner.
3. **Download de plataformas** (yt-dlp: YouTube, TikTok, Instagram, Bilibili): termos de uso e direitos autorais.
4. **Credenciais em JSON claro** em `%LOCALAPPDATA%\Hypit` (tokens OAuth não cabem no cofre do Windows, 512 caracteres): proteger a pasta ou usar variáveis de ambiente.
5. **Sem trava de consentimento, moderação ou marca d'água.** A skill orienta "faça com o meu rosto" e clonagem de voz; o marketing é "clonar qualquer vídeo viral". Gerar rosto ou voz de pessoa real sem consentimento, ou copiar peça alheia, viola imagem, personalidade, LGPD e direitos autorais. Uso aqui: material próprio ou com autorização; **nunca** rosto/voz de pessoa real do acervo de caso e nenhuma peça que simule terceiros.
6. Exemplos baixam mídia de `storage.googleapis.com` sem hash: não rodar.

## Licença
Apache-2.0 modificada: uso próprio e comercial interno permitidos, inclusive para clientes; proibido oferecer como serviço multi-tenant/SaaS e revender; **não remover nome, logo e copyright** da CLI e dos relatórios; o produtor pode mudar a licença no futuro. A saída é do usuário, sujeita aos termos dos provedores de modelo.

## Viabilidade
- Runtime: Node ≥ 22.15, ffmpeg/ffprobe no PATH, `uv` para WhisperX/yt-dlp, Chromium baixado sob demanda. Windows suportado (winget, cofre via PowerShell); o launcher da raiz é `sh`, mas `npm i -g` expõe `hypit`.
- Custo: chaves pagas para gerar mídia (exemplo do README: ~US$ 1,09 por vídeo de ~26 s, não medido aqui). Legendas e motion graphics só por código funcionam sem modelo de geração.
- Sobrepõe [`video-codigo`](../video-codigo/SKILL.md) e as skills de [`skills-animacao/`](../skills-animacao/README.md); `hypit` é para vídeo com mídia gerada por provedor, as demais renderizam localmente.

## Instalação da skill (cópia manual, sem o plugin)
```bash
git clone --depth 1 https://github.com/hypit-ai/hypit && git -C hypit checkout 2d31e88
cp -r hypit/skills/hypit ~/.claude/skills/hypit
```
Alternativa: `npx skills add hypit-ai/hypit -g`. As pastas `.claude/skills/hypit` e `.codex/skills/hypit` do repo são links simbólicos: copiar `skills/hypit`.

Instalada em 06/11/2026 numa estação Windows; nenhuma geração executada.
