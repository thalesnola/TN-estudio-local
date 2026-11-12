---
tipo: padrao
tags: [blender, 3d, relevo, displace, emblema, video, ffmpeg, medido]
projeto: tmp
atualizado: 2026-10-06
---
# Relevo 3D de emblema no Blender por mapa de altura (moeda com giro 360°)

Receita medida em 06/10/2026 (Blender 4.5 LTS, EEVEE, Dell Pro Max). Emblema entra como **textura do arquivo fornecido**, nunca redesenhado: [[emblema-institucional-nunca-redesenhado-por-ia]]. Complementa [[recriar-emblema-com-relevo]] e [[skills-de-3d-e-video-avaliacao-2026-10]].

## Receita
1. **Mapa de altura** (PIL+scipy): luminância → mediana 5 px (tira granulado) → gaussiana → smoothstep → **piso**: abaixo de ~0,10 vira zero exato (campo escuro plano) → gaussiana final. Salvar em **PNG 16 bits** (`uint16`); 8 bits dá degraus.
2. **Malha**: `primitive_grid_add` 900×900, size 2, apagar vértices com `|v|>0.985` (círculo); aro de metal (torus) cobre a borda recortada. Modificador **Displace**: textura de imagem Non-Color, coordenada UV, `mid_level=0`, `strength` 0,075–0,08 para disco de 2 m.
3. **Textura de cor**: cópia com `cv2.fastNlMeansDenoisingColored(h=4)`; original intacto.
4. **Verso**: segunda grade com rotação `(90°,0,180°)` (sem espelhar, de cabeça para cima); frente `(90°,0,0)`. Filhos de um Empty que gira em Z (keyframes 0→360° em 1→145, interpolação linear = ciclo sem emenda).
5. **Render**: `blender -b arq.blend -o prefixo -a` em segundo plano (não pelo MCP); 256 amostras TAA; depois `ffmpeg -framerate 24 -i f_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 15`.

## Lições de erro
- **Listras horizontais = z-fighting**, não mapa ruim: face plana coincidia com a tampa do cilindro-base. Diagnóstico: renderizar com o Displace desligado (listras ficam piores). Solução: afinar a base (`scale.z=0.9`).
- Filhos de Empty sem *parent inverse*: deslocamentos de profundidade ficam no eixo local do pai; após girar 90° a profundidade é Y, não Z (base cobriu a face).
- Luz rasante sem sombra não resolveu nada; hipótese de "shadow acne" descartada pelo teste.
- `rm` de `giro2\*` foi barrado pela trava de segurança: renderizar em prefixo novo em vez de apagar.

## Atualização — de "relevo por mapa" a geometria extrudada + Cycles (06/10/2026)
Usuário achou o resultado "plástico" sem saber dizer por quê. Diagnóstico por causas, não por sintoma:
- **Displace de grade em parede íngreme** gera riscas/degraus na vista de lado (parede = 1 faixa de polígonos esticados). Para letras e aros, **extrudar o contorno**: `cv2.findContours(RETR_CCOMP)` sobre máscara 2× (cúbica) limiarizada → JSON → `tessellate_polygon([externo, *furos])` → `bmesh.ops.extrude_face_region` → Bevel (35°, 3 seg) + `shade_smooth_by_angle`. Campo = disco plano escuro. Displace só para o que é orgânico (coruja).
- **Aros tremidos** (máscara por limiar sobre foto): medir círculo por mínimos quadrados, apagar a faixa da máscara (± 0,004) e modelar o aro como anel perfeito (256 seg). Atenção: o emblema pode não estar centrado na imagem (desvio 0,04).
- **"Plástico" = reflexo uniforme**: face plana de frente reflete uma cor só. Receita: mundo (só raios não-câmera, via Light Path *Is Camera Ray*) com **degradê vertical** pela coordenada Generated Z; rugosidade com ruído (±0,07) + bump alongado (escovado) + anisotropia 0,5; **inclinação oscilante** do Empty (`rotation_mode='ZXY'`, X ±9° em 5 chaves, laço perfeito).
- Prata polida plana reflete o escuro atrás da câmera e sai cinza; luz frontal grande a deixa branca chapada. Campo escuro: metálico 1, base ~0,03, rugosidade 0,7.
- **Cycles**: `-P script.py` define `compute_device_type` OPTIX→CUDA e `scene.cycles.device='GPU'` (preferências não vão no .blend); 128 amostras + OIDN, ~10 s/quadro 1080² na RTX PRO 1000 de 8 GB; `sample_clamp_indirect=8` contra fireflies.

## Atualização 07/10/2026 — corrigir defeito da arte-fonte sem redesenhar
O emblema-fonte tinha **dois pontos decorativos desalinhados** (um em y≈0,02, outro em y≈−0,24, não antípodas) e o anel de texto assimétrico. Correção validada pelo usuário como pedido explícito:
- Medir antes de mexer: centro dos círculos por mínimos quadrados, ângulo de cada letra do anel (`atan2` em relação ao centro do aro) e centro vertical da palavra central (bbox das letras).
- Só mover os pontos **colide** com as letras do fim do arco; reabrir lacunas: **rotacionar cada letra** em torno do centro do aro (e escalar ~5% no arco apertado), mapeando centroides linearmente para o novo arco. Pontos viram círculos perfeitos na altura da palavra.
- ⚠️ **Prévia 2D (matplotlib) antes do Blender**: ali achei fragmentos soltos (crescentes finos de resíduo de limiar: 12 de 70 formas) e **errei um índice** (li "30" como "40" e apaguei um "C" de INSTITUICAO). Conferir rótulos pelo bbox/centro, nunca só pela imagem.
- Verso (relevo por mapa) em ângulo rasante mostra "camadas empilhadas": limite do Displace; só para detalhe orgânico.
- Material de verso por máscara de luminância (`ColorRamp` 0,02→0,36 → mistura escuro/prata) × imagem com brilho/contraste (fator 0,7) devolve a modelagem sem a luz embutida; fundo neutro (preto→cinza) exige também ambiente de reflexo **neutro**, ou o metal sai azulado.
Preferência reforçada: [[emblema-institucional-nunca-redesenhado-por-ia]] (alterações só quando pedidas e descritas ao usuário).
