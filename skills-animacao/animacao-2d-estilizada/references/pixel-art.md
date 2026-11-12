# Pixel art

Construa na resolução lógica do sprite/cena, definida pela legibilidade e pelo destino; por exemplo 320×180 ampliado 6× para 1920×1080. Mantenha pixels quadrados e escala inteira com nearest-neighbor. Não reduza uma ilustração suave e a chame automaticamente de pixel art.

Defina uma paleta curta, clusters de pixels e espessura de contorno consistentes. Desenhe poses-chave em camadas/sprites, estabeleça pivôs e uma grade de contato. Se Aseprite não estiver disponível, use editor raster disponível e sequência PNG; verifique alpha e margens na exportação.

Como ponto de partida, use 8–12 novas poses por segundo; ajuste ao movimento. Mantenha câmera e translações alinhadas à grade lógica. Subpixel por mudança de cor é opcional e deve preservar o contorno. Desative interpolação óptica e suavização automática.

Valide em tamanho nativo e ampliado: pixels de mesma dimensão, sem bordas suavizadas, dithering controlado, sem tremor do pivô ou vazamento de alpha. Em loops, compare última e primeira pose em reprodução. Entregue sprite/atlas com ordem, tamanho de célula, pivô e duração por quadro quando solicitado.
