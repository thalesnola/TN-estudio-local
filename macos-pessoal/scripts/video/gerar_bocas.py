#!/usr/bin/env python3
"""Gera, com o Codex deste Mac (gpt-6.1-terra), variantes de BOCA de um personagem 3D a partir da base.
Entrada: PNG do personagem (corpo inteiro, fundo liso). Saída: pranchas/bocas/<nome>_<estado>.png
Estados: fechada (boca fechada, sorriso suave) e meia (lábios entreabertos, boca pequena). A base original
vale como "aberta". Só serve a pranchas 3D do estúdio (nunca foto real).
Uso: python3 gerar_bocas.py nome=caminho.png [nome=caminho.png ...]"""
import os, sys, subprocess, time
from concurrent.futures import ThreadPoolExecutor
OUT=os.path.expanduser("~/estudio/pranchas/bocas"); os.makedirs(OUT,exist_ok=True)
ESTADOS={
 "fechada":"a boca totalmente FECHADA, num sorriso suave e fechado, sem língua e sem dentes à mostra",
 "meia":"a boca ENTREABERTA (lábios levemente separados), abertura pequena como quem diz uma vogal curta, sem a língua para fora",
 "aberta":"a boca bem ABERTA, como quem fala uma vogal aberta ('a'), com a língua visível dentro da boca, sem pôr a língua para fora",
 "olhos":"os DOIS OLHOS FECHADOS, como num piscar suave (pálpebras fechadas, sem olhar para lugar nenhum), e a boca FECHADA num sorriso suave, sem língua",
}
PROMPT="""Edite a imagem fornecida com a ferramenta nativa de geração/edição de imagens (não escreva código para desenhar).
É o MESMO personagem 3D de animação. Mantenha EXATAMENTE: o mesmo personagem, a mesma pose do corpo e da cabeça, o mesmo ângulo,
o mesmo enquadramento, a mesma escala e posição na imagem, o mesmo fundo liso, a mesma iluminação, as mesmas cores, roupas e acessórios.
Mude SOMENTE isto: {estado}. Todo o resto (sobrancelhas, orelhas, pelos, cabelo, corpo) fica idêntico, nos mesmos pixels sempre que possível.
Sem texto, sem legenda, sem marca d'água. Depois de gerar, copie o arquivo para exatamente este caminho: {out}
Responda apenas com 'ok' e o caminho."""
def roda(t):
    nome,src,est=t; out=f"{OUT}/{nome}_{est}.png"
    if os.path.isfile(out) and os.path.getsize(out)>50000: return (nome,est,"já existe")
    for k in (1,2):
        ini=time.time()
        p=subprocess.run(["codex","exec","-m","gpt-6.1-terra","-s","workspace-write","--skip-git-repo-check","--add-dir",OUT,"-i",src,"-"],
            input=PROMPT.format(estado=ESTADOS[est],out=out),text=True,capture_output=True)
        if os.path.isfile(out) and os.path.getsize(out)>50000: return (nome,est,f"ok {int(time.time()-ini)}s")
    return (nome,est,"FALHOU "+p.stderr[-200:])
if __name__=="__main__":
    itens=[]
    for a in sys.argv[1:]:
        n,s=a.split("=",1)
        for e in ESTADOS: itens.append((n,os.path.expanduser(s),e))
    with ThreadPoolExecutor(2) as ex:
        for r in ex.map(roda,itens): print(*r,flush=True)
