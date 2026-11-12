# Emblemas 3D das instituições — PF · INSTITUICAO-A · PMMG · PPMG

Mesmo padrão do emblema INSTITUICAO v7 (`Documents\Emblema-INSTITUICAO-Padrao`): moeda 3D girando 360° em laço (144 quadros, 24 fps, 6 s),
Cycles, câmera fixa com inclinação oscilante, ambiente neutro.
**Frente = escudo da instituição. Verso = medalhão INSTITUICAO · [UNIDADE]** (geometria extrudada do padrão v7, prata sobre preto acetinado).

## O que há para cada sigla (`renders/<SIGLA>/`)
| Arquivo | Uso |
|---|---|
| `emblema-<sigla>-giro-horizontal-1920x1080.mp4` | Horizontal, fundo degradê preto→cinza |
| `emblema-<sigla>-giro-vertical-1080x1920.mp4` | Vertical (stories/reels), fundo degradê |
| `emblema-<sigla>-giro.gif` / `-whatsapp.mp4` | Quadrado leve (480 px GIF; 720 px MP4 sem áudio) |
| `transparente/…-horizontal-alpha.mov` / `.webm` / `horizontal-png/` | Fundo transparente 1920×1080: ProRes 4444 (editores), VP9 com alfa (Chrome/Edge/DaVinci), sequência PNG RGBA |
| `transparente/…-vertical-alpha.mov` / `.webm` / `vertical-png/` | Idem, 1080×1920 |
| `transparente/…-alpha-previa.mp4` | Só para assistir (alfa sobre cinza); o Windows não abre o `.mov` ProRes |

Modelos: `modelo-3d/emblema-<sigla>-3d.glb` (PowerPoint 3D, web, Unity, Blender; ~15–23 MB, ~550 mil polígonos; sem escovado/anisotropia).
Mestres editáveis: `blend/emblema-<sigla>-3d.blend` (Blender 4.5, texturas empacotadas).
Arte-fonte e insumos (máscara, mapa de altura, esmalte): `fontes/`.

## Como foi feito
- Escudo extrudado a partir da silhueta da imagem (0,11 m, chanfro), imagem original como textura (**nenhum desenho refeito**), relevo de 5 cm por mapa de altura derivado das cores/contornos da própria imagem, metal × esmalte por saturação.
- O degradê é o do mundo do mestre INSTITUICAO, composto depois sobre os quadros com fundo transparente (um render serve aos dois fundos).
- O horizontal é o quadro quadrado 1080 centralizado em 1920×1080; o vertical tem render próprio, com a câmera mais próxima em proporção à largura do escudo.

## Refazer
```bash
python scripts/preparar.py PF                       # máscara, altura, esmalte, contorno (Python do sistema, usa OpenCV)
blender -b blend/_mestre-instituicao.blend -P scripts/construir.py -- PF   # copiar antes o mestre INSTITUICAO v7 para blend/_mestre-instituicao.blend
bash scripts/renderizar_tudo.sh PF                  # quadros RGBA (retomável)
python scripts/posprocessar.py PF                   # mp4, gif, mov, webm, png
blender -b blend/emblema-pf-3d.blend -P scripts/exportar_glb.py -- PF
blender -b -P scripts/verificar_glb.py -- PF pasta  # confere o GLB num Blender limpo
```
Fundos do degradê: `scripts/so_fundo.py` (ver `renders/_trabalho/fundos`).

## Limites
- O relevo vem de mapa de altura estimado da imagem: laurel dourado sobre fundo dourado (INSTITUICAO-A) tem relevo suave; em ângulo rasante pode aparecer o efeito de "camadas".
- A resolução da textura é a da imagem-fonte (INSTITUICAO-A: 1024 px, mais macia que as demais).
- O GLB do verso fica prata lisa (o escovado do `.blend` não exporta).
- Não testado em WhatsApp/Instagram reais.
