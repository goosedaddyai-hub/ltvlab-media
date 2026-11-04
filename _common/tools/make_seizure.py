# 쇼츠: 압류·연체 중에도 대출 될까? (실제 등기 2건) — 2026-11-05
# 사용: python3 make_seizure.py ig|yt [scene번호...]
import sys, os, re, html, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

V = sys.argv[1]
ONLY = [int(x) for x in sys.argv[2:]]
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


# ---------- 실사 소스 ----------
def clip(name, dur, y_off=0.5, speed=1.0):
    """세로 실사 영상 → 가운데 1080x660 띠. 길면 잘라 쓰고, 짧으면 끝에서 정지"""
    vf = f'setpts=PTS/{speed},fps={FPS},scale=1080:1920,crop=1080:{MID}:0:{int((1920 - MID) * y_off)}'
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{VID}/{name}.mp4', '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    fsz = W * MID * 3; frames = [raw[i:i + fsz] for i in range(0, len(raw) - fsz + 1, fsz)]
    def fn(t):
        i = min(int(t * FPS), len(frames) - 1)
        return Image.frombytes('RGB', (W, MID), frames[i])
    return fn


def photo(idx, dur, dirn=1, dark=0.0):
    src = Image.open(f'{IMG}/img{idx}.png').convert('RGB'); sw, sh = src.size; ar = W / MID
    bw, bh = (sw, sw / ar) if sw / sh < ar else (sh * ar, sh)
    def fn(t):
        z = 1 + 0.08 * t / dur; cw, ch = bw / z, bh / z
        x0 = (sw - cw) / 2 + dirn * (bw - cw) * 0.3; y0 = (sh - ch) / 2
        im = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, MID), Image.BILINEAR)
        return Image.blend(im, Image.new('RGB', im.size, NAVY), dark) if dark else im
    return fn


# ---------- 등기 (개인정보 모자이크) ----------
S = 3.0
NAMES = '이기용 한기환 진영목 이종열 김강훈 윤승만 김진경 허준 김보화 변승재 연경순'.split()
PAT = [r'\d{6}-\*', r'^\d{6}-', r'\d+동', r'\d+호', r'제\d+층', r'\d+층', r'^\d+-\d+$', r'\d{4}-\d{4}-\d{6}', r'^\d+-\d+\)?$']


def words(pdf, page):
    pg = open(f'{RL}/{pdf}.html', encoding='utf-8').read().split('<page ')[page]
    return [(*map(float, m.groups()[:4]), html.unescape(m.group(5))) for m in
            re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', pg)]


def blur_box(im, b):
    reg = im.crop(b); sm = reg.resize((max(1, reg.width // 14), max(1, reg.height // 14)))
    im.paste(sm.resize(reg.size, Image.NEAREST).filter(ImageFilter.GaussianBlur(3)), b)


_pg = {}
def page(pdf, p):
    if (pdf, p) in _pg: return _pg[(pdf, p)]
    base = f'{RL}/pg_{pdf}_{p}'
    subprocess.run(['pdftoppm', '-r', '216', '-f', str(p), '-l', str(p), '-png', '-singlefile', f'{RL}/{pdf}.pdf', base], check=True)
    im = Image.open(base + '.png').convert('RGB')
    for x0, y0, x1, y1, w in words(pdf, p):
        nm = next((n for n in NAMES if n in w), None)
        if nm:   # 이름 부분만 가림 (예: '7번변승재지분가압' → 이름만)
            i = w.index(nm); cw = (x1 - x0) / len(w)
            blur_box(im, (int((x0 + i * cw) * S) - 3, int(y0 * S) - 3, int((x0 + (i + len(nm)) * cw) * S) + 3, int(y1 * S) + 3))
        elif any(re.search(q, w) for q in PAT):
            blur_box(im, (int(x0 * S) - 4, int(y0 * S) - 3, int(x1 * S) + 4, int(y1 * S) + 3))
    _pg[(pdf, p)] = im
    return im


def doc(pdf, p, cy_pt, dur, rows, col=(255, 214, 0), t_hl=0.45, cx_pt=300, z1=0.16):
    """rows: [(y0,y1)] pt — 해당 줄 형광펜으로 쓱"""
    pg = page(pdf, p); cx, cy = cx_pt * S, cy_pt * S
    def fn(t):
        im = pg.copy().convert('RGBA')
        hl = Image.new('RGBA', im.size); d = ImageDraw.Draw(hl)
        for k, (a, b) in enumerate(rows):
            pk = ease((t - t_hl - k * 0.35) / 0.45)
            if pk > 0: d.rectangle((78 * S, a * S, (78 + (482 * pk)) * S, b * S), fill=col + (95,))
        im = Image.alpha_composite(im, hl).convert('RGB')
        z = 1.0 + z1 * ease(t / dur); ww = 1380 / z; hh = ww * MID / W
        return im.crop((cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2)).resize((W, MID), Image.LANCZOS)
    return fn


# ---------- 장면 ----------
SC = []; SFX = []   # (종류, 장면 내 초) → 전체 초로 변환


# 1. 훅: 세무서 압류 등기 + '압류' 도장
def s1():
    dur = 3.6
    T = text_layer([('세무서 압류에 연체까지', 0), ('대출, 끝난 걸까?', 1)],
                   ['집 있으면 얘기가 달라요', '실제 등기부등본으로 보여드릴게요'])
    st = stamp('압류', RED, 120, -10)
    return dur, doc('suwon', 3, 410, dur, [(427, 459)], col=(255, 90, 80), t_hl=0.2), T, stamp_fx(st, 0.9, W / 2 + 160, TOP + MID / 2 + 40), [(1, 0.9)]
SC.append(s1)


# 2. 은행은 바로 컷
def s2():
    dur = 3.4
    T = text_layer([('은행은 보통', 0), ('여기서 바로 컷', 1)],
                   ['연체·압류 기록 있으면', '은행·상호금융은 대부분 어려워요'])
    return dur, photo(2, dur, 1, dark=0.2), T, stamp_fx(stamp('부결', RED, 110, 10), 0.6), [(1, 0.6)]
SC.append(s2)


# 3. 전환: 담보대출은 집을 본다
def s3():
    dur = 3.4
    T = text_layer([('근데 담보대출은', 0), ("'집'을 먼저 봐요", 1)],
                   ['신용점수보다 중요한 건', '시세 대비 남은 한도(LTV)'])
    return dur, clip('49453997e718', dur, 0.45), T, None, []
SC.append(s3)


# 4. CASE 1 — 수원 세금 압류
def s4():
    dur = 5.0
    T = text_layer([('세금 밀려서', 0), ('세무서 압류 걸린 집', 1)],
                   ['2026년 8월 세무서 압류 등기', '은행 1순위 + 대부 후순위도 이미 있음'], chip='CASE 1  세금 체납', chipcol=CORAL)
    C = info_chip(['경기 수원 권선 · 73㎡ 구축 아파트', '갑구 5번 압류 (권리자: 국 · 수원세무서)'])
    def fx(t, fr):
        if t > 1.4: fr.alpha_composite(with_alpha(C, ease((t - 1.4) / 0.3)))
    return dur, doc('suwon', 3, 430, dur, [(427, 459)], t_hl=0.35), T, fx, [(2, 0.0)]
SC.append(s4)


# 5. CASE 1 해법 — 대출금으로 세금 먼저 → 압류 해제
def s5():
    dur = 5.4
    bg = Image.new('RGB', (W, MID), NAVY2)
    steps = [('1', '대출 실행', '시세 대비 남은 한도 안에서'), ('2', '체납 세금 바로 납부', '대출금에서 먼저 처리'),
             ('3', '압류 해제(말소)', '해제 조건으로 진행')]
    cards = []
    for n_, a, b in steps:
        c = Image.new('RGBA', (880, 170)); d = ImageDraw.Draw(c)
        d.rounded_rectangle((0, 0, 880, 170), 30, fill=(255, 255, 255, 248))
        d.ellipse((30, 35, 130, 135), fill=YEL); f = F(BLACK, 64); tw = d.textlength(n_, font=f)
        d.text((80 - tw / 2, 38), n_, font=f, fill=NAVY)
        d.text((165, 26), a, font=F(BLACK, 52), fill=NAVY); d.text((167, 100), b, font=F(BOLD, 34), fill=(90, 100, 125))
        cards.append(c)
    arrow = Image.new('RGBA', (60, 40)); ImageDraw.Draw(arrow).polygon([(0, 0), (60, 0), (30, 36)], fill=YEL)
    def mid(t):
        im = bg.copy().convert('RGBA')
        for i, c in enumerate(cards):
            p = ease((t - 0.25 - i * 0.55) / 0.35)
            if p <= 0: continue
            y = 22 + i * 214
            im.alpha_composite(with_alpha(c, p), (100 + int((1 - p) * 120), y))
            if i < 2 and t > 0.25 + i * 0.55 + 0.3: im.alpha_composite(arrow, (510, y + 174))
        return im.convert('RGB')
    T = text_layer([('대출금으로 세금부터 내고', 0), ('압류 풀면서 진행', 1)],
                   ["이른바 '압류 해제 조건부' 실행", '관건은 시세 대비 남은 한도'], handle=False)
    return dur, mid, T, None, [(2, 0.25), (2, 0.8), (2, 1.35)]
SC.append(s5)


# 6. CASE 2 — 사당 카드 연체 가압류 2건
def s6():
    dur = 5.0
    T = text_layer([('카드값 밀려서', 0), ('가압류 2건', 1)],
                   ['1월 국민카드, 2월 하나카드', '청구금액 합계 약 6,770만원'], chip='CASE 2  카드 연체', chipcol=CORAL)
    C = info_chip(['서울 동작 사당 · 59㎡ 구축 아파트', '공유자 1명 지분(1/5)에 가압류'])
    def fx(t, fr):
        if t > 1.6: fr.alpha_composite(with_alpha(C, ease((t - 1.6) / 0.3)))
    return dur, doc('sadang', 4, 610, dur, [(557, 612), (635, 690)], t_hl=0.35), T, fx, [(2, 0.0)]
SC.append(s6)


# 7. CASE 2 — 3월 경매 개시
def s7():
    dur = 4.2
    T = text_layer([('한 달 뒤엔', 0), ('경매 개시까지', 1)],
                   ['연체 방치하면', '몇 달 만에 여기까지 와요'])
    return dur, doc('sadang', 5, 190, dur, [(154, 214)], col=(255, 90, 80), t_hl=0.25), T, \
        stamp_fx(stamp('경매', RED, 120, 8), 1.0, W / 2 + 180, TOP + MID / 2 + 60), [(2, 0.0), (1, 1.0)]
SC.append(s7)


# 8. 근데 경매도 끝 아님
def s8():
    dur = 4.2
    T = text_layer([('근데 경매 들어가도', 0), ('끝난 거 아니에요', 1)],
                   ['낙찰(매각) 전에 대환으로 갚으면', '경매 취하까지 노려볼 수 있어요'])
    return dur, clip('a1359cf9584d', dur, 0.5), T, None, [(3, 0.0)]
SC.append(s8)


# 9. 한눈에 정리
def s9():
    dur = 5.6
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    x0, x1, y0 = 30, 930, TOP + 30
    rows = [('연체 중', '저축은행·캐피탈·대부', '담보대출로 길 찾기'),
            ('세금 압류', '대출금으로 세금 납부', '→ 압류 해제 조건'),
            ('가압류·경매', '매각 전에 대환 상환', '→ 해제·취하 진행')]
    rh = 170
    d.rounded_rectangle((x0, y0, x1, y0 + rh * 3 + 20), 30, fill=(255, 255, 255, 250))
    for i, (a, b, c) in enumerate(rows):
        y = y0 + 10 + i * rh
        if i: d.line((x0 + 24, y, x1 - 24, y), fill=(215, 220, 230), width=2)
        d.rounded_rectangle((x0 + 26, y + 46, x0 + 276, y + 124), 22, fill=CORAL if i else YEL)
        f = fit(d, a, BLACK, 40, 230); tw = d.textlength(a, font=f); d.text((x0 + 151 - tw / 2, y + 58), a, font=f, fill=NAVY)
        d.text((x0 + 306, y + 30), b, font=fit(d, b, BLACK, 44, 580), fill=NAVY)
        d.text((x0 + 308, y + 94), c, font=F(BOLD, 36), fill=(70, 85, 115))
    note = '한도·금리는 시세·선순위·연체 규모에 따라 달라요'; f = F(BOLD, 28); tw = d.textlength(note, font=f)
    d.text(((x0 + x1) / 2 - tw / 2, y0 + rh * 3 + 44), note, font=f, fill=SUB)
    T = text_layer([('압류·연체 있을 때', 0), ('한눈에 정리', 1)], [], handle=False)
    bg = Image.new('RGB', (W, MID), NAVY)
    def fx(t, fr):
        p = ease((t - 0.15) / 0.4); fr.alpha_composite(with_alpha(L, p), (0, int((1 - p) * 60)))
    return dur, (lambda t: bg), T, fx, [(2, 0.15)]
SC.append(s9)


# 9-2. 카카오톡 검색 → 채팅 상담
def s9b():
    dur = 4.6
    KY = (254, 229, 0); BR = (58, 29, 29); G = (120, 120, 128)
    bg = Image.new('RGB', (W, MID), (242, 243, 246))
    # 아바타: 네이비 원 + 베이지 지붕선 (엔딩과 같은 톤)
    av = Image.new('RGBA', (150, 150)); d = ImageDraw.Draw(av)
    d.ellipse((0, 0, 150, 150), fill=NAVY + (255,))
    d.line([(38, 78), (75, 42), (112, 78)], fill=(232, 214, 180, 255), width=9, joint='curve')
    d.line([(50, 70), (50, 104), (100, 104), (100, 70)], fill=(232, 214, 180, 255), width=9)
    name = 'LTV연구소'
    def mid(t):
        im = bg.copy().convert('RGBA'); d = ImageDraw.Draw(im)
        # 검색창
        d.rounded_rectangle((40, 40, 1040, 180), 70, fill=(255, 255, 255, 255), outline=KY + (255,), width=8)
        d.ellipse((92, 76, 146, 130), outline=BR + (255,), width=8); d.line((139, 123, 166, 150), fill=BR + (255,), width=10)
        n = int(len(name) * max(0, min(1, (t - 0.35) / 0.9))); typed = name[:n]
        if n == 0: d.text((196, 68), '카카오톡 검색', font=F(BOLD, 60), fill=(180, 180, 188))
        else: d.text((196, 58), typed, font=F(BLACK, 72), fill=(25, 25, 30))
        if int(t * 2.4) % 2 == 0 and t < 1.6:
            cx = 196 + d.textlength(typed, font=F(BLACK, 72)) + 8; d.rectangle((cx, 72, cx + 6, 150), fill=BR + (255,))
        # 검색 결과(채널)
        p = ease((t - 1.45) / 0.35)
        if p > 0:
            row = Image.new('RGBA', (980, 210)); r = ImageDraw.Draw(row)
            r.rounded_rectangle((0, 0, 980, 210), 34, fill=(255, 255, 255, 255))
            row.alpha_composite(av, (30, 30))
            r.text((206, 34), name, font=F(BLACK, 62), fill=(20, 20, 26))
            tw = r.textlength(name, font=F(BLACK, 62))
            r.rounded_rectangle((206 + tw + 18, 52, 206 + tw + 118, 100), 14, fill=KY + (255,))
            r.text((206 + tw + 38, 52), '채널', font=F(BLACK, 30), fill=BR)
            r.text((208, 124), '아파트 대출 한도·시세 상담', font=F(BOLD, 34), fill=G)
            # 채팅 버튼 (탭 효과)
            tap = ease((t - 2.4) / 0.25); press = 0.92 if 2.4 < t < 2.6 else 1.0
            bx0, by0, bx1, by1 = 700, 70, 900, 150
            cxm, cym = (bx0 + bx1) / 2, (by0 + by1) / 2; hw, hh = (bx1 - bx0) / 2 * press, (by1 - by0) / 2 * press
            r.rounded_rectangle((cxm - hw, cym - hh, cxm + hw, cym + hh), 40, fill=KY + (255,))
            f = F(BLACK, 40); r.text((cxm - r.textlength('채팅', font=f) / 2, cym - 28), '채팅', font=f, fill=BR)
            if t > 2.4:   # 손가락 탭 링
                rr = 30 + 70 * tap; a = int(200 * (1 - tap))
                if a > 8:
                    ring = Image.new('RGBA', row.size)
                    ImageDraw.Draw(ring).ellipse((cxm - rr, cym - rr, cxm + rr, cym + rr), outline=(255, 190, 0, a), width=8)
                    row.alpha_composite(ring)
            im.alpha_composite(with_alpha(row, p), (50, 220 + int((1 - p) * 50)))
        # 단계 안내
        steps = [('1', '검색'), ('2', '채널 추가'), ('3', '채팅으로 상담 신청')]
        x = 60
        for i, (k, s_) in enumerate(steps):
            q = ease((t - 2.7 - i * 0.18) / 0.3)
            if q <= 0: break
            f = F(BLACK, 40); w_ = d.textlength(s_, font=f) + 110
            chip = Image.new('RGBA', (int(w_), 92)); c = ImageDraw.Draw(chip)
            c.rounded_rectangle((0, 0, w_, 92), 46, fill=(NAVY if i < 2 else BR) + (255,))
            c.ellipse((14, 14, 78, 78), fill=KY + (255,)); c.text((46 - c.textlength(k, font=F(BLACK, 40)) / 2, 16), k, font=F(BLACK, 40), fill=BR)
            c.text((94, 16), s_, font=f, fill=(255, 255, 255))
            im.alpha_composite(with_alpha(chip, q), (x, 500 + int((1 - q) * 30))); x += int(w_) + 18
        return im.convert('RGB')
    T = text_layer([('상담은 카톡으로', 0), ("'LTV연구소' 검색", 1)], [], handle=False)
    # 기밀 엄수 배지 (자물쇠) + 보조 문구 — 오른쪽 버튼 구간 피해 왼쪽 중심
    Lk = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(Lk)
    f = F(BLACK, 54); txt = '상담 요청·내용 기밀 엄수'; tw = d.textlength(txt, font=f)
    x0 = 470 - (tw + 120) / 2; y0 = TOP + MID + 56
    d.rounded_rectangle((x0, y0, x0 + tw + 120, y0 + 104), 52, fill=YEL)
    lx, ly = x0 + 34, y0 + 26          # 자물쇠
    d.arc((lx + 6, ly - 6, lx + 38, ly + 30), 180, 360, fill=NAVY, width=7)
    d.line((lx + 6, ly + 12, lx + 6, ly + 22), fill=NAVY, width=7); d.line((lx + 38, ly + 12, lx + 38, ly + 22), fill=NAVY, width=7)
    d.rounded_rectangle((lx, ly + 20, lx + 44, ly + 58), 8, fill=NAVY); d.ellipse((lx + 17, ly + 31, lx + 27, ly + 41), fill=YEL)
    d.text((x0 + 96, y0 + 14), txt, font=f, fill=NAVY)
    for k, line in enumerate(['댓글 안 남겨도 괜찮아요', '1:1 채팅으로 조용히 상담 신청']):
        ff = F(BOLD, 48); w2 = d.textlength(line, font=ff)
        d.text((470 - w2 / 2, y0 + 140 + k * 70), line, font=ff, fill=WHITE if k == 0 else YEL)
    def fx(t, fr):
        q = ease((t - 0.2) / 0.35); fr.alpha_composite(with_alpha(Lk, q), (0, int((1 - q) * 30)))
    return dur, mid, T, fx, []
SC.append(s9b)


# 10. 핵심은 타이밍 + CTA
def s10():
    dur = 4.4
    sub = ["댓글 부담되면 카톡 'LTV연구소'", '비밀 보장 1:1로 한도 확인'] if V == 'ig' else ['채널 이름 누르고 프로필 링크', '우리 집 남은 한도 1분이면 확인']
    return dur, clip('d41c4fe9a7ce', dur, 0.55), text_layer([("핵심은 '타이밍'", 0), ('경매 전에 한도부터', 1)], sub), None, []
SC.append(s10)


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


if __name__ == '__main__':
    for i, fn in enumerate(SC):
        if ONLY and i + 1 not in ONLY: continue
        render_scene(i + 1, fn); print('scene', i + 1, 'ok', flush=True)
