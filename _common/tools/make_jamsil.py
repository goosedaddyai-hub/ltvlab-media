# 쇼츠: 잠실 래미안아이파크 계약취소 3가구 무순위 줍줍 (2026-11-18)
# 사용: python3 make_exit.py ig|yt [scene번호...]   /  python3 make_guri.py ig|yt build  (렌더+BGM+엔딩 합치기)
import sys, os, re, html, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

V = sys.argv[1]
BUILD = 'build' in sys.argv[2:]
ONLY = [int(x) for x in sys.argv[2:] if x.isdigit()]
W, H, FPS = 1080, 1920, 30
TOP, MID = 600, 660
NAVY = (20, 33, 61); NAVY2 = (31, 49, 89); YEL = (255, 201, 40); WHITE = (255, 255, 255)
SUB = (190, 202, 225); RED = (232, 65, 58); CORAL = (255, 122, 89); GREEN = (46, 196, 125)
FD = '/home/claude/ltvlab-media/_common/fonts'
BLACK = f'{FD}/Pretendard-Black.otf'
BOLD = f'{FD}/Pretendard-ExtraBold.otf'
_fc = {}
def F(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]
HANDLE = '@ltv_lab_kr' if V == 'yt' else '@ltv.lab'
RAW = '/home/claude/ltvlab-media/_raw'
OUT = f'/home/claude/jamsil/out_{V}'; os.makedirs(OUT, exist_ok=True)
ease = lambda x: 1 - (1 - max(0, min(1, x))) ** 3


def fit(d, text, path, size, maxw):
    while size > 24:
        if d.textlength(text, font=F(path, size)) <= maxw: return F(path, size)
        size -= 2
    return F(path, size)


def with_alpha(L, a):
    if a >= 1: return L
    r, g, b, al = L.split(); return Image.merge('RGBA', (r, g, b, al.point(lambda v: int(v * a))))


COL = {'y': YEL, 'r': (255, 92, 80), 'g': (52, 222, 150), 'c': (120, 215, 255), 'w': WHITE, 's': SUB}
BOX = {'b': (YEL, NAVY), 'x': ((235, 64, 58), WHITE), 'm': ((52, 210, 140), NAVY), 'w': (WHITE, NAVY)}


def segs(s, base):
    out = []
    for m in re.finditer(r'\[([a-z])\](.*?)\[/\]|([^\[]+)', s):
        if m.group(3): out.append((m.group(3), base, None))
        else:
            k = m.group(1)
            out.append((m.group(2), WHITE if k in BOX else COL[k], k if k in BOX else None))
    return out


def rich(t, cx, y, s, path, size, maxw, base=WHITE, shadow=False):
    """[y]노랑[/] [r]빨강[/] [g]초록[/] [c]하늘[/] / 박스: [b]노랑박스[/] [x]빨강박스[/] [m]초록박스[/]
    박스는 실제 글자 높이('가') 기준으로 위아래 여백을 똑같이 → 어느 줄이든 같은 규격"""
    sg = segs(s, base)
    def geo(f):
        pad = round(f.size * 0.17); gap = round(f.size * 0.09)
        return pad, gap
    def width(f):
        pad, gap = geo(f)
        return sum(t.textlength(a, font=f) + ((2 * pad + 2 * gap) if bx else 0) for a, _, bx in sg)
    size_ = size
    while size_ > 24 and width(F(path, size_)) > maxw: size_ -= 2
    f = F(path, size_); pad, gap = geo(f); x = cx - width(f) / 2
    _, gt, _, gb = t.textbbox((0, 0), '한을', font=f)      # 한글 글자 실제 위·아래
    vp = round(f.size * 0.15)
    for a, c, bx in sg:
        tw = t.textlength(a, font=f)
        if bx:
            bgc, fg = BOX[bx]; x += gap
            if shadow: t.rounded_rectangle((x + 4, y + gt - vp + 7, x + tw + 2 * pad + 4, y + gb + vp + 7), round(f.size * 0.16), fill=(0, 0, 0, 110))
            t.rounded_rectangle((x, y + gt - vp, x + tw + 2 * pad, y + gb + vp), round(f.size * 0.16), fill=bgc)
            t.text((x + pad, y), a, font=f, fill=NAVY if bx in 'bmw' else WHITE); x += tw + 2 * pad + gap
        else:
            if shadow: t.text((x + 3, y + 6), a, font=f, fill=(0, 0, 0, 120))
            t.text((x, y), a, font=f, fill=c); x += tw
    return f


def text_layer(head, sub, src='', chip=None, chipcol=YEL, handle=True):
    L = Image.new('RGBA', (W, H)); t = ImageDraw.Draw(L)
    t.rectangle((0, TOP - 6, W, TOP), fill=YEL)
    lh = 92 + 30
    y = TOP - 60 - lh * len(head)
    if chip:
        cf = F(BLACK, 40); cw = t.textlength(chip, font=cf)
        t.rounded_rectangle(((W - cw) / 2 - 28, y - 86, (W + cw) / 2 + 28, y - 22), 32, fill=chipcol)
        t.text(((W - cw) / 2, y - 82), chip, font=cf, fill=NAVY)
    for s, em in head:
        rich(t, W / 2, y, s, BLACK, 96, W - 110, YEL if (em and '[' not in s) else WHITE, shadow=True); y += lh
    cx = 470; y = TOP + MID + 60          # 오른쪽 버튼 구간 피해서 왼쪽 중심
    for k, s in enumerate(sub):
        f = rich(t, cx, y, s, BOLD, 56, 820, WHITE if (k == 0 or '[' in s) else (215, 222, 238)); y += f.size + 30
    if src:
        f = F(BOLD, 26); tw = t.textlength(src, font=f); t.text((cx - tw / 2, y + 8), src, font=f, fill=SUB)
    if handle:
        f = F(BOLD, 28); tw = t.textlength(HANDLE, font=f)
        t.rounded_rectangle((40, TOP + 24, 40 + tw + 36, TOP + 72), 24, fill=(20, 33, 61, 190))
        t.text((58, TOP + 30), HANDLE, font=f, fill=WHITE)
    return L


def info_chip(lines, y=TOP + MID - 150, col=NAVY):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    f1, f2 = F(BLACK, 38), F(BOLD, 30)
    w_ = max(d.textlength(lines[0], font=f1), d.textlength(lines[1], font=f2)) + 56
    d.rounded_rectangle((36, y, 36 + w_, y + 116), 22, fill=col + (235,))
    d.rectangle((36, y + 20, 44, y + 96), fill=YEL)
    d.text((64, y + 12), lines[0], font=f1, fill=YEL); d.text((64, y + 64), lines[1], font=f2, fill=WHITE)
    return L


def stamp(word, col=RED, size=110, rot=12):
    f = F(BLACK, size); tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1))); tw = tmp.textlength(word, font=f)
    w_, h_ = int(tw + 100), int(size * 2)
    st = Image.new('RGBA', (w_, h_)); d = ImageDraw.Draw(st)
    d.rounded_rectangle((8, 8, w_ - 8, h_ - 8), 26, outline=col + (255,), width=14)
    d.text(((w_ - tw) / 2, h_ / 2 - size * 0.68), word, font=f, fill=col + (255,))
    return st.rotate(rot, expand=True, resample=Image.BICUBIC)


def stamp_fx(st, t0, cx=W / 2, cy=TOP + MID / 2):
    def fx(t, fr):
        if t > t0:
            p = ease((t - t0) / 0.18); s = 1.8 - 0.8 * p
            im = with_alpha(st.resize((int(st.width * s), int(st.height * s))), p)
            fr.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
    return fx


def photo(idx, dur, dirn=1, dark=0.0):
    src = Image.open(f'{RAW}/{idx}').convert('RGB'); sw, sh = src.size; ar = W / MID
    bw, bh = (sw, sw / ar) if sw / sh < ar else (sh * ar, sh)
    def fn(t):
        z = 1 + 0.08 * t / dur; cw, ch = bw / z, bh / z
        x0 = (sw - cw) / 2 + dirn * (bw - cw) * 0.3; y0 = (sh - ch) / 2
        im = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, MID), Image.BILINEAR)
        return Image.blend(im, Image.new('RGB', im.size, NAVY), dark) if dark else im
    return fn




def chip_fx(C, t0):
    def fx(t, fr):
        if t > t0: fr.alpha_composite(with_alpha(C, ease((t - t0) / 0.3)))
    return fx


def both(*fxs):
    def fx(t, fr):
        for f in fxs:
            if f: f(t, fr)
    return fx


def bars(vals, labels, tops, t0=0.3, step=0.5, col=YEL, hi=None):
    """가운데 띠 막대그래프 (만원 단위 금액 라벨)"""
    bg = Image.new('RGB', (W, MID), NAVY2)
    n = len(vals); vmax = max(vals); bw = 150 if n == 4 else 190; gapx = (W - 120 - n * bw) / max(1, n - 1)
    base = MID - 110; hmax = MID - 250
    def mid(t):
        im = bg.copy().convert('RGBA'); d = ImageDraw.Draw(im)
        d.line((50, base, W - 50, base), fill=(90, 110, 150), width=4)
        for i, (v, lb, tp) in enumerate(zip(vals, labels, tops)):
            p = ease((t - t0 - i * step) / 0.45)
            if p <= 0: continue
            x = 60 + i * (bw + gapx); h = hmax * v / vmax * p
            c = (hi if (hi and i == n - 1) else col)
            d.rounded_rectangle((x, base - h, x + bw, base), 18, fill=c)
            f = fit(d, tp, BLACK, 44, bw + 40); tw = d.textlength(tp, font=f)
            d.text((x + bw / 2 - tw / 2, base - h - f.size - 22), tp, font=f, fill=WHITE)
            f2 = F(BOLD, 32); tw = d.textlength(lb, font=f2)
            d.text((x + bw / 2 - tw / 2, base + 22), lb, font=f2, fill=SUB)
            if i:  # 화살표
                ax = x - gapx / 2; ay = base - hmax * vals[i - 1] / vmax - 40
                d.text((ax - 18, ay), '›', font=F(BLACK, 60), fill=YEL)
        return im.convert('RGB')
    return mid


def step_cards(steps, t0=0.25, step=0.55, numcol=YEL):
    bg = Image.new('RGB', (W, MID), NAVY2); cards = []
    for n_, a, b in steps:
        c = Image.new('RGBA', (880, 170)); d = ImageDraw.Draw(c)
        d.rounded_rectangle((0, 0, 880, 170), 30, fill=(255, 255, 255, 248))
        d.ellipse((30, 35, 130, 135), fill=numcol); f = F(BLACK, 64); tw = d.textlength(n_, font=f)
        d.text((80 - tw / 2, 38), n_, font=f, fill=NAVY)
        d.text((165, 26), a, font=fit(d, a, BLACK, 52, 690), fill=NAVY); d.text((167, 100), b, font=fit(d, b, BOLD, 34, 690), fill=(90, 100, 125))
        cards.append(c)
    arrow = Image.new('RGBA', (60, 40)); ImageDraw.Draw(arrow).polygon([(0, 0), (60, 0), (30, 36)], fill=YEL)
    def mid(t):
        im = bg.copy().convert('RGBA')
        for i, c in enumerate(cards):
            p = ease((t - t0 - i * step) / 0.35)
            if p <= 0: continue
            y = 22 + i * 214
            im.alpha_composite(with_alpha(c, p), (100 + int((1 - p) * 120), y))
            if i < len(cards) - 1 and t > t0 + i * step + 0.3: im.alpha_composite(arrow, (510, y + 174))
        return im.convert('RGB')
    return mid


# ---------- 장면 ----------
SC = []
J = '2026-10-26_jeonse-ban/'; C = '2026-11-11_rate-compare/'


def won(v):
    e, m = divmod(int(v), 10000)
    return (f'{e}억' if e else '') + (f' {m:,}만' if m else '') or '0'


# 1. 훅
def s1():
    dur = 4.2
    T = text_layer([('잠실 신축 84㎡가', 0), ('[x]18억[/]에 줍줍?', 1)],
                   ['잠실 래미안아이파크 [y]계약취소 3가구[/]', '84㎡ 입주권 [y]43억[/] 거래된 단지'], chip='11/23 무순위 청약')
    return dur, photo(C + 'c9.jpg', dur, 1, dark=0.05), T, stamp_fx(stamp('로또 24억', RED, 100, -9), 1.0), []
SC.append(s1)


# 2. 분양가 vs 시세
def s2():
    dur = 6.2
    rows = [('43㎡', '일반 1가구', '11억 548만', '실거래 23억8천 (26.6)', '+12.7억'),
            ('59㎡A', '일반 1가구', '15억 7,939만', '실거래 32억7천 (26년)', '+16.9억'),
            ('84㎡D', '신혼특공 1가구', '18억 5,607만', '입주권 43억 (26.7)', '+24억')]
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    x0, x1, y0, rh = 30, 1050, TOP + 34, 182
    d.rounded_rectangle((x0, y0, x1, y0 + rh * 3 + 16), 30, fill=(255, 255, 255, 250))
    for i, (a, a2, b, c, g) in enumerate(rows):
        y = y0 + 8 + i * rh
        if i: d.line((x0 + 24, y, x1 - 24, y), fill=(215, 220, 230), width=2)
        d.rounded_rectangle((x0 + 24, y + 36, x0 + 234, y + 146), 22, fill=NAVY)
        f = F(BLACK, 46); tw = d.textlength(a, font=f); d.text((x0 + 129 - tw / 2, y + 44), a, font=f, fill=YEL)
        f = fit(d, a2, BOLD, 26, 190); tw = d.textlength(a2, font=f); d.text((x0 + 129 - tw / 2, y + 104), a2, font=f, fill=WHITE)
        d.text((x0 + 262, y + 30), b, font=fit(d, b, BLACK, 54, 460), fill=NAVY)
        d.text((x0 + 264, y + 106), c, font=fit(d, c, BOLD, 30, 460), fill=(90, 100, 125))
        f = F(BLACK, 54); tw = d.textlength(g, font=f)
        d.rounded_rectangle((x1 - 40 - tw - 36, y + 52, x1 - 24, y + 132), 40, fill=(46, 196, 125))
        d.text((x1 - 42 - tw, y + 58), g, font=f, fill=WHITE)
    T = text_layer([('분양가 vs 시세', 0), ('차익 [m]12~24억[/]', 1)],
                   ['3가구 다 [y]분양가 그대로[/] 재공급', '분양가상한제 단지라 [c]싸게[/] 나옴'],
                   '청약홈 공고 · 실거래 (파이낸셜뉴스·서울경제 2026.11.17~18)', handle=False)
    bg = Image.new('RGB', (W, MID), NAVY)
    def fx(t, fr):
        for i in range(3):
            p = ease((t - 0.2 - i * 0.5) / 0.35)
            if p <= 0: continue
            y = y0 + 8 + i * rh - (8 if i == 0 else 0); hh = rh + (8 if i == 0 else 0) + (8 if i == 2 else 0)
            band = with_alpha(L.crop((0, y, W, y + hh)), p); fr.alpha_composite(band, (int((1 - p) * 60), y))
    return dur, (lambda t: bg), T, fx, []
SC.append(s2)


# 3. 자격
def s3():
    dur = 5.6
    mid = step_cards([('1', '서울 거주 무주택 세대주', '일반공급 43·59㎡ · 소득·자산 기준 없음'),
                      ('2', '84㎡는 신혼부부 특공', '혼인 7년 이내 · 서울 무주택 가구원'),
                      ('3', '조건 되면 전부 추첨', '가점·소득 순위 없이 1가구씩')], numcol=CORAL)
    T = text_layer([('누가 넣을 수 있어?', 0), ('[b]서울 무주택[/]만', 1)],
                   ['불법전매로 [r]계약취소[/]된 물량', '일반 [y]5만명[/] 몰릴 거란 전망도'],
                   '청약홈 공고 · 예상 신청자 헤럴드경제 2026.11.18', chip='자격', chipcol=CORAL, handle=False)
    return dur, mid, T, None, []
SC.append(s3)


# 4. 일정
def s4():
    dur = 5.2
    mid = step_cards([('1', '11/23 특공 · 11/24 일반', '한국부동산원 청약홈 접수'),
                      ('2', '11/27 당첨자 발표', '각 1가구 · 추첨'),
                      ('3', '12/4 계약 → 27년 1월 입주', '계약금 30% 바로 준비')])
    T = text_layer([('일정 [b]다음 주[/]임', 0), ('놓치면 [x]끝[/]', 1)],
                   ['실거주 [y]2년[/] · 전매제한 [y]3년[/]', '재당첨 제한 [r]10년[/]도 걸림'],
                   '청약홈 계약취소주택 재공급 공고 (2026.11)', handle=False)
    return dur, mid, T, None, []
SC.append(s4)


# 5. 계약금 30%
def s5():
    dur = 4.8
    T = text_layer([('근데 함정', 0), ('계약금 [x]30%[/]', 1)],
                   ['84㎡ 계약금만 [y]약 5.6억[/]', '59㎡도 [y]4억 7천[/] 바로 현금'],
                   '보통 10~20% → 이번엔 30% (서울경제 2026.11.18)')
    return dur, photo(C + 'c12.jpg', dur, -1, dark=0.1), T, stamp_fx(stamp('현금 박치기', RED, 92, 8), 0.9, W / 2 + 120, TOP + MID / 2 + 60), []
SC.append(s5)


# 6. 대출은?
def s6():
    dur = 5.6
    mid = step_cards([('1', '중도금·집단대출 어려움', '이미 다 지어진 단지'),
                      ('2', '미등기라 일반 주담대 X', '조합 해산·등기 전까지'),
                      ('3', '신용대출 1억↑ 받았으면', '1년 내라면 규제지역 매수 제한')], numcol=RED)
    T = text_layer([('대출은?', 0), ('[x]사실상 현금[/]', 1)],
                   ['그래서 나오는 게 [c]전세 끼고 잔금[/]', '분상제라 입주 [y]최대 3년[/] 유예 가능'],
                   '서울경제·헤럴드경제 2026.11.18', chip='잔금 플랜', chipcol=RED, handle=False)
    return dur, mid, T, None, []
SC.append(s6)


# 7. 현금 계산 (84㎡)
def s7():
    dur = 6.2
    TOT, JS = 187879, 120000
    rows = [('84㎡ 총액', '발코니 확장·옵션 포함', TOT, NAVY, (230, 236, 248), 0.3),
            ('전세 보증금', '잔금에 넣는다고 가정', JS, CORAL, (255, 242, 236), 1.0),
            ('내 현금 필요', '', TOT - JS, RED, (255, 236, 234), 1.8)]
    bg = Image.new('RGB', (W, MID), NAVY2)
    def mid(t):
        im = bg.copy().convert('RGBA')
        for i, (name, note, v, col, fill, t0) in enumerate(rows):
            p = ease((t - t0) / 0.35)
            if p <= 0: continue
            card = Image.new('RGBA', (1000, 180)); c = ImageDraw.Draw(card)
            c.rounded_rectangle((0, 0, 1000, 180), 30, fill=fill + (250,)); c.rounded_rectangle((0, 0, 22, 180), 11, fill=col)
            c.text((50, 26), name, font=fit(c, name, BLACK, 48, 420), fill=NAVY if i < 2 else (200, 45, 40))
            c.text((50, 112), note, font=fit(c, note, BOLD, 30, 420), fill=(100, 110, 135) if i < 2 else (200, 70, 60))
            q = ease((t - t0 - 0.1) / 0.7); val = won(round(v * q / 10) * 10) if q < 1 else won(v)
            if i == 1: val = '− ' + val
            f = fit(c, val, BLACK, 84, 520); tw = c.textlength(val, font=f)
            c.text((960 - tw, 46), val, font=f, fill=NAVY if i == 0 else (220, 95, 60) if i == 1 else (215, 50, 45))
            im.alpha_composite(with_alpha(card, p), (40 + int((1 - p) * 80), 30 + i * 205))
        if t > 2.9:
            pk = ease((t - 2.9) / 0.25); s = '+ 취득세 별도'; f = F(BLACK, 46); d = ImageDraw.Draw(im); tw = d.textlength(s, font=f)
            b = Image.new('RGBA', (int(tw + 60), 80)); bd = ImageDraw.Draw(b)
            bd.rounded_rectangle((0, 0, b.width, 80), 40, fill=(255, 201, 40, 255)); bd.text((30, 10), s, font=f, fill=NAVY)
            b = b.rotate(-5, expand=True, resample=Image.BICUBIC); sc = 1.6 - 0.6 * pk
            b = with_alpha(b.resize((int(b.width * sc), int(b.height * sc))), pk)
            im.alpha_composite(b, (int(290 - b.width / 2), int(578 - b.height / 2)))
        return im.convert('RGB')
    T = text_layer([('40억대 아파트를', 0), ('현금 [x]약 7억[/]으로?', 1)],
                   ['전세 [y]12억[/] 받아 잔금 치는 가정', '대신 [r]2년 실거주[/]는 결국 해야 함'],
                   '헤럴드경제 2026.11.18 계산 방식 · 전세금은 가정치', chip='84㎡ 당첨 시', handle=False)
    return dur, mid, T, None, []
SC.append(s7)


# 8. CTA
def s8():
    dur = 4.4
    sub = ["댓글에 '[y]한도[/]' 남기면", '우리 집 [c]최대 대출 한도[/] DM으로'] if V == 'ig' else ['[y]채널 이름[/] 누르고 프로필 링크', '우리 집 [c]최대 한도[/] 1분 확인']
    T = text_layer([('당첨되면 [y]잔금 플랜[/]부터', 0), ('[b]미리 계산[/]해두기', 1)], sub)
    return dur, photo(J + 'img3.png', dur, -1, dark=0.1), T, None, []
SC.append(s8)


def render_scene(i, fn):
    dur, mid, T, fx, _ = fn()
    n = int(round(dur * FPS)); tmp = f'{OUT}/s{i:02d}.tmp.mp4'; out = f'{OUT}/s{i:02d}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    snaps = {int(n * 0.85)}
    for k in range(n):
        t = k / FPS
        fr = Image.new('RGBA', (W, H), NAVY + (255,)); fr.paste(mid(t), (0, TOP))
        fr.alpha_composite(with_alpha(T, ease(t / 0.3)))
        if fx: fx(t, fr)
        rgb = fr.convert('RGB')
        if k in snaps: rgb.save(f'{OUT}/snap{i:02d}.jpg', quality=85)
        p.stdin.write(rgb.tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)


def build():
    TOOLS = os.path.dirname(os.path.abspath(__file__)); OUTRO = f'{TOOLS}/../outro/outro_{V}.mp4'
    t = 0.0; sfx = []; lst = []
    for i, fn in enumerate(SC):
        dur, *_r, ev = fn(); sfx += [f'{k}:{t + s:.2f}' for k, s in ev]; lst.append(f"file '{OUT}/s{i + 1:02d}.mp4'"); t += dur
    drop = 1.0; total = t + 8.0
    open(f'{OUT}/list.txt', 'w').write('\n'.join(lst + [f"file '{os.path.abspath(OUTRO)}'"]))
    subprocess.run(['python3', f'{TOOLS}/bgm_marimba.py', f'{OUT}/bgm.wav', f'{total:.2f}', '17', '114'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-an', '-vf', f'fps={FPS},scale={W}:{H},setsar=1',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', f'{OUT}/video.mp4'], check=True)
    final = f'{OUT}/final_{V}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/video.mp4', '-i', f'{OUT}/bgm.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final], check=True)
    print('built', final, round(total, 2))


if __name__ == '__main__':
    for i, fn in enumerate(SC):
        if ONLY and i + 1 not in ONLY: continue
        if BUILD and not ONLY and os.path.exists(f'{OUT}/s{i + 1:02d}.mp4'): continue
        render_scene(i + 1, fn); print('scene', i + 1, 'ok', flush=True)
    if BUILD: build()
