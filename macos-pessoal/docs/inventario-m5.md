# Inventário de ferramentas audiovisuais — M5 (macOS), 07/11/2026

Verificação somente leitura, sem instalar nem gerar. Só versões, caminhos e saúde de importação.
Não cobre abertura de apps gráficos, render, geração ou download.

| Componente | Versão / estado | Observação |
|---|---|---|
| ffmpeg / ffprobe | 9.0.2 | responde |
| whisper | CLI presente | modelo padrão turbo baixa pesos na primeira execução |
| yt-dlp | 2026.10.26 | responde |
| exiftool | 13.55 | responde |
| tesseract | 5.5.3 | idioma `por` presente |
| uv | 0.13.5 | responde |
| node | v26.12.1 | compatibilidade com Remotion/HyperFrames não testada |
| Blender | 5.2.3 LTS (`/Applications/Blender.app`) | Promax tem 4.5; scripts de `blender/` devem ser checados nas duas versões |
| kdenlive | 26.08 | instalado, UI não aberta |
| Draw Things | 26.1020.0 | instalado, não testado nesta verificação |
| draw.io | 32.6.1 | instalado |
| Ollama | nomic-embed-text, qwen3.8:27b, gpt-oss:20b, qwen3-coder:30b | — |
| venv `~/Estudio/ltx-venv` | mlx 0.32.4, mlx_audio 0.6.4, mlx-vlm 0.7.12, mlx-video-with-audio 0.1.37 | **o pacote instala o módulo `mlx_video`; `import mlx_video_with_audio` falha** |

## Skills em `~/.claude/skills`
- 10 links para `~/.agents/skills` (hyperframes, hyperframes-cli, hyperframes-registry, low-stimulation-video, media-use, figma, reverse-any-video, slideshow, style-sampling, e um de remotion), todos resolvendo.
- 14 skills `remotion-*`, todas com SKILL.md.
- 6 diretórios próprios: soundtrack, earshot, anidoodle, claude-drawing, javascript-animation, whiteboard-video.
- Nenhum link quebrado. Conteúdo interno dos SKILL.md não auditado nesta rodada.

## Pendências
1. Corrigir o nome de import do LTX com áudio (`mlx_video`).
2. Testar Blender 5.2 contra os scripts de `blender/` (foram escritos para 4.5).
3. Medir LTX em MLX com um clipe, antes de qualquer decisão de fila.
4. Decidir se whisper usa modelo menor para conferência de legenda.
