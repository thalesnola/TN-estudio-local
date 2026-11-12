# Scripts pessoais nola-macm5

Os arquivos em `scripts/` na raiz do repositório permanecem originais da estação profissional. Esta variante executa somente as cópias em `macos-pessoal/scripts/`, com identificadores neutros. Assets não são copiados nem fabricados durante a instalação.

## Ambiente e caminhos

```sh
uv pip install --python .venv/bin/python -r macos-pessoal/scripts/requirements-media.txt
export NOLA_MEDIA_ROOT="$HOME/nola-macm5/midia"
```

A raiz é configurável e independe do diretório corrente. O padrão é `~/nola-macm5/midia`; subpastas: `fontes`, `blend`, `modelo-3d`, `renders` e `renders-esfera`. Fontes e mestres precisam ser fornecidos pelo usuário. Não apontar para pastas profissionais para obter um arquivo que está faltando.

**CPU é o padrão validado no Blender 5.2.3 LTS desta máquina.** A GPU Metal foi detectada, mas o primeiro render real abortou no compilador Metal com `NSInvalidArgumentException` e `NSURL initFileURLWithPath: nil string parameter`; uma segunda inspeção Metal concluiu frente/verso após cerca de dois minutos de compilação. Isso é uma limitação observada da instalação, não uma sonda de sucesso. `NOLA_BLENDER_DEVICE=METAL` ou `--device METAL` seleciona Metal explicitamente para diagnóstico. Os scripts não gravam preferências globais do Blender nem fazem fallback silencioso depois de um crash.

## Composição de vídeo

```sh
.venv/bin/python macos-pessoal/scripts/video/aplicar_emblema.py \
  "$NOLA_MEDIA_ROOT/entrada/video.mp4" "$NOLA_MEDIA_ROOT/saida/video-com-arte.mp4" \
  --emblema "$NOLA_MEDIA_ROOT/fontes/arte.png" \
  --centro 500 350 --diam 90 --modelo 300 200 400 280
```

Preserva o rastreio por correlação de textura, busca multiescala opcional `--ref`, suavização e composição local. A arte é obrigatória; PNG com alfa respeita sua transparência, imagem sem alfa recebe a máscara circular do algoritmo original. Áudio opcional é codificado em AAC para MP4/MOV. Valida vídeos, caixa de rastreio e dimensões pares para H.264; preserva entradas, recusa saída existente sem `--sobrescrever`, grava primeiro em arquivo temporário e verifica o FFmpeg antes de entregar. A fonte nunca é redesenhada por modelo.

## Blender com caminhos explícitos

```sh
blender --background --python-exit-code 1 \
  --python macos-pessoal/scripts/blender_media.py -- \
  render --input "$NOLA_MEDIA_ROOT/blend/cena.blend" \
  --output "$NOLA_MEDIA_ROOT/saida/quadro.png" --width 1080 --height 1920 --transparent

blender --background --python-exit-code 1 \
  --python macos-pessoal/scripts/blender_media.py -- \
  export-glb --input "$NOLA_MEDIA_ROOT/blend/cena.blend" \
  --output "$NOLA_MEDIA_ROOT/modelo-3d/modelo.glb"

blender --background --python-exit-code 1 \
  --python macos-pessoal/scripts/blender_media.py -- \
  verify-glb --input "$NOLA_MEDIA_ROOT/modelo-3d/modelo.glb" \
  --output "$NOLA_MEDIA_ROOT/saida/conferencia"
```

Ação `pack` empacota texturas e salva uma cópia `.blend`. Exportação genérica usa somente meshes/empties e materiais que o exportador GLB suporta; ela não promete equivalência de redes procedurais arbitrárias. Ações recusam sobrescrita por padrão. `verify-glb` enquadra a geometria importada e renderiza frente/verso, sem salvar alterações no asset original.

## Equivalentes dos scripts de produção

| Etapa | Cópia pessoal | Requisito e limite |
|---|---|---|
| Imagem → contorno e mapas de cor/altura/esmalte | `scripts/3d/emblemas/preparar.py` | Lê `fontes/<id>.jpg`; SciPy/OpenCV. Preserva o algoritmo de máscara, contorno, relevo e metal. |
| Preparar texturas esféricas e material GLB | `preparar_esfera.py`, `preparar_glb_esfera.py` | Usa os mapas produzidos e, para o verso GLB, `fontes/nola-macm5-cor.png`. |
| Construir moeda/escudo e esfera | `construir.py`, `construir_esfera.py` | Requer mestre pessoal compatível, materiais e objetos descritos abaixo; não há mestre no Git. |
| Render CPU/Metal, alfa, vertical e quadros de teste | `cycles_gpu.py`, `render_alpha.py`, `render_vertical.py`, `render_vertical_arte.py`, `teste_quadros.py` | `cycles_gpu.py` mantém o nome por compatibilidade, mas escolhe CPU por padrão. |
| Exportar e inspecionar GLB da peça/esfera | `exportar_glb.py`, `exportar_glb_esfera.py`, `verificar_glb.py` | Usa os mesmos nomes neutros dos objetos construídos nesta variante. |
| Fundo e entregas finais | `so_fundo.py`, `posprocessar.py` | Mantém composição, dithering, ProRes 4444 e VP9 alfa. Pós-processamento legado espera 144 quadros/24 FPS e tamanhos medidos; não é conversor genérico. |
| Lote serial e finalização | `scripts/renderizar_lote.py` | Substitui os dois shell scripts dependentes de caminhos Windows; verifica exit codes e não aguarda texto em log indefinidamente. |
| Empacotar e exportar o modelo-base | `scripts/3d/modelo-base/` | Cópias com caminhos pessoais; a construção exata depende de mestre/arte compatíveis. |

Os caminhos na tabela, salvo quando completos, são relativos a `macos-pessoal/scripts/3d/emblemas/`.

Exemplo de preparação e lote:

```sh
.venv/bin/python macos-pessoal/scripts/3d/emblemas/preparar.py nola-macm5
.venv/bin/python macos-pessoal/scripts/3d/emblemas/preparar_esfera.py nola-macm5
.venv/bin/python macos-pessoal/scripts/renderizar_lote.py nola-macm5 --tipo emblema --posprocessar
```

Preparação conserva os limiares gerais do algoritmo. Ajustes antes associados a nomes específicos agora são explícitos: `NOLA_LUMINANCE_WEIGHT` (padrão 0.6), `NOLA_GLOBAL_DISTANCE=1`, `NOLA_HEIGHT_LOW` (14), `NOLA_HEIGHT_HIGH` (34). Esses parâmetros precisam ser medidos na arte pessoal; nomes não selecionam presets institucionais.

A construção de moeda exige no mestre os objetos `GIRO`, `GEO-FaceVerso`, `GEO-AroVerso`, `GEO-Base`, `GEO-Aro`, `GEO-FaceCampo`, `GEO-FaceLetras` e material `MAT-Campo`. A esfera exige `GIRO`, `MAT-Metal` e os mapas pessoais `nola-macm5-cor.png`/`nola-macm5-altura16.png`. Centro/raio do verso são obrigatórios via `NOLA_BACK_U`, `NOLA_BACK_V`, `NOLA_BACK_RADIUS`, todos normalizados; não reaproveita silenciosamente coordenadas medidas em outra arte. `NOLA_SPHERE_SEGMENTS` e `NOLA_SPHERE_RINGS` configuram densidade (padrões 1440/720, execução pesada); rings deve ser par. Não monte uma esfera completa para um teste de instalação.

`modelo-base/gerar_contornos_emblema.py` preserva uma calibração geométrica específica e por isso **recusa execução por padrão**. `NOLA_ALLOW_CALIBRATED_CONTOURS=1` só deve ser usado após conferir compatibilidade da arte pessoal. Para arte arbitrária, usar a preparação geral. Não se afirma equivalência visual dos mestres ausentes.

## Validação observada

```sh
.venv/bin/python -m unittest discover -s macos-pessoal/tests -p 'test_media.py' -v
```

Três testes passaram: identificadores sem caminhos; composição real de vídeo sintético de seis quadros com arte alfa, preservação da fonte e recusa de sobrescrita; preparação real de imagem sintética e mapas esféricos de 16 bits. Compilação Python de todas as cópias passou. Na variante foram corrigidos dois defeitos encontrados ao portar: índices de triângulos retornados como vetores no Blender e canvas esférico que podia ser menor que a imagem recortada.

Smoke test do Blender com uma cena sintética: exportação GLB concluída, render CPU 64×64 e inspeção CPU frente/verso concluídos. Os 23 scripts 3D não foram todos exercitados com os assets reais ausentes; o pipeline de 144 quadros e os mestres especializados continuam exigindo validação na produção pessoal fornecida.
