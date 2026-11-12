---
tipo: padrao
tags: [blender, 3d, esfera, emblema, projecao, cycles, glb, medido]
projeto: INSTITUICAO_identidade
atualizado: 2026-10-07
---
# Esfera 3D com emblema em cada hemisfério (frente = instituição, costa = INSTITUICAO)

Veio da rejeição da moeda-escudo ("não ficou legal") em [[escudo-institucional-3d-por-mascara-e-mapa-de-altura]]. Mesma base do padrão [[emblema-instituicao-3d-padrao-v7]] (GIRO, câmera, mundo, luzes). Scripts em `Emblemas-Instituicoes-3D\scripts`: `preparar_esfera.py`, `construir_esfera.py`, `exportar_glb_esfera.py`; pipeline com `TIPO=esfera`.

## Receita
- **Tela quadrada** por sigla: escudo colado no centro de uma tela cujo círculo inscrito (raio = maior distância do contorno ao centro ×1,04) cobre o hemisfério; fora do escudo, metal na cor da moldura.
- **Projeção**: emblema plano em hemisfério precisa de mapa azimutal. Ortográfica (r=sinθ) mantém o emblema "de frente" mas estica o limbo; equidistante (r=θ/90°) agranda o centro 1,57×. Usar a **média** `r=0,5(sinθ+θ/90°)`. Costa vista por trás: espelhar u.
- **Malha**: hemisférios gerados direto em numpy (polo + anéis, 1440×360, leque no polo), relevo embutido nos vértices (amostra bilinear do mapa de altura, 3,5% do raio), UV por vértice. Faixa de metal (toro) no equador cobre a emenda.
- **INSTITUICAO na costa**: campo preto acetinado liso por máscara de luminância (mix escuro/textura) — a textura crua tinha manchas da iluminação embutida que o metal 1 amplificava.
- **GLB**: Decimate 0,30, cor + imagem metal/rugosidade empacotada (G/B) e costa com cor achatada; ~20–25 MB.

## Lições
- `primitive_uv_sphere_add` + loop bmesh sobre 1 milhão de faces travou >5 min; gerar a malha em numpy levou 4 s.
- Câmera do vertical = padrão da moeda de 2 m (esfera tem 2 m): `TIPO=esfera` fixa k=1 em `render_vertical_inst.py`.
