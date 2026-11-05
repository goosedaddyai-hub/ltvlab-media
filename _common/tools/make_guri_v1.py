# 쇼츠: 구리 실제 등기 3건 — 최대한도·하자 해소·증액 (2026-11-05)
# 사용: python3 make_guri.py ig|yt [scene번호...]   /  python3 make_guri.py ig|yt build  (렌더+BGM+엔딩 합치기)
import sys, os, re, html, subprocess
import numpy as np
sys.path.insert(0, '/home/claude/rl'); import mask
from PIL import Image, ImageDraw, ImageFont, ImageFilter

V = sys.argv[1]
BUILD = 'build' in sys.argv[2:]
ONLY = [int(x) for x in sys.argv[2:] if x.isdigit()]
W, H, FPS = 1080, 1920, 30
TOP, MID = 600, 660
NAVY = (20, 33, 61); NAVY2 = (31, 49, 89); YEL = (255, 201, 40); WHITE = (255, 255, 255)
SUB = (190, 202, 225); RED = (232, 65, 58); CORAL = (255, 122, 89); GREEN = (46, 196, 125)
BLACK = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
_fc = {}
def F(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]
HANDLE = '@ltv_lab_kr' if V == 'yt' else '@ltv.lab'
RL = '/home/claude/rl'; VID = f'{RL}/vid'; IMG = '/home/claude/ltvlab-media/_raw/2026-10-26_jeonse-ban'
OUT = f'{RL}/out_{V}'; os.makedirs(OUT, exist_ok=True)
ease = lambda x: 1 - (1 - max(0, min(1, x))) ** 3


def fit(d, text, path, size, maxw):
    while size > 24:
        if d.textlength(text, font=F(path, size)) <= maxw: return F(path, size)
        size -= 2
    return F(path, size)


def with_alpha(L, a):
    if a >= 1: return L
    r, g, b, al = L.split(); return Image.merge('RGBA', (r, g, b, al.point(lambda v: int(v * a))))


def text_layer(head, sub, src='', chip=None, chipcol=YEL, handle=True):
    L = Image.new('RGBA', (W, H)); t = ImageDraw.Draw(L)
    t.rectangle((0, TOP - 6, W, TOP), fill=YEL)
    fs = [fit(t, s, BLACK, 92, W - 120) for s, _ in head]
    lh = [f.size + 22 for f in fs]
    y = TOP - 60 - sum(lh)
    if chip:
        cf = F(BLACK, 40); cw = t.textlength(chip, font=cf)
        t.rounded_rectangle(((W - cw) / 2 - 28, y - 86, (W + cw) / 2 + 28, y - 22), 32, fill=chipcol)
        t.text(((W - cw) / 2, y - 82), chip, font=cf, fill=NAVY)
    for (s, em), f, h in zip(head, fs, lh):
        tw = t.textlength(s, font=f); t.text(((W - tw) / 2, y), s, font=f, fill=YEL if em else WHITE); y += h
    cx = 470; y = TOP + MID + 60          # 오른쪽 버튼 구간 피해서 왼쪽 중심
    for k, s in enumerate(sub):
        f = fit(t, s, BOLD, 56, 820); tw = t.textlength(s, font=f)
        t.text((cx - tw / 2, y), s, font=f, fill=WHITE if k == 0 else YEL); y += f.size + 26
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
    src = Image.open(f'{IMG}/img{idx}.png').convert('RGB'); sw, sh = src.size; ar = W / MID
    bw, bh = (sw, sw / ar) if sw / sh < ar else (sh * ar, sh)
    def fn(t):
        z = 1 + 0.08 * t / dur; cw, ch = bw / z, bh / z
        x0 = (sw - cw) / 2 + dirn * (bw - cw) * 0.3; y0 = (sh - ch) / 2
        im = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, MID), Image.BILINEAR)
        return Image.blend(im, Image.new('RGB', im.size, NAVY), dark) if dark else im
    return fn




# ---------- 등기 (개인정보 모자이크: 이름·주민번호·동호수·접수번호·개인 주소) ----------
S = 3.0
_pg = {}
def page(pdf, p):
    if (pdf, p) not in _pg: _pg[(pdf, p)] = mask.page(pdf, p)
    return _pg[(pdf, p)]


def doc(pdf, p, cy_pt, dur, rows, col=(255, 214, 0), t_hl=0.45, cx_pt=300, z1=0.16, gap=0.35):
    """rows: [(y0,y1)] pt — 해당 줄 형광펜으로 쓱"""
    pg = page(pdf, p); cx = cx_pt * S
    cy0, cy1 = (cy_pt if isinstance(cy_pt, tuple) else (cy_pt, cy_pt))
    def fn(t):
        u = max(0, min(1, (t - 0.2) / (dur - 0.6))); u = u * u * (3 - 2 * u); cy = (cy0 + (cy1 - cy0) * u) * S
        im = pg.copy().convert('RGBA')
        hl = Image.new('RGBA', im.size); d = ImageDraw.Draw(hl)
        for k, r in enumerate(rows):
            a, b = r[:2]; c = r[2] if len(r) > 2 else col
            pk = ease((t - t_hl - k * gap) / 0.45)
            if pk > 0: d.rectangle((78 * S, a * S, (78 + (482 * pk)) * S, b * S), fill=c + (95,))
        im = Image.alpha_composite(im, hl).convert('RGB')
        z = 1.0 + z1 * ease(t / dur); ww = 1380 / z; hh = ww * MID / W
        return im.crop((cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2)).resize((W, MID), Image.LANCZOS)
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


# 1. 훅: 아름마을 을구 — 후순위 금액 3줄 연속 형광
def s1():
    dur = 3.8
    T = text_layer([('구리 아파트 등기 3개', 0), ('까봤더니 대출이…', 1)],
                   ['규제 묶이기 직전 실제 사례', '이름·동호수는 가렸어요'])
    st = stamp('실제 등기', RED, 96, -9)
    return dur, doc('areum', 10, (200, 580), dur, [(165, 181), (296, 312), (608, 624)], t_hl=0.15, gap=1.0, z1=0.04), T, \
        stamp_fx(st, 1.1, W / 2 + 190, TOP + MID / 2 + 120), [(2, 0.15), (1, 1.1)]
SC.append(s1)


# 2. 맥락: 7월 1일부터 구리 규제지역
def s2():
    dur = 3.6
    T = text_layer([('7월 1일부터 구리는', 0), ('규제지역 + 토허제', 1)],
                   ['투기과열·조정대상·토지거래허가', '그 직전까지 등기엔 무슨 일이?'], '출처: 국토교통부·경기도 발표 (2026.6.30)')
    return dur, photo(0, dur, 1, dark=0.15), T, stamp_fx(stamp('삼중 규제', RED, 100, 10), 0.7), [(1, 0.7)]
SC.append(s2)


# 3. CASE 1 — 아차산어울림 84㎡, 7억 매수 + 1순위
def s3():
    dur = 5.0
    T = text_layer([('7억에 산 84㎡', 0), ('1순위 대출부터 크게', 1)],
                   ['보험사 1순위 채권최고 5억3,130만', '매매가의 76%를 1순위로'], chip='CASE 1  최대한도', chipcol=YEL)
    C = info_chip(['구리 교문동 · 아차산어울림 84㎡', '2024.9 매매 (거래가액 7억)'])
    return dur, doc('achasan', 6, 300, dur, [(283, 300), (352, 368)], t_hl=0.35), T, chip_fx(C, 1.4), [(2, 0.0)]
SC.append(s3)


# 4. CASE 1 — 후순위 4번 갈아타기 막대
def s4():
    dur = 5.4
    mid = bars([6000, 8400, 9600, 10200], ['25.1', '26.1', '26.2', '26.4'], ['6,000', '8,400', '9,600', '1억200'], hi=GREEN)
    T = text_layer([('후순위만 4번 갈아타며', 0), ('한도 1.7배 ↑', 1)],
                   ['1·2순위 채권최고 합계 6억3,330만', '매매가 대비 약 90%까지'], '채권최고액 기준 (만원) · 실제 대출금은 이보다 적어요', handle=False)
    return dur, mid, T, None, [(4, 0.3), (4, 0.8), (4, 1.3), (4, 1.8)]
SC.append(s4)


# 5. CASE 2 — 인창주공 58㎡, 개인 근저당 + 전세권
def s5():
    dur = 5.0
    T = text_layer([('개인한테 빌린 돈에', 0), ('전세권까지 걸린 집', 1)],
                   ['개인 근저당 7,800만 + 전세권 500만', "금융사들이 꺼리는 등기 '하자'"], chip='CASE 2  하자 해소', chipcol=CORAL)
    C = info_chip(['구리 인창동 · 인창1단지주공 58㎡', '2025.7 개인 채권자 근저당·전세권'])
    return dur, doc('inchang', 9, 230, dur, [(166, 182), (218, 234), (270, 286), (322, 338)], col=(255, 120, 100), t_hl=0.35, gap=0.25), T, chip_fx(C, 1.6), [(2, 0.0)]
SC.append(s5)


# 6. CASE 2 해법 — 등록 대부로 대환하며 말소
def s6():
    dur = 5.6
    mid = step_cards([('1', '등록 대부업체로 대환', '채권최고 1억7,250만 (2026.6)'),
                      ('2', '개인 근저당 말소', '빚 갚으면서 등기에서 삭제'),
                      ('3', '개인 전세권 말소', '후순위 막던 전세권도 정리')])
    T = text_layer([('6월, 갈아타면서', 0), ('하자 싹 정리', 1)],
                   ['규제 시행 딱 1주일 전 실행', '한도는 7,800만 → 1억7,250만'], '채권최고액 기준', handle=False)
    return dur, mid, T, None, [(4, 0.25), (4, 0.8), (4, 1.35)]
SC.append(s6)


# 6-2. 등기에 빨간 줄 = 말소 증거
def s6b():
    dur = 3.4
    T = text_layer([('등기에 그어진 빨간 줄', 0), ('= 깔끔하게 말소 완료', 1)],
                   ['26번 근저당·27번 전세권', '둘 다 같은 날 해지'])
    return dur, doc('inchang', 10, 160, dur, [(121, 150), (158, 187)], col=(46, 196, 125), t_hl=0.25, cx_pt=250), T, \
        stamp_fx(stamp('정리 완료', GREEN, 96, -8), 1.2, W / 2 + 200, TOP + MID / 2 + 110), [(2, 0.0), (1, 1.2)]
SC.append(s6b)


# 7. CASE 3 — 아름마을엘지 59㎡, 후순위 3번 증액
def s7():
    dur = 5.2
    T = text_layer([('저층 59㎡인데도', 0), ('후순위 3번 증액', 1)],
                   ['1억8,200만 → 2억4,700만 → 2억8,500만', '마지막 갈아타기는 딱 3주 만'], chip='CASE 3  증액', chipcol=GREEN)
    C = info_chip(['구리 인창동 · 아름마을엘지 59㎡', '1순위 은행 대출은 그대로 두고'])
    return dur, doc('areum', 10, (190, 600), dur, [(165, 181), (296, 312), (608, 624)], t_hl=0.3, gap=1.3, z1=0.04), T, chip_fx(C, 1.8), \
        [(2, 0.0), (4, 0.3), (4, 1.6), (4, 2.9)]
SC.append(s7)


# 8. 근데 지금은 규제지역
def s8():
    dur = 3.8
    T = text_layer([('근데 지금 구리는', 0), ('규제지역이에요', 1)],
                   ['같은 방법이 그대로 될지는', '시세·선순위·소득마다 달라요'])
    return dur, photo(3, dur, -1, dark=0.1), T, None, [(3, 0.0)]
SC.append(s8)


# 9. 한눈에 정리
def s9():
    dur = 5.6
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    x0, x1, y0 = 30, 930, TOP + 30
    rows = [('최대한도', '1순위 크게 + 후순위 갈아타기', '7억 집 → 채권최고 6.3억'),
            ('하자 해소', '개인 근저당·전세권 정리', '→ 등록 대부로 대환'),
            ('증액', '1순위 유지, 후순위만 갈아타기', '→ 9개월 새 1억 ↑')]
    cols = [YEL, CORAL, GREEN]; rh = 170
    d.rounded_rectangle((x0, y0, x1, y0 + rh * 3 + 20), 30, fill=(255, 255, 255, 250))
    for i, (a, b, c) in enumerate(rows):
        y = y0 + 10 + i * rh
        if i: d.line((x0 + 24, y, x1 - 24, y), fill=(215, 220, 230), width=2)
        d.rounded_rectangle((x0 + 26, y + 46, x0 + 276, y + 124), 22, fill=cols[i])
        f = fit(d, a, BLACK, 42, 230); tw = d.textlength(a, font=f); d.text((x0 + 151 - tw / 2, y + 58), a, font=f, fill=NAVY)
        d.text((x0 + 306, y + 30), b, font=fit(d, b, BLACK, 44, 590), fill=NAVY)
        d.text((x0 + 308, y + 94), c, font=F(BOLD, 36), fill=(70, 85, 115))
    note = '채권최고액 기준 · 한도·금리는 시세·선순위·신용에 따라 달라요'; f = fit(d, note, BOLD, 28, 900); tw = d.textlength(note, font=f)
    d.text(((x0 + x1) / 2 - tw / 2, y0 + rh * 3 + 44), note, font=f, fill=SUB)
    T = text_layer([('구리 등기 3건', 0), ('한눈에 정리', 1)], [], handle=False)
    bg = Image.new('RGB', (W, MID), NAVY)
    def fx(t, fr):
        p = ease((t - 0.15) / 0.4); fr.alpha_composite(with_alpha(L, p), (0, int((1 - p) * 60)))
    return dur, (lambda t: bg), T, fx, [(2, 0.15)]
SC.append(s9)


# 10. 카카오톡 친구추가 → 채팅 상담
def s10():
    dur = 5.4
    KY = (254, 229, 0); BR = (58, 29, 29); G = (120, 120, 128)
    bg = Image.new('RGB', (W, MID), (242, 243, 246))
    av = Image.new('RGBA', (150, 150)); d = ImageDraw.Draw(av)
    d.ellipse((0, 0, 150, 150), fill=NAVY + (255,))
    d.line([(38, 78), (75, 42), (112, 78)], fill=(232, 214, 180, 255), width=9, joint='curve')
    d.line([(50, 70), (50, 104), (100, 104), (100, 70)], fill=(232, 214, 180, 255), width=9)
    name = 'LTV연구소'
    T_ADD, T_CHAT = 2.25, 3.1

    def button(r, box, label, fill, fg, t_tap, t):
        bx0, by0, bx1, by1 = box; press = 0.92 if t_tap < t < t_tap + 0.2 else 1.0
        cxm, cym = (bx0 + bx1) / 2, (by0 + by1) / 2; hw, hh = (bx1 - bx0) / 2 * press, (by1 - by0) / 2 * press
        r.rounded_rectangle((cxm - hw, cym - hh, cxm + hw, cym + hh), 40, fill=fill)
        f = fit(r, label, BLACK, 38, bx1 - bx0 - 30); r.text((cxm - r.textlength(label, font=f) / 2, cym - f.size * 0.68), label, font=f, fill=fg)
        return cxm, cym

    def ring(row, cxm, cym, t, t_tap):
        tap = ease((t - t_tap) / 0.25); rr = 30 + 70 * tap; a = int(200 * (1 - tap))
        if t > t_tap and a > 8:
            L_ = Image.new('RGBA', row.size)
            ImageDraw.Draw(L_).ellipse((cxm - rr, cym - rr, cxm + rr, cym + rr), outline=(255, 190, 0, a), width=8)
            row.alpha_composite(L_)

    def mid(t):
        im = bg.copy().convert('RGBA'); d = ImageDraw.Draw(im)
        d.rounded_rectangle((40, 40, 1040, 180), 70, fill=(255, 255, 255, 255), outline=KY + (255,), width=8)
        d.ellipse((92, 76, 146, 130), outline=BR + (255,), width=8); d.line((139, 123, 166, 150), fill=BR + (255,), width=10)
        n = int(len(name) * max(0, min(1, (t - 0.35) / 0.9))); typed = name[:n]
        if n == 0: d.text((196, 68), '카카오톡 검색', font=F(BOLD, 60), fill=(180, 180, 188))
        else: d.text((196, 58), typed, font=F(BLACK, 72), fill=(25, 25, 30))
        if int(t * 2.4) % 2 == 0 and t < 1.6:
            cx = 196 + d.textlength(typed, font=F(BLACK, 72)) + 8; d.rectangle((cx, 72, cx + 6, 150), fill=BR + (255,))
        p = ease((t - 1.45) / 0.35)
        if p > 0:
            row = Image.new('RGBA', (980, 210)); r = ImageDraw.Draw(row)
            r.rounded_rectangle((0, 0, 980, 210), 34, fill=(255, 255, 255, 255))
            row.alpha_composite(av, (30, 30))
            r.text((200, 34), name, font=F(BLACK, 50), fill=(20, 20, 26))
            tw = r.textlength(name, font=F(BLACK, 50))
            r.rounded_rectangle((200 + tw + 12, 46, 200 + tw + 96, 88), 14, fill=KY + (255,))
            r.text((200 + tw + 27, 46), '채널', font=F(BLACK, 26), fill=BR)
            r.text((202, 120), '대출 한도·시세 상담', font=F(BOLD, 32), fill=G)
            added = t > T_ADD + 0.15
            a = button(r, (615, 64, 800, 146), '추가됨' if added else '+ 친구추가', (225, 228, 235, 255) if added else KY + (255,), G if added else BR, T_ADD, t)
            c = button(r, (815, 64, 955, 146), '채팅', BR + (255,) if t > T_CHAT else (250, 236, 120, 255), (255, 255, 255) if t > T_CHAT else BR, T_CHAT, t)
            ring(row, *a, t, T_ADD); ring(row, *c, t, T_CHAT)
            im.alpha_composite(with_alpha(row, p), (50, 220 + int((1 - p) * 50)))
        steps = [('1', '검색'), ('2', '친구 추가'), ('3', '채팅으로 상담')]
        x = 60
        for i, (k, s_) in enumerate(steps):
            q = ease((t - 3.4 - i * 0.18) / 0.3)
            if q <= 0: break
            f = F(BLACK, 40); w_ = d.textlength(s_, font=f) + 110
            chip = Image.new('RGBA', (int(w_), 92)); c = ImageDraw.Draw(chip)
            c.rounded_rectangle((0, 0, w_, 92), 46, fill=(NAVY if i < 2 else BR) + (255,))
            c.ellipse((14, 14, 78, 78), fill=KY + (255,)); c.text((46 - c.textlength(k, font=F(BLACK, 40)) / 2, 16), k, font=F(BLACK, 40), fill=BR)
            c.text((94, 16), s_, font=f, fill=(255, 255, 255))
            im.alpha_composite(with_alpha(chip, q), (x, 500 + int((1 - q) * 30))); x += int(w_) + 18
        return im.convert('RGB')
    T = text_layer([('카톡 친구추가하고', 0), ("'LTV연구소' 1:1 상담", 1)], [], handle=False)
    Lk = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(Lk)
    f = F(BLACK, 54); txt = '상담 요청·내용 기밀 엄수'; tw = d.textlength(txt, font=f)
    x0 = 470 - (tw + 120) / 2; y0 = TOP + MID + 56
    d.rounded_rectangle((x0, y0, x0 + tw + 120, y0 + 104), 52, fill=YEL)
    lx, ly = x0 + 34, y0 + 26
    d.arc((lx + 6, ly - 6, lx + 38, ly + 30), 180, 360, fill=NAVY, width=7)
    d.line((lx + 6, ly + 12, lx + 6, ly + 22), fill=NAVY, width=7); d.line((lx + 38, ly + 12, lx + 38, ly + 22), fill=NAVY, width=7)
    d.rounded_rectangle((lx, ly + 20, lx + 44, ly + 58), 8, fill=NAVY); d.ellipse((lx + 17, ly + 31, lx + 27, ly + 41), fill=YEL)
    d.text((x0 + 96, y0 + 14), txt, font=f, fill=NAVY)
    for k, line in enumerate(['우리 집도 이렇게 될까?', '친구추가 해두면 바로 상담 연결']):
        ff = F(BOLD, 48); w2 = d.textlength(line, font=ff)
        d.text((470 - w2 / 2, y0 + 140 + k * 70), line, font=ff, fill=WHITE if k == 0 else YEL)
    def fx(t, fr):
        q = ease((t - 0.2) / 0.35); fr.alpha_composite(with_alpha(Lk, q), (0, int((1 - q) * 30)))
    return dur, mid, T, fx, [(5, T_ADD), (4, T_CHAT)]
SC.append(s10)


# 11. CTA
def s11():
    dur = 3.8
    sub = ["댓글에 '한도' 남기면", '우리 집 남은 한도 DM으로'] if V == 'ig' else ['채널 이름 누르고 프로필 링크', '우리 집 남은 한도 1분이면 확인']
    return dur, photo(0, dur, -1, dark=0.1), text_layer([('우리 집 남은 한도', 0), ('지금 기준으로 확인', 1)], sub), None, []
SC.append(s11)


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
    drop = SC[0]()[0]; total = t + 8.0
    open(f'{OUT}/list.txt', 'w').write('\n'.join(lst + [f"file '{os.path.abspath(OUTRO)}'"]))
    subprocess.run(['python3', f'{TOOLS}/bgm_groove.py', f'{OUT}/bgm.wav', f'{total:.2f}', f'{drop:.2f}', '21', ','.join(sfx)], check=True)
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
