import re, html, subprocess
from PIL import Image, ImageFilter
RL='/home/claude/rl'; S=3.0
NAMES='김수영 김하나 김희룡 노상모 박병철 박은숙 배을순 서한준 신원혜 윤성운 이경진 이경환 이민자 이상권 이시형 이향숙 정휴영 조한 최수정 하효'.split()
PAT=[r'\d{6}-\*', r'^\d{6}-', r'\d+동', r'\d+호', r'제\d+층', r'^\d+층', r'\d{4}-\d{4}-\d{6}', r'^\d+-\d+\)?,?$', r'^\d{3}-\d{3,4}$']
def words(pdf, page):
    pg=open(f'{RL}/{pdf}.html',encoding='utf-8').read().split('<page ')[page]
    return [(*map(float,m.groups()[:4]), html.unescape(m.group(5))) for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>',pg)]
def blur_box(im,b):
    reg=im.crop(b); sm=reg.resize((max(1,reg.width//14),max(1,reg.height//14)))
    im.paste(sm.resize(reg.size,Image.NEAREST).filter(ImageFilter.GaussianBlur(3)),b)
ADDR=['체육관로','한숲','수택동','관악로','봉천동','관전로즈','천호대로','장안동','로얄빌라트','호현로','소사본동','소사구','청수로','용현동','건영아파트','의정부시','관악구','동대문구','부천시','수성구']
def page(pdf,p):
    base=f'{RL}/pg_{pdf}_{p}'
    subprocess.run(['pdftoppm','-r','216','-f',str(p),'-l',str(p),'-png','-singlefile',f'{RL}/{pdf}.pdf',base],check=True)
    im=Image.open(base+'.png').convert('RGB')
    ws=words(pdf,p); hot=set()
    for k,(x0,y0,x1,y1,w) in enumerate(ws):
        if any(a in w for a in ADDR):
            for j in range(k,min(k+3,len(ws))):
                if abs(ws[j][1]-y0)<3: hot.add(j)
    for k,(x0,y0,x1,y1,w) in enumerate(ws):
        if k in hot: blur_box(im,(int(x0*S)-4,int(y0*S)-3,int(x1*S)+4,int(y1*S)+3)); continue
        if '대부' in w:
            blur_box(im,(int(x0*S)-4,int(y0*S)-3,int(x1*S)+4,int(y1*S)+3)); continue
        nm=next((n for n in NAMES if n in w),None)
        if nm:
            i=w.index(nm); cw=(x1-x0)/len(w)
            blur_box(im,(int((x0+i*cw)*S)-3,int(y0*S)-3,int((x0+(i+len(nm))*cw)*S)+3,int(y1*S)+3))
        elif any(re.search(q,w) for q in PAT):
            blur_box(im,(int(x0*S)-4,int(y0*S)-3,int(x1*S)+4,int(y1*S)+3))
    if p==1: blur_box(im,(1270,395,1750,480))
    return im
if __name__=='__main__':
    import sys
    page(sys.argv[1],int(sys.argv[2])).save(sys.argv[3])
