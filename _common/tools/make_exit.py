# 쇼츠: 2027.1.1 비거주 1주택 전세대출 제한 → 퇴거자금 지역별 한도·예전 계약 예외 — 노원 중계 청구3차 (2026-11-13)
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
OUT = f'/home/claude/exit/out_{V}'; os.makedirs(OUT, exist_ok=True)
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
KB, DEP = 139500, 80000          # 청구3차 84㎡ KB시세 13억9,500(26.10.02) / 돌려줄 보증금 8억 가정 (KB 전세 8억1,500)


def won(v):
    e, m = divmod(int(v), 10000)
    return (f'{e}억' if e else '') + (f' {m:,}만' if m else '') or '0'


# 1. 훅
def s1():
    dur = 4.2
    T = text_layer([('세입자 [r]내보내야[/] 하는데', 0), ('은행은 [x]1억[/]만?', 1)],
                   ['노원 중계 [y]청구3차[/]로 계산해봄', '전세 [y]8억[/] 돌려줘야 하는 집'], chip='2027.1.1부터 달라지는 것')
    return dur, photo(J + 'img4.png', dur, 1, dark=0.1), T, stamp_fx(stamp('한도 1억', RED, 100, -9), 1.0), [(1, 1.0)]
SC.append(s1)


# 2. 왜 지금: 8·13 대책 비거주 1주택 전세대출 제한
def s2():
    dur = 5.4
    mid = step_cards([('1', '수도권·규제지역 아파트 1채', '부부 합산 1주택'),
                      ('2', '그 집은 세 줬고', '가족한테 준 건 제외'),
                      ('3', '부부 둘 다 산 적 없음', '전입 이력 0번')], numcol=CORAL)
    T = text_layer([('내년 1월부터', 0), ('[x]비거주 1주택자[/] 전세대출 X', 1)],
                   ['3개 다 해당하면 [r]신규·연장 금지[/]', '→ 결국 [y]내 집 들어가야[/] 하는 사람 ↑'],
                   '금융위 부동산 시장 안정 금융 종합대책 (2026.8.13 발표 · 2027.1.1 시행)', chip='8·13 대책', chipcol=CORAL, handle=False)
    return dur, mid, T, None, [(4, 0.25), (4, 0.8), (4, 1.35)]
SC.append(s2)


# 3. 그래서 퇴거자금
def s3():
    dur = 4.6
    T = text_layer([('그래서 필요한 게', 0), ('[b]퇴거자금대출[/]', 1)],
                   ['세입자 보증금 돌려주는 [c]집주인 대출[/]', '근데 수도권은 [r]원칙 1억[/]까지'], '6·27 대책(2025) 이후 · 수도권 다주택자는 아예 불가')
    return dur, photo(J + 'img2.png', dur, -1, dark=0.15), T, None, []
SC.append(s3)


# 4. 지역별 한도
def s4():
    dur = 6.0
    rows = [('서울·경기 규제', '1억 + LTV 40%', '서울 전역·과천·분당·광명·동탄·구리 등', RED),
            ('수도권 나머지', '1억 + LTV 70%', '인천·경기 비규제지역', CORAL),
            ('지방', '1억 제한 없음', 'LTV 70%·DSR 안에서 보증금까지', GREEN)]
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    x0, x1, y0, rh = 30, 1050, TOP + 34, 182
    d.rounded_rectangle((x0, y0, x1, y0 + rh * 3 + 16), 30, fill=(255, 255, 255, 250))
    for i, (a, b, c, col) in enumerate(rows):
        y = y0 + 8 + i * rh
        if i: d.line((x0 + 24, y, x1 - 24, y), fill=(215, 220, 230), width=2)
        d.rounded_rectangle((x0 + 24, y + 50, x0 + 304, y + 130), 22, fill=col)
        f = fit(d, a, BLACK, 42, 260); tw = d.textlength(a, font=f); d.text((x0 + 164 - tw / 2, y + 64), a, font=f, fill=WHITE)
        d.text((x0 + 334, y + 30), b, font=fit(d, b, BLACK, 58, 650), fill=NAVY)
        d.text((x0 + 336, y + 108), c, font=fit(d, c, BOLD, 32, 650), fill=(90, 100, 125))
    T = text_layer([('우리 동네', 0), ('퇴거자금 [b]얼마까지?[/]', 1)],
                   ['수도권은 어디든 [r]원칙 1억[/]', '지방은 [g]보증금만큼[/]도 가능'], '1주택자 기준 · 규제지역 2026.7 동탄·기흥·구리 추가', handle=False)
    bg = Image.new('RGB', (W, MID), NAVY)
    def fx(t, fr):
        for i in range(3):
            p = ease((t - 0.2 - i * 0.45) / 0.35)
            if p <= 0: continue
            y = y0 + 8 + i * rh - (8 if i == 0 else 0); hh = rh + (8 if i == 0 else 0) + (8 if i == 2 else 0)
            band = with_alpha(L.crop((0, y, W, y + hh)), p); fr.alpha_composite(band, (int((1 - p) * 60), y))
    return dur, (lambda t: bg), T, fx, [(4, 0.2), (4, 0.65), (4, 1.1)]
SC.append(s4)


# 5. 예전 계약 예외
def s5():
    dur = 5.6
    mid = step_cards([('1', '세입자 계약 2025.6.27 이전', '지금 세입자와의 최초 임대차 계약'),
                      ('2', '내가 산 날도 6.27 이전', '매매계약 또는 소유권 이전등기'),
                      ('✓', '둘 다 OK → 1억 초과 + LTV 70%', '은행업감독규정 경과규정')], numcol=GREEN)
    T = text_layer([('[c]예전 계약[/]이면', 0), ('[m]1억 넘게[/] 가능', 1)],
                   ['[r]하나라도[/] 6.27 이후면', '→ [r]1억 · LTV 40%[/] 그대로'], '세입자 계약이 먼저여도 매매가 6.27 이후면 X (이데일리 2026.2.11)', chip='예외 조건', chipcol=GREEN, handle=False)
    return dur, mid, T, None, [(4, 0.25), (4, 0.8), (5, 1.35)]
SC.append(s5)


# 6. 은행 진짜 해줘?
def s6():
    dur = 5.4
    mid = step_cards([('1', '내 돈으로 못 돌려줄 때만', "'자력 반환 불가' 확인"),
                      ('2', '1개월 내 전입 + 2년 거주', '들어가 살 거면 실거주 의무'),
                      ('3', '돈은 세입자에게 직접', '보증금 반환 외 사용 금지')])
    T = text_layer([('예전 계약이면', 0), ('은행 [b]진짜 해줘요?[/]', 1)],
                   ['우리·신한·BNK 등 [g]재개[/]했지만', '조건·해석은 은행마다 [r]제각각[/]'], '6·27 이전 계약분 1억 초과 취급 조건 (2025.7 은행권 약정서)', handle=False)
    return dur, mid, T, None, [(4, 0.25), (4, 0.8), (4, 1.35)]
SC.append(s6)


# 7. 청구3차 실제 계산
def s7():
    dur = 6.2
    rows = [('돌려줄 보증금', '전세 시세 8억대 · 8억 가정', DEP, NAVY, (230, 236, 248), 0.3),
            ('예전 계약 (둘 다 6.27 이전)', f'LTV 70% = {won(KB * 7 // 10)} → 보증금 전액', DEP, GREEN, (255, 255, 255), 1.0),
            ('6.27 이후 계약', '수도권 퇴거자금 상한', 10000, RED, (255, 236, 234), 1.8)]
    bg = Image.new('RGB', (W, MID), NAVY2)
    def mid(t):
        im = bg.copy().convert('RGBA')
        for i, (name, note, v, col, fill, t0) in enumerate(rows):
            p = ease((t - t0) / 0.35)
            if p <= 0: continue
            card = Image.new('RGBA', (1000, 180)); c = ImageDraw.Draw(card)
            c.rounded_rectangle((0, 0, 1000, 180), 30, fill=fill + (250,)); c.rounded_rectangle((0, 0, 22, 180), 11, fill=col)
            c.text((50, 26), name, font=fit(c, name, BLACK, 44, 560), fill=NAVY if i < 2 else (200, 45, 40))
            c.text((50, 112), note, font=fit(c, note, BOLD, 30, 600), fill=(100, 110, 135) if i < 2 else (200, 70, 60))
            q = ease((t - t0 - 0.1) / 0.7); val = won(round(v * q / 1000) * 1000) if q < 1 else won(v)
            f = F(BLACK, 92); tw = c.textlength(val, font=f)
            c.text((960 - tw, 40), val, font=f, fill=NAVY if i == 0 else (20, 140, 90) if i == 1 else (215, 50, 45))
            im.alpha_composite(with_alpha(card, p), (40 + int((1 - p) * 80), 30 + i * 205))
        if t > 2.9:   # 부족 7억 뱃지
            pk = ease((t - 2.9) / 0.25); s = '부족 7억'; f = F(BLACK, 54); d = ImageDraw.Draw(im); tw = d.textlength(s, font=f)
            b = Image.new('RGBA', (int(tw + 70), 92)); bd = ImageDraw.Draw(b)
            bd.rounded_rectangle((0, 0, b.width, 92), 46, fill=(235, 64, 58, 255)); bd.text((35, 12), s, font=f, fill=WHITE)
            b = b.rotate(-6, expand=True, resample=Image.BICUBIC); sc = 1.6 - 0.6 * pk
            b = with_alpha(b.resize((int(b.width * sc), int(b.height * sc))), pk)
            im.alpha_composite(b, (int(610 - b.width / 2), int(530 - b.height / 2)))
        return im.convert('RGB')
    T = text_layer([('[w]중계 청구3차[/] 84㎡', 0), ('같은 집, [x]7억[/] 차이', 1)],
                   ['계약 [y]날짜[/] 하나로 갈림', 'KB시세 [y]13억9,500[/] 기준 (26.10)'],
                   '보증금 8억 가정 · 기존 대출 0 · LTV 기준(DSR 별도)', chip='노원구 중계동 · 은행사거리', handle=False)
    return dur, mid, T, None, [(4, 0.3), (4, 1.0), (1, 1.8), (1, 2.9)]
SC.append(s7)


# 8. DSR 2차 관문
def s8():
    dur = 5.0
    T = text_layer([('LTV 통과해도', 0), ('[r]DSR[/]이 2차 관문', 1)],
                   ['8억 받으려면 연소득 [y]약 1.2억[/]↑', '스트레스 금리 붙으면 [r]더 필요[/]'],
                   '금리 4.4%·30년 원리금균등·DSR 40%·다른 대출 0 단순 계산')
    return dur, photo(J + 'img1.png', dur, 1, dark=0.15), T, stamp_fx(stamp('DSR 40%', RED, 92, 8), 0.8, W / 2 + 170, TOP + MID / 2 + 100), [(1, 0.8)]
SC.append(s8)


# 9. CTA
def s9():
    dur = 4.2
    sub = ["댓글에 '[y]한도[/]' 남기면", '우리 집 퇴거자금 [c]가능 금액[/] DM으로'] if V == 'ig' else ['[y]채널 이름[/] 누르고 프로필 링크', '우리 집 [c]최대 한도[/] 1분 확인']
    T = text_layer([('계약일부터 [y]확인[/]하고', 0), ('[b]은행 여러 곳[/] 비교', 1)], sub)
    return dur, photo(J + 'img0.png', dur, -1, dark=0.1), T, None, [(5, 0.4)]
SC.append(s9)


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
    subprocess.run(['python3', f'{TOOLS}/bgm_trap.py', f'{OUT}/bgm.wav', f'{total:.2f}', '13', '142', ','.join(sfx)], check=True)
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
