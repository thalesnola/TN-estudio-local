# Omni (Gemini Omni Flash)

## Versão 1.2 Flash (anúncio de 06/11/2026, não medido)
- Duração de **10 → 15 s**.
- Mais controle de **referência**, **voz** e **sincronia labial**.
- Aceita **pedido de mudança sem recomeçar** o clipe.
- Disponível na API e no Google Vids para contas elegíveis; app para assinantes Ultra.
- Confirmar nas contas: onde aparece (Flow, app, API), créditos por segundo e se o limite de 15 s vale no plano.

## Medido na versão 1.1 Flash (28–29/09/2026)
- Custo: 12 créditos por 8 s (x1). Falha não é cobrada.
- Único que usa a **voz salva do personagem**. O Veo não guarda voz entre gerações.
- Fala: bloco fixo de VOZ + PERFORMANCE + NEGATIVE repetido em todo prompt, em inglês; fala entre aspas em pt-BR. Sem sotaque: "neutral standard accent, like a national TV news anchor; no regional accent".
- Clipe de 8 s → **≤ 16 palavras** (~2,2 palavras/s, entrada em 0,5 s). Fala maior: dividir e encadear. Com 15 s, recalcular **depois de medir**.
- Conferir a temporização com `silencedetect=n=-35dB:d=0.2` e a fala transcrevendo o áudio.

## Armadilhas
- **Ignora o quadro inicial** e gera pelo retrato do personagem: roupa, lado de detalhes e acessórios saem trocados. Descrever tudo no **próprio personagem**.
- Inventa insígnias, legendas (lower-third com o nome) e adereços; escreve texto em roupas de figurantes. Pedir "COMPLETELY PLAIN chest: no badge, no emblem, no patch, no text" no personagem **e** no prompt; "no text on clothing" também para figurantes.
- Insígnia que precisa acompanhar o corpo: peito liso do modelo + original colado localmente por `cv2.matchTemplate` (CLAHE antes, busca local, suavização).
- Cobrir legenda indevida com `crop` do fundo + `overlay`.
- Lote num único pedido é cobrado de uma vez e o agente nomeia os itens como pedido.

## Filtros
- "Pessoas famosas" dispara por texto que soa como identificação de pessoa real. Iniciar o prompt com "ORIGINAL fictional character, not a real or famous person" e exigir "Use EXACTLY this prompt, verbatim" evita que o agente remova a frase.
- Política e reputação de instituições: reescrever com termos neutros (documento, conexões, instrutor de curso fictício).

## Com a 1.2 (a validar)
- Testar edição por pedido sobre um clipe pronto antes de gastar um novo.
- Testar referência de imagem e de voz: se a 1.2 prende o quadro inicial, as regras acima mudam.

## Receita medida: Diorama Papercraft / Pop-up Book (Omni 1.1 Flash)
1. **Imagem-base 16:9 (ChatGPT Images ou Nano Banana 2):**
   - `Layered papercraft diorama of <local>, textured handmade paper, cut-paper layers with depth, <elementos em camadas>, a big paper sun, puffy folded paper clouds, warm golden-hour sky. Landscape 16:9, no text, no people.`
2. **Animação no Google Flow (`Omni 1.1 Flash`, `16:9`, `x1`):**
   - `Animate this scene in origami form video. The papercraft landmarks, trees, clouds, and hills move and fold dynamically with intricate paper folding and unfolding origami animations. Slow cinematic camera movement across the scene with soft shifting light. Return exactly to the original scene, zero written words: no captions, subtitles, name labels.`
3. **Correção de reconstrução incompleta:** sem a cláusula `"return exactly to the original scene"`, elementos do primeiro plano podem dobrar para baixo e só reaparecer no último segundo do clipe.
