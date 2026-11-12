---
tipo: padrao
tags: [blender, 3d, emblema, escudo, cycles, glb, alfa, medido]
projeto: INSTITUICAO_identidade
atualizado: 2026-10-07
---
# Escudo institucional 3D a partir de imagem renderizada (frente = escudo, verso = medalhão INSTITUICAO)

Extensão de [[emblema-instituicao-3d-padrao-v7]] e [[relevo-3d-de-emblema-no-blender-por-mapa-de-altura]] para emblemas multicoloridos (PF, INSTITUICAO-A, PMMG, PPMG) onde extrudar letras não serve. Arte nunca redesenhada: [[emblema-institucional-nunca-redesenhado-por-ia]]. Pacote em `C:\Users\<USUARIO>\Documents\Emblemas-Instituicoes-3D\` (scripts `preparar.py`, `construir.py`, `renderizar_tudo.sh`, `posprocessar.py`, `exportar_glb.py`).

## Receita
- **Máscara**: fundo = escuro (lum<38 após blur) conectado à borda; preencher furos, maior componente, erodir 5 px (tira halo). Contorno suavizado + approxPolyDP → JSON em metros (altura 2,10 m).
- **Corpo**: polígono extrudado (tessellate_polygon) 0,11 m + Bevel; frente com a imagem por UV planar; verso preto (MAT-Campo) com medalhão INSTITUICAO reaproveitado do mestre (Aro, FaceCampo, FaceLetras), escala 0,90 × raio do círculo inscrito (distanceTransform).
- **Relevo**: grade 2 mm recortada pela máscara erodida (numpy, ~700 mil vértices) 1,5 mm acima da tampa + Displace por mapa 16 bits (5 cm). Altura = distância de cor ao "campo" (moda em Lab) com min contra mediana local (mata gradiente de iluminação) + alta frequência + moldura. PMMG usa só a distância global (campo preto); INSTITUICAO-A limiares maiores.
- **Material**: cor da imagem; metal×esmalte por saturação/matiz (esmalte = sat alta fora do dourado, + branco puro); coat leve. Brilho +0,10 deixou tudo pastel/rosa; ficou Bright 0,02, Contraste 0,15.
- **Vídeos**: renderizar UMA vez com fundo transparente (quadrado 1080 e vertical 1080×1920 com câmera proporcional à largura) e compor o degradê depois no ffmpeg (fundo = mundo do mestre renderizado sem geometria, 16 bits → 8 com dithering). Horizontal 1920×1080 = quadrado centralizado. Metade dos renders.
- **GLB**: material Principled simples com cor + imagem empacotada (G rugosidade, B metal) via Separate Color; Decimate 0,35 no relevo; ~15–23 MB.

## Lições de erro
- Blender embutido **não tem cv2/scipy**: gerar máscaras no Python do sistema e só ler PNG no Blender.
- `-o renders/...` relativo com bash virou `C:\renders`: usar caminho absoluto Windows. `pkill` não existe no Git Bash; matar por WINPID (`ps aux`, 4ª coluna + `taskkill //PID`). Relançar lote sem matar o laço antigo gera dois Blender disputando a GPU.
- `bpy.ops.render` dimensões: `dimensions` de objeto não inclui a escala do pai (medi anel como 1,5 m, era 2,04): conferir por bound_box × matrix_world.
- Tempo medido (RTX PRO 1000, 128 amostras): quadrado ~9 s/quadro, vertical ~14 s.
