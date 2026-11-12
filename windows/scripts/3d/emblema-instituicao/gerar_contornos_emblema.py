"""Gera os contornos corrigidos do emblema frontal (letras, aros, pontos) a partir da imagem-fonte.
Reproduz o pipeline do padrao INSTITUICAO: mascara por limiar -> remove faixas dos aros -> contornos ->
remove fragmentos soltos -> reabre lacunas do anel de texto -> pontos alinhados a palavra central.
Saida: emblema-contornos3.json (lido pelo Blender para extrudar). Requer: numpy scipy opencv-python pillow."""
import json, math, numpy as np, cv2
from PIL import Image
from scipy.ndimage import gaussian_filter as gf, median_filter
SRC="../fontes/emblema-3d-unidade-mg.png"          # imagem-fonte (NUNCA redesenhar)
C=(-0.0090,0.0405); RINGS=[(0.6403,0.6745),(0.8636,0.9104)]   # centro e aros medidos por minimos quadrados
DROP={66,65,61,58,35,33,5,13,16,30,29,51}          # fragmentos soltos (indices da extracao com estes parametros)
DOTS={20,32}; INSTITUICAO_YC=0.0463; R_DOT=0.7695; DOT_R=0.0323
a=gf(median_filter(np.asarray(Image.open(SRC).convert("L"),dtype=np.float32)/255,size=3),0.8)
a2=cv2.resize(a,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC); m=(a2>0.435).astype(np.uint8)*255
H,W=m.shape; yy,xx=np.mgrid[0:H,0:W]; X=(xx/W-0.5)*2; Y=(0.5-yy/H)*2; rr=np.hypot(X-C[0],Y-C[1])
for lo,hi in RINGS: m[(rr>lo-0.004)&(rr<hi+0.004)]=0
m[rr>0.935]=0
cs,h=cv2.findContours(m,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE); h=h[0]
conv=lambda c:[[round((x/W-0.5)*2,5),round((0.5-y/H)*2,5)] for x,y in cv2.approxPolyDP(c,1.0,True)[:,0,:].astype(float)]
S=[]
for i,c in enumerate(cs):
    if h[i][3]!=-1 or cv2.contourArea(c)<30: continue
    holes=[];k=h[i][2]
    while k!=-1:
        if cv2.contourArea(cs[k])>=12: holes.append(conv(cs[k]))
        k=h[k][0]
    S.append([conv(c),holes])
C=np.array(C); ang=lambda p:math.degrees(math.atan2(p[1]-C[1],p[0]-C[0]))
info={}
for i,(o,hh) in enumerate(S):
    c=np.array(o).mean(0)
    if i in DROP or i in DOTS: continue
    if 0.68<np.hypot(*(c-C))<=0.83: info[i]=(c,ang(c))
up=[i for i,(c,a_) in info.items() if -10<a_<175]; lo=[i for i in info if i not in up]
u0=min(info[i][1] for i in up); u1=max(info[i][1] for i in up); lm=(min(info[i][1] for i in lo)+max(info[i][1] for i in lo))/2
newang=lambda i:(11.2+(info[i][1]-u0)*(169.5-11.2)/(u1-u0)) if i in up else -90+(info[i][1]-lm)*1.12
def xf(poly,cen,s,da):
    p=np.array(poly);p=cen+s*(p-cen);t=math.radians(da);R=np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
    return (C+(p-C)@R.T).round(5).tolist()
out=[]
for i,(o,hh) in enumerate(S):
    if i in DROP or i in DOTS: continue
    if i in info:
        cen,a0=info[i]; da=newang(i)-a0; s=0.95 if i in up else 1.0
        out.append([xf(o,cen,s,da),[xf(x,cen,s,da) for x in hh]])
    else: out.append([o,hh])
dx=R_DOT*math.cos(math.asin((INSTITUICAO_YC-C[1])/R_DOT))
for sg in (-1,1):
    cx=C[0]+sg*dx; out.append([[[round(cx+DOT_R*math.cos(2*math.pi*k/48),5),round(INSTITUICAO_YC+DOT_R*math.sin(2*math.pi*k/48),5)] for k in range(48)],[]])
json.dump({"shapes":out,"center":list(C),"rings":RINGS},open("../fontes/emblema-contornos3.json","w")); print(len(out),"formas")
