#!/bin/bash
# espera cada sigla ficar pronta no lote e roda o pos-processamento.  TIPO=emblema|esfera
cd "$(dirname "$0")/.."; TIPO=${TIPO:-emblema}; RD=renders; [ "$TIPO" = esfera ] && RD=renders-esfera; export TIPO
for S in ${@:-PF INSTITUICAO-A PMMG PPMG}; do
  until grep -q "$S pronto" $RD/_trabalho/lote.log; do sleep 30; done
  python scripts/posprocessar.py $S > $RD/_trabalho/pos-$S.log 2>&1 && echo "$S pos OK" || echo "$S pos FALHOU"
done
echo FIM-POS
