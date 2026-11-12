# Testes das skills próprias de animação

Execução em Windows, 06/11/2026. Entradas exclusivamente sintéticas; sem geração neural, downloads de modelos ou envio de mídias. Artefatos de teste ficam fora do repositório.

## Resultados

| Verificação | Resultado | O que cobre |
|---|---|---|
| `python -m unittest discover -s tests -v` | 2 testes aprovados | Metadados de descoberta, links existentes e contidos na skill, receitas acessíveis, formatos de distribuição e ausência de caminhos pessoais |
| `quick_validate.py` da skill-creator, para ambas as skills | Aprovadas | Frontmatter e nomenclatura; executado com Python em modo UTF-8 e PyYAML disponível |
| Pixel art via FFmpeg/ffprobe | Aprovado | Duas poses sintéticas 8×8 a 12 poses/s, ampliadas para 32×32 com nearest-neighbor e entregues em quatro quadros a 24 fps. Comparação RGB integral após decodificar FFV1: escala e holds exatos |
| Blender 4.5.10 LTS / Cycles CPU | Aprovado | Cena sintética salva em `.blend`, render PNG 64×64 não uniforme, seis faces com shading plano; quadro inspecionado visualmente |
| Revisão independente das instruções | Realizada | Cenários de pixel art com identidade exata, PS2 com cena editável, risografia com texto exato e produção local sob sigilo |

## Reprodução do smoke local

Com Blender, FFmpeg e ffprobe disponíveis, na raiz do repo:

```powershell
python tests/smoke_media.py --blender 'C:/Tools/audio-visual/Blender-4.5/blender.exe' --output '../smoke-animacao'
```

Substitua o executável pela instalação real. A pasta de saída deve ser nova: o script recusa sobrescrita. O script não precisa de Pillow, PyYAML, GPU, navegador, rede ou serviço de geração. Produz `results.json`, frames sintéticos, vídeo lossless, cena Blender e render para inspeção. Falhas de subprocessos ou invariantes encerram com erro.

## Limites

Os testes de integração comprovam dois percursos técnicos mínimos e a distribuição das instruções. Não comprovam qualidade artística dos dez estilos, comportamento de todas as ferramentas MCP, exportação de todos os formatos, nem uma produção completa de animação. ArtCraft, WanGP, ImageGen, HyperFrames e plugins comerciais não foram executados nesta atualização. As receitas exigem descoberta de capacidades e revisão visual durante cada produção real.
