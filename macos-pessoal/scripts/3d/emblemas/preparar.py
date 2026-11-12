from pathlib import Path as _NolaPath
import sys as _nola_sys
_nola_sys.path.insert(0, str(_NolaPath(__file__).resolve().parents[2]))
from nola_paths import media_root, configure_device, asset_id
"""Prepara, a partir da imagem-fonte (NAO redesenhada), os insumos 3D de um emblema de projeto pessoal:
   contorno do escudo (JSON, metros), textura de cor, mapa de altura 16 bits, mapa de metal/esmalte, circulo inscrito.
   uso: python preparar.py SIGLA   (le fontes/SIGLA.jpg, grava fontes/SIGLA-*.png|json)"""
import sys, json, os
import numpy as np, cv2
from scipy import ndimage as ndi
sig=asset_id(sys.argv[1]); raiz=str(media_root()/"fontes")
img=cv2.imread(os.path.join(raiz,sig+".jpg")); H0,W0=img.shape[:2]
lum=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
# --- mascara: fundo = escuro conectado a borda
T=38
dark=cv2.GaussianBlur(lum,(0,0),2)<T
lab,n=ndi.label(dark)
bord=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))-{0}
bg=np.isin(lab,list(bord))
m=~bg
m=ndi.binary_fill_holes(m)
m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
l2,n2=ndi.label(m); sz=ndi.sum(m,l2,range(1,n2+1)); m=(l2==(1+int(np.argmax(sz)))).astype(np.uint8)
m=cv2.erode(m,np.ones((5,5),np.uint8))          # tira o halo escuro da borda
ys,xs=np.nonzero(m); x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
pad=4; x0=max(0,x0-pad);y0=max(0,y0-pad);x1=min(W0,x1+pad);y1=min(H0,y1+pad)
m=m[y0:y1,x0:x1]; img=img[y0:y1,x0:x1]; lum=lum[y0:y1,x0:x1]; H,W=m.shape
# --- escala mundo: altura 2,10 m, largura limitada a 1,95 m
esc=min(2.10/H,1.95/W); wm,hm=W*esc,H*esc
cx=(np.nonzero(m)[1].mean());
def px2m(x,y): return [round(float((x-W/2)*esc),5),round(float((H/2-y)*esc),5)]   # y para cima
# --- contorno
cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)[:,0,:].astype(np.float32)
k=9; ker=np.ones(k)/k; c=np.stack([np.convolve(np.r_[c[-k:,i],c[:,i],c[:k,i]],ker,'same')[k:-k] for i in (0,1)],1)
c=cv2.approxPolyDP(c.reshape(-1,1,2).astype(np.float32),0.9,True)[:,0,:]
poly=[px2m(x,y) for x,y in c]
# --- circulo inscrito (medalhao do verso)
dt=cv2.distanceTransform(m,cv2.DIST_L2,5); iy,ix=np.unravel_index(np.argmax(dt),dt.shape); rin=dt[iy,ix]*esc
# --- cor de fundo da peca (moda) e rim
lab_=cv2.cvtColor(cv2.GaussianBlur(img,(0,0),3),cv2.COLOR_BGR2LAB).astype(np.float32)
q=(lab_[::6,::6]//12).reshape(-1,3).astype(int); mm=m[::6,::6].reshape(-1)>0; q=q[mm]
key=q[:,0]*10000+q[:,1]*100+q[:,2]; vals,cnt=np.unique(key,return_counts=True); kk=vals[np.argmax(cnt)]
campo=np.array([kk//10000,(kk//100)%100,kk%100])*12+6
w=np.array([float(os.environ.get('NOLA_LUMINANCE_WEIGHT','0.6')),1,1],np.float32)
lb=cv2.GaussianBlur(lab_,(0,0),1.5)
dist_g=np.sqrt((((lb-campo)*w)**2).sum(2))
sm=cv2.resize(lb,None,fx=.25,fy=.25,interpolation=cv2.INTER_AREA)
loc=np.stack([cv2.medianBlur(np.clip(sm[...,i],0,255).astype(np.uint8),45) for i in range(3)],2).astype(np.float32)
loc=cv2.resize(loc,(W,H),interpolation=cv2.INTER_LINEAR)
dist_l=np.sqrt((((lb-loc)*w)**2).sum(2))
dist=dist_g if os.environ.get('NOLA_GLOBAL_DISTANCE')=='1' else np.minimum(dist_g,dist_l*1.4)
lo,hi=float(os.environ.get('NOLA_HEIGHT_LOW','14')),float(os.environ.get('NOLA_HEIGHT_HIGH','34')); elem=np.clip((dist-lo)/(hi-lo),0,1)
# detalhe fino: |alta-frequencia| da luminancia
hp=np.abs(lum-cv2.GaussianBlur(lum,(0,0),9)); det=np.clip(hp/ (np.percentile(hp[m>0],97)+1e-6),0,1)
det=cv2.GaussianBlur(det,(0,0),2.5)
h=np.maximum(elem,0.55*det)
h=cv2.GaussianBlur(h,(0,0),2.2)
# aro externo elevado (moldura)
dd=cv2.distanceTransform(m,cv2.DIST_L2,5)*esc
rim=np.clip((dd-0.004)/0.006,0,1)*np.clip((0.050-dd)/0.012,0,1)
h=np.clip(np.maximum(h*0.85,rim),0,1)*(m>0)
h=cv2.GaussianBlur(h,(0,0),1.2)
# --- metal x esmalte: saturacao alta e matiz fora do dourado
hsv=cv2.cvtColor(cv2.GaussianBlur(img,(0,0),1.5),cv2.COLOR_BGR2HSV).astype(np.float32)
hue=hsv[...,0]*2; sat=hsv[...,1]/255; val=hsv[...,2]/255
ouro=(hue>18)&(hue<62)
esm=np.clip((sat-0.45)/0.25,0,1)*(~ouro)+np.clip((sat-0.78)/0.15,0,1)*ouro
branco=np.clip((val-0.80)/0.10,0,1)*np.clip((0.22-sat)/0.10,0,1)
esm=np.maximum(esm,0.85*branco)
esm=cv2.GaussianBlur(esm.astype(np.float32),(0,0),1.5)
# --- textura: fora da mascara preenche com cor da borda (sem halo preto)
tex=img.copy(); fora=(cv2.dilate(m,np.ones((9,9),np.uint8))==0)
_,ind=ndi.distance_transform_edt(m==0,return_indices=True); tex=img[ind[0],ind[1]]
cv2.imwrite(os.path.join(raiz,f"{sig}-cor.png"),tex)
cv2.imwrite(os.path.join(raiz,f"{sig}-altura16.png"),(h*65535).astype(np.uint16))
cv2.imwrite(os.path.join(raiz,f"{sig}-esmalte.png"),(esm*255).astype(np.uint8))
cv2.imwrite(os.path.join(raiz,f"{sig}-mascara.png"),m*255)
cv2.imwrite(os.path.join(raiz,f"{sig}-mascara-grade.png"),cv2.erode(m,np.ones((7,7),np.uint8))*255)
rimcor=np.median(img[(dd>0.004)&(dd<0.02)].reshape(-1,3),axis=0)[::-1]/255.0
json.dump(dict(sigla=sig,largura_m=float(wm),altura_m=float(hm),esc=float(esc),poly=poly,
  medalhao=dict(x=round((ix-W/2)*esc,4),y=round((H/2-iy)*esc,4),raio=round(float(rin),4)),
  rim_rgb=[round(float(v),4) for v in rimcor],px=[int(W),int(H)]),open(os.path.join(raiz,f"{sig}-contorno.json"),"w"))
prev=np.hstack([cv2.cvtColor((m*255).astype(np.uint8),cv2.COLOR_GRAY2BGR),cv2.cvtColor((h*255).astype(np.uint8),cv2.COLOR_GRAY2BGR),cv2.cvtColor((esm*255).astype(np.uint8),cv2.COLOR_GRAY2BGR)])
cv2.imwrite(os.path.join(raiz,f"{sig}-previa.jpg"),cv2.resize(prev,None,fx=700/prev.shape[1]*1.0,fy=700/prev.shape[1]*1.0))
print(sig,"escudo %.2f x %.2f m"%(wm,hm),"medalhao r=%.3f"%rin,"campo Lab",campo,"rim",rimcor.round(2),"pts",len(poly))
