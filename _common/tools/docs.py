# 등기부 페이지 렌더 + 개인정보(이름·주민번호·동호수·고유번호) 모자이크
import re, subprocess, html
from PIL import Image, ImageFilter

S = 3.0  # 216dpi = 72*3
NAMES = set('배강호 김영미 김건호 이성규 왕지연 김현상 성락수 성인모 성규모 김형찬 임현우 김인식 김일열 곽병학 박준형 최순조 이병익 김남옥 이종철'.split())
PAT = [r'\d{6}-\*', r'^\d{6}-', r'\d+동', r'\d+호', r'제\d+층', r'^\d+-\d+$', r'\d{4}-\d{4}-\d{6}', r'^\d+-\d+\)?$']


def words(pdf, page):
    t = open(pdf.replace('.pdf', '.html'), encoding='utf-8').read()
    pg = t.split('<page ')[page]
    out = []
    for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', pg):
        x0, y0, x1, y1 = map(float, m.groups()[:4]); out.append((x0, y0, x1, y1, html.unescape(m.group(5))))
    return out


def sensitive(w):
    if '동의' in w: return False
    if any(n in w for n in NAMES): return True
    return any(re.search(p, w) for p in PAT)


def render(pdf, page, out):
    subprocess.run(['pdftoppm', '-r', '216', '-f', str(page), '-l', str(page), '-png', '-singlefile', pdf, out[:-4]], check=True)
    im = Image.open(out).convert('RGB')
    for x0, y0, x1, y1, w in words(pdf, page):
        if sensitive(w):
            b = (int(x0 * S) - 4, int(y0 * S) - 3, int(x1 * S) + 4, int(y1 * S) + 3)
            reg = im.crop(b)
            sm = reg.resize((max(1, reg.width // 14), max(1, reg.height // 14)))
            im.paste(sm.resize(reg.size, Image.NEAREST).filter(ImageFilter.GaussianBlur(3)), b)
    if page == 1:  # 바코드(고유번호) 가림
        b = (1270, 395, 1750, 480); reg = im.crop(b)
        im.paste(reg.resize((24, 6)).resize(reg.size).filter(ImageFilter.GaussianBlur(4)), b)
    im.save(out)
    return im


if __name__ == '__main__':
    import sys
    render(sys.argv[1], int(sys.argv[2]), sys.argv[3])
