#!/bin/bash
# Renderiza (fundo transparente, RGBA) o giro de cada instituicao: quadrado 1080x1080 (base do horizontal) e vertical 1080x1920.
# Retomavel. TIPO=emblema (moeda-escudo, padrao) | esfera.   uso: TIPO=esfera bash scripts/renderizar_tudo.sh [SIGLAS...]
cd "$(dirname "$0")/.."; RAIZ="C:/Users/<USUARIO>/Documents/Emblemas-Instituicoes-3D"
TIPO=${TIPO:-emblema}; RD=renders; [ "$TIPO" = esfera ] && RD=renders-esfera; export TIPO
B="/c/Program Files/Blender Foundation/Blender 4.5/blender.exe"
SIGS=${@:-PF INSTITUICAO-A PMMG PPMG}
for S in $SIGS; do
  s=$(echo $S | tr A-Z a-z); T=$RD/_trabalho/$S; mkdir -p $T/q $T/v
  echo "[$(date +%T)] $S quadrado"
  "$B" -b blend/$TIPO-$s-3d.blend -P scripts/cycles_gpu.py -P scripts/sem_sobrescrever.py -P scripts/render_alpha.py -o $RAIZ/$T/q/q_ -a > $T/q.log 2>&1
  echo "[$(date +%T)] $S vertical"
  SIG=$S "$B" -b blend/$TIPO-$s-3d.blend -P scripts/cycles_gpu.py -P scripts/sem_sobrescrever.py -P scripts/render_vertical_inst.py -P scripts/render_alpha.py -o $RAIZ/$T/v/v_ -a > $T/v.log 2>&1
  echo "[$(date +%T)] $S pronto"
done
echo FIM
