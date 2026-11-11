# 쇼츠: 주담대 금리 금융사별 비교 (5대 은행 고정·변동 / 생보사) — 2026-11-11
# 스타일: 분양플랜식 풀스크린 실사(Unsplash) + 외곽선 자막 + 꿀담한입식 TOP3 금리 카드
# 사용: python3 make_rate.py ig|yt [scene번호...] / python3 make_rate.py ig|yt build
import sys, os, re, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

V = sys.argv[1]
BUILD = 'build' in sys.argv[2:]
ONLY = [int(x) for x in sys.argv[2:] if x.isdigit()]
W, H, FPS = 1080, 1920, 30
NAVY = (20, 33, 61); YEL = (255, 201, 40); WHITE = (255, 255, 255); RED = (232, 65, 58)
GRAY = (110, 120, 140); SKY = (120, 215, 255); GREEN = (52, 222, 150)
TOOLS = os.path.dirname(os.path.abspath(__file__))
FD = f'{TOOLS}/../fonts'; BLACK = f'{FD}/Pretendard-Black.otf'; BOLD = f'{FD}/Pretendard-ExtraBold.otf'
IMG = f'{TOOLS}/../../_raw/2026-11-11_rate-compare'
OUT = f'/home/claude/rate/out_{V}'; os.makedirs(OUT, exist_ok=True)
HANDLE = '@ltv_lab_kr' if V == 'yt' else '@ltv.lab'
_fc = {}
def F(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]
ease = lambda x: 1 - (1 - max(0, min(1, x))) ** 3
COL = {'y': YEL, 'r': (255, 92, 80), 'c': SKY, 'g': GREEN, 'w': WHITE}


def segs(s, base):
    return [(m.group(3), base) if m.group(3) else (m.group(2), COL[m.group(1)])
            for m in re.finditer(r'\[([a-z])\](.*?)\[/\]|([^\[]+)', s)]


def otext(d, cx, y, s, path, size, maxw, base=WHITE, stroke=None, anchor='c'):
    """외곽선 자막. [y]노랑[/] [r]빨강[/] [c]하늘[/] [g]초록[/]"""
    sg = segs(s, base)
    while size > 24 and sum(d.textlength(a, font=F(path, size)) for a, _ in sg) > maxw: size -= 2
    f = F(path, size); tw = sum(d.textlength(a, font=f) for a, _ in sg)
    x = cx - tw / 2 if anchor == 'c' else cx
    sw = stroke if stroke is not None else max(3, size // 11)
    for a, c in sg:
        d.text((x + 3, y + 5), a, font=f, fill=(0, 0, 0, 150), stroke_width=sw, stroke_fill=(0, 0, 0, 150))
        d.text((x, y), a, font=f, fill=c, stroke_width=sw, stroke_fill=(0, 0, 0, 255)); x += d.textlength(a, font=f)
    return f


def with_alpha(L, a):
    if a >= 1: return L
    r, g, b, al = L.split(); return Image.merge('RGBA', (r, g, b, al.point(lambda v: int(v * a))))


# ---------- 배경: 풀스크린 실사 + 켄번스 + 상/하 그라데이션 ----------
_grad = None
def grad():
    global _grad
    if _grad is None:
        g = Image.new('L', (1, H))
        for y in range(H):
            top = max(0, 1 - y / 700) * 200; bot = max(0, (y - 900) / 1020) * 215
            g.putpixel((0, y), int(min(235, top + bot + 40)))
        _grad = Image.merge('RGBA', [Image.new('L', (W, H), 0)] * 3 + [g.resize((W, H))])
    return _grad


_src = {}
def bg(name, t, dur, dirn=1, blur=0):
    key = (name, blur)
    if key not in _src:
        im = Image.open(f'{IMG}/{name}.jpg').convert('RGB').resize((W + 120, H + 214))
        if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
        _src[key] = im
    src = _src[key]; z = 1 + 0.07 * t / dur
    cw, ch = src.width / z, src.height / z
    x0 = (src.width - cw) / 2 + dirn * (src.width - cw) * 0.35; y0 = (src.height - ch) / 2
    fr = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR).convert('RGBA')
    fr.alpha_composite(grad()); return fr


# ---------- 공통 레이어 ----------
def header(d, chip, lines, y0=150):
    if chip:
        cf = F(BLACK, 40); cw = d.textlength(chip, font=cf)
        d.rounded_rectangle(((W - cw) / 2 - 28, y0, (W + cw) / 2 + 28, y0 + 64), 32, fill=YEL)
        d.text(((W - cw) / 2, y0 + 5), chip, font=cf, fill=NAVY)
    y = y0 + 90
    for s in lines:
        f = otext(d, W / 2, y, s, BLACK, 92, W - 100); y += f.size + 22
    return y


def subtitle(d, lines, y=1110):
    for s in lines:                       # 오른쪽 버튼 구간 피해 왼쪽 중심(470)
        f = otext(d, 470, y, s, BLACK, 62, 840); y += f.size + 26
    return y


def foot(d, s, y=1395):
    f = F(BOLD, 28); tw = d.textlength(s, font=f)
    d.text((470 - tw / 2, y), s, font=f, fill=(225, 230, 240), stroke_width=2, stroke_fill=(0, 0, 0))


def handle(d):
    f = F(BOLD, 30); tw = d.textlength(HANDLE, font=f)
    d.rounded_rectangle((44, 1460, 44 + tw + 40, 1512), 26, fill=(20, 33, 61, 200))
    d.text((64, 1466), HANDLE, font=f, fill=WHITE)


MEDAL = [(255, 196, 0), (176, 186, 200), (205, 127, 50)]
def card(title, rows, extra, t, t0=0.35, step=0.35, y0=430):
    """rows: [(이름, 금리문자열, 범위문자열)] 3개. 위→아래 순차 슬라이드"""
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    x0, x1 = 60, 1020; rh = 132; y1 = y0 + 92 + rh * 3 + (70 if extra else 16)
    d.rounded_rectangle((x0 + 6, y0 + 12, x1 + 6, y1 + 12), 36, fill=(0, 0, 0, 90))
    d.rounded_rectangle((x0, y0, x1, y1), 36, fill=(255, 255, 255, 240))
    d.rounded_rectangle((x0, y0, x1, y0 + 92), 36, fill=NAVY); d.rectangle((x0, y0 + 50, x1, y0 + 92), fill=NAVY)
    tf = F(BLACK, 46); d.text(((x0 + x1) / 2 - d.textlength(title, font=tf) / 2, y0 + 18), title, font=tf, fill=WHITE)
    for k, (nm, rate, rng) in enumerate(rows):
        p = ease((t - t0 - k * step) / 0.3)
        if p <= 0: continue
        R = Image.new('RGBA', (x1 - x0, rh)); r = ImageDraw.Draw(R)
        cy = rh // 2
        r.ellipse((30, cy - 34, 98, cy + 34), fill=MEDAL[k]); nf = F(BLACK, 44)
        r.text((64 - r.textlength(str(k + 1), font=nf) / 2, cy - 28), str(k + 1), font=nf, fill=WHITE)
        r.text((126, cy - 46), nm, font=F(BLACK, 54), fill=NAVY)
        r.text((128, cy + 18), rng, font=F(BOLD, 30), fill=GRAY)
        num, pct = F(BLACK, 96), F(BLACK, 54); col = RED if k == 0 else NAVY
        pw = r.textlength('%', font=pct); nw = r.textlength(rate, font=num)
        xr = (x1 - x0) - 40
        r.text((xr - pw, cy - 4), '%', font=pct, fill=col); r.text((xr - pw - nw - 4, cy - 56), rate, font=num, fill=col)
        if k < 2: r.line((30, rh - 2, (x1 - x0) - 30, rh - 2), fill=(225, 229, 236), width=2)
        L.alpha_composite(with_alpha(R, p), (x0 + int(60 * (1 - p)), y0 + 92 + k * rh))
    if extra:
        pe = ease((t - t0 - 3 * step) / 0.3)
        if pe > 0:
            ef = F(BOLD, 34); ew = d.textlength(extra, font=ef)
            d.text(((x0 + x1) / 2 - ew / 2, y1 - 56), extra, font=ef, fill=GRAY + (int(255 * pe),))
    return L


# ---------- 장면 ----------
SC = []
def scene(f): SC.append(f); return f


@scene
def s1():
    dur = 3.4
    def draw(t):
        L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
        header(d, '2026.11.10 기준', ['주담대 금리', '[y]어디가 제일 쌀까?[/]'], y0=300)
        if t > 0.6: subtitle(d, ['은행 vs 보험사', '고정 vs 변동 [y]싹 다 비교[/]'], y=1060)
        handle(d); return L
    return dur, 'c1', 1, draw, [(4, 0.6)]


@scene
def s2():
    dur = 5.0
    rows = [('신한은행', '4.38', '4.38~5.79%'), ('NH농협은행', '4.54', '4.54~6.34%'), ('하나은행', '4.70', '4.697~5.897%')]
    def draw(t):
        L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
        header(d, None, ['[y]①[/] 은행 [y]5년 고정[/]'], y0=170)
        L.alpha_composite(card('5대 은행 고정형 최저금리 TOP3', rows, '그 외  KB국민 4.85% · 우리 4.88%', t))
        d = ImageDraw.Draw(L)
        if t > 1.7: subtitle(d, ['고정은 [y]신한은행[/]이 제일 낮아요'], y=1150)
        foot(d, '※ 5년 혼합·주기형, 금리 하단 기준 (11/10)'); handle(d); return L
    return dur, 'c9', -1, draw, [(4, 0.35), (4, 0.7), (4, 1.05), (5, 1.7)]


@scene
def s3():
    dur = 5.0
    rows = [('NH농협은행', '4.38', '4.38~6.48%'), ('신한은행', '4.42', '4.42~5.83%'), ('KB국민은행', '4.64', '4.64~6.06%')]
    def draw(t):
        L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
        header(d, None, ['[y]②[/] 은행 [y]변동금리[/]'], y0=170)
        L.alpha_composite(card('5대 은행 변동형 최저금리 TOP3', rows, '그 외  하나 4.73% · 우리 4.87%', t))
        d = ImageDraw.Draw(L)
        if t > 1.7: subtitle(d, ['변동은 [y]농협은행[/]이 1등'], y=1150)
        foot(d, '※ 6개월 변동형(코픽스·금융채), 금리 하단 기준 (11/10)'); handle(d); return L
    return dur, 'c8', 1, draw, [(4, 0.35), (4, 0.7), (4, 1.05), (5, 1.7)]


@scene
def s4():
    dur = 4.8
    def draw(t):
        L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
        header(d, '근데 요즘 이상한 일', ['[r]변동이 고정보다[/]', '[r]더 비싸졌어요[/]'], y0=170)
        x0, x1, y0 = 60, 1020, 560
        p = ease((t - 0.5) / 0.35)
        if p > 0:
            C = Image.new('RGBA', (W, H)); c = ImageDraw.Draw(C)
            c.rounded_rectangle((x0, y0, x1, y0 + 400), 36, fill=(255, 255, 255, 240))
            c.text((100, y0 + 30), '5대 은행 금리 상단', font=F(BLACK, 40), fill=NAVY)
            for k, (lb, v, col, ln) in enumerate((('고정형', '6.34%', NAVY, 0.80), ('변동형', '6.48%', RED, 0.82))):
                yy = y0 + 120 + k * 130; bw = int((700) * ln * ease((t - 0.7 - k * 0.3) / 0.5))
                c.text((100, yy + 8), lb, font=F(BLACK, 46), fill=NAVY)
                if bw > 0:
                    c.rounded_rectangle((280, yy, 280 + bw, yy + 76), 16, fill=col)
                    c.text((280 + bw - 190, yy + 6), v, font=F(BLACK, 56), fill=WHITE)
            c.text((100, y0 + 340), '하단은 둘 다 4.38%로 같아요', font=F(BOLD, 34), fill=GRAY)
            L.alpha_composite(with_alpha(C, p))
        d = ImageDraw.Draw(L)
        if t > 1.9: subtitle(d, ['은행채 5년물이 한 달 새', '[y]0.46%p[/] 떨어져서 고정만 내려감'], y=1080)
        foot(d, '※ 은행채 5년물 4.514%(10/1) → 4.057%(11/9)'); handle(d); return L
    return dur, 'c11', -1, draw, [(4, 0.7), (4, 1.0), (5, 1.9)]


@scene
def s5():
    dur = 5.0
    rows = [('동양생명', '4.87', '4.87%'), ('NH농협생명', '5.70', '5.70~6.10%'), ('삼성생명', '5.71', '5.71~7.21%')]
    def draw(t):
        L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
        header(d, None, ['[y]③[/] 보험사 [y]고정금리[/]'], y0=170)
        L.alpha_composite(card('생명보험사 고정형 최저금리 TOP3', rows, '그 외  하나생명 5.92% · 교보생명 6.06%', t))
        d = ImageDraw.Draw(L)
        if t > 1.7: subtitle(d, ['보험사는 [y]동양생명[/]이 최저'], y=1150)
        foot(d, '※ 생보협회 11월 공시 · 아파트·분할상환 · 신규 취급 여부는 회사별 상이'); handle(d); return L
    return dur, 'c12', 1, draw, [(4, 0.35), (4, 0.7), (4, 1.05), (5, 1.7)]


@scene
def s6():
    dur = 5.2
    def draw(t):
        L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
        header(d, '한눈에 비교', ['이번 달은 [y]은행이 더 싸요[/]'], y0=170)
        p = ease((t - 0.4) / 0.35)
        if p > 0:
            C = Image.new('RGBA', (W, H)); c = ImageDraw.Draw(C); y0 = 470
            for k, (x, tag, tc, rate, who) in enumerate(((60, '은행 최저(고정)', NAVY, '4.38%', '신한은행'), (560, '보험사 최저(고정)', (90, 100, 120), '4.87%', '동양생명'))):
                c.rounded_rectangle((x, y0, x + 460, y0 + 330), 32, fill=(255, 255, 255, 240))
                c.rounded_rectangle((x, y0, x + 460, y0 + 76), 32, fill=tc); c.rectangle((x, y0 + 40, x + 460, y0 + 76), fill=tc)
                tf = F(BLACK, 38); c.text((x + 230 - c.textlength(tag, font=tf) / 2, y0 + 14), tag, font=tf, fill=WHITE)
                nf = F(BLACK, 104); c.text((x + 230 - c.textlength(rate, font=nf) / 2, y0 + 100), rate, font=nf, fill=RED if k == 0 else NAVY)
                wf = F(BOLD, 40); c.text((x + 230 - c.textlength(who, font=wf) / 2, y0 + 240), who, font=wf, fill=GRAY)
            vf = F(BLACK, 56); c.ellipse((490, y0 + 120, 590, y0 + 220), fill=YEL); c.text((540 - c.textlength('VS', font=vf) / 2, y0 + 136), 'VS', font=vf, fill=NAVY)
            pc = ease((t - 1.0) / 0.3)
            if pc > 0:
                s = '차이 0.49%p'; ff = F(BLACK, 50); sw = c.textlength(s, font=ff)
                c.rounded_rectangle((540 - sw / 2 - 34, y0 + 360, 540 + sw / 2 + 34, y0 + 440), 40, fill=RED + (int(255 * pc),))
                c.text((540 - sw / 2, y0 + 370), s, font=ff, fill=WHITE + (int(255 * pc),))
            L.alpha_composite(with_alpha(C, p))
        d = ImageDraw.Draw(L)
        if t > 2.2: subtitle(d, ['대신 보험사는 DSR [c]50%[/] (은행 40%)', '→ [y]한도[/]는 더 나올 수 있어요'], y=1060)
        foot(d, '※ 금리 하단 기준 · 실제 금리는 신용·소득·담보에 따라 달라요', y=1300); handle(d); return L
    return dur, 'c3', -1, draw, [(4, 0.4), (4, 1.0), (5, 2.2)]


@scene
def s7():
    dur = 4.6
    items = ['LTV · DSR 한도 먼저', '중도상환수수료', '우대금리 조건 (급여·카드)', '내 신용점수 적용 금리']
    def draw(t):
        L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
        header(d, None, ['금리만 보면 [r]손해[/]', '이것도 꼭 체크!'], y0=170)
        y0 = 560
        for k, s in enumerate(items):
            p = ease((t - 0.4 - k * 0.3) / 0.3)
            if p <= 0: continue
            R = Image.new('RGBA', (900, 110)); r = ImageDraw.Draw(R)
            r.rounded_rectangle((0, 0, 900, 100), 26, fill=(255, 255, 255, 240))
            r.ellipse((24, 20, 84, 80), fill=GREEN); r.line((40, 50, 52, 63, 70, 37), fill=WHITE, width=9)
            r.text((112, 20), s, font=F(BLACK, 50), fill=NAVY)
            L.alpha_composite(with_alpha(R, p), (60 + int(50 * (1 - p)), y0 + k * 125))
        d = ImageDraw.Draw(L)
        if t > 1.9: subtitle(d, ['[y]한도[/] 안 나오면 금리 1등도 소용없어요'], y=1150)
        handle(d); return L
    return dur, 'c5', 1, draw, [(4, 0.4), (4, 0.7), (4, 1.0), (4, 1.3)]


@scene
def s8():
    dur = 4.6
    sub = ["댓글에 '[y]한도[/]' 남기면", '우리 집 [c]최대 한도[/] DM으로'] if V == 'ig' else ['[y]채널 이름[/] 누르고 프로필 링크', '우리 집 [c]최대 한도[/] 1분 확인']
    def draw(t):
        L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
        header(d, '3억 · 30년 원리금균등', ['금리 [y]0.5%p[/] 차이 =', '총이자 [r]약 3,200만원[/]'], y0=300)
        if t > 1.4: subtitle(d, sub, y=1060)
        foot(d, '※ 4.38% vs 4.88% 단순 계산 (월 약 9만원 차이)', y=1300); handle(d); return L
    return dur, 'c10', -1, draw, [(5, 0.5), (4, 1.4)]


def render_scene(i, fn):
    dur, img, dirn, draw, _ = fn()
    n = int(round(dur * FPS)); tmp = f'{OUT}/s{i:02d}.tmp.mp4'; out = f'{OUT}/s{i:02d}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    snaps = {int(n * 0.9)}
    for k in range(n):
        t = k / FPS
        fr = bg(img, t, dur, dirn)
        a = 1 if i == 1 else ease(t / 0.25)
        fr.alpha_composite(with_alpha(draw(t), a))
        rgb = fr.convert('RGB')
        if k in snaps: rgb.save(f'{OUT}/snap{i:02d}.jpg', quality=85)
        p.stdin.write(rgb.tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)


def snap(i, t):
    dur, img, dirn, draw, _ = SC[i - 1]()
    fr = bg(img, t, dur, dirn); fr.alpha_composite(draw(t)); fr.convert('RGB').save(f'{OUT}/frame{i:02d}.jpg', quality=85)


def build():
    OUTRO = f'{TOOLS}/../outro/outro_{V}.mp4'
    t = 0.0; sfx = []; lst = []
    for i, fn in enumerate(SC):
        dur, *_r, ev = fn(); sfx += [f'{k}:{t + s:.2f}' for k, s in ev]; lst.append(f"file '{OUT}/s{i + 1:02d}.mp4'"); t += dur
    total = t + 8.0
    open(f'{OUT}/list.txt', 'w').write('\n'.join(lst + [f"file '{os.path.abspath(OUTRO)}'"]))
    subprocess.run(['python3', f'{TOOLS}/bgm_citypop.py', f'{OUT}/bgm.wav', f'{total:.2f}', '11', '104', ','.join(sfx)], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-an', '-vf', f'fps={FPS},scale={W}:{H},setsar=1',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', f'{OUT}/video.mp4'], check=True)
    final = f'{OUT}/final_{V}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/video.mp4', '-i', f'{OUT}/bgm.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final], check=True)
    print('built', final, round(total, 2))


if __name__ == '__main__':
    if 'snap' in sys.argv:
        for i in range(1, len(SC) + 1): snap(i, 4.5 if i != 1 else 3.0)
        sys.exit()
    for i, fn in enumerate(SC):
        if ONLY and i + 1 not in ONLY: continue
        if BUILD and not ONLY and os.path.exists(f'{OUT}/s{i + 1:02d}.mp4'): continue
        render_scene(i + 1, fn); print('scene', i + 1, 'ok', flush=True)
    if BUILD: build()
