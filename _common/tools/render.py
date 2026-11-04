# 릴스: 은행 막혀도 우리는 되는 이유 + A/B 타겟 (2026-11-04)
# 사용: python3 render.py ig|yt [scene번호...]
import sys, os, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from docs import render as render_page, words

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
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]
HANDLE = '@ltv_lab_kr' if V == 'yt' else '@ltv.lab'
IMG = '/home/claude/ltvlab-media/_raw/2026-10-26_jeonse-ban'
OUT = f'/home/claude/rl/out_{V}'; os.makedirs(OUT, exist_ok=True)

ease = lambda x: 1 - (1 - max(0, min(1, x))) ** 3
clamp = lambda x: max(0.0, min(1.0, x))


def fit(d, text, path, size, maxw):
    while size > 24:
        if d.textlength(text, font=F(path, size)) <= maxw: return F(path, size)
        size -= 2
    return F(path, size)


# ---------- 공통 레이어 ----------
def text_layer(head, sub, src='', chip=None, chipcol=YEL, sub_y=None, handle=True):
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
        tw = t.textlength(s, font=f)
        t.text(((W - tw) / 2, y), s, font=f, fill=YEL if em else WHITE); y += h
    cx = 470; y = sub_y or TOP + MID + 60
    for k, s in enumerate(sub):
        f = fit(t, s, BOLD, 56, 820); tw = t.textlength(s, font=f)
        t.text((cx - tw / 2, y), s, font=f, fill=WHITE if k == 0 else YEL); y += f.size + 26
    if src:
        f = F(BOLD, 26); tw = t.textlength(src, font=f)
        t.text((cx - tw / 2, y + 8), src, font=f, fill=SUB)
    if handle:
        f = F(BOLD, 28); tw = t.textlength(HANDLE, font=f)
        t.rounded_rectangle((40, TOP + 24, 40 + tw + 36, TOP + 72), 24, fill=(20, 33, 61, 190))
        t.text((58, TOP + 30), HANDLE, font=f, fill=WHITE)
    return L


def photo(idx, dur, dirn=1, dark=0.0):
    src = Image.open(f'{IMG}/img{idx}.png').convert('RGB')
    sw, sh = src.size; ar = W / MID
    bw, bh = (sw, sw / ar) if sw / sh < ar else (sh * ar, sh)
    def fn(t):
        z = 1 + 0.08 * t / dur
        cw, ch = bw / z, bh / z
        x0 = (sw - cw) / 2 + dirn * (bw - cw) * 0.3; y0 = (sh - ch) / 2
        im = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, MID), Image.BILINEAR)
        if dark: im = Image.blend(im, Image.new('RGB', im.size, NAVY), dark)
        return im
    return fn


_pages = {}
def page(pdf, p):
    k = (pdf, p)
    if k not in _pages:
        out = f'/home/claude/rl/pg_{pdf}_{p}.png'
        if not os.path.exists(out): render_page(f'/home/claude/rl/{pdf}.pdf', p, out)
        _pages[k] = Image.open(out).convert('RGB')
    return _pages[k]


def doc(pdf, p, ky, dur, t_hl=0.5):
    """을구 한 줄을 크게 보여주고 형광펜으로 쓱 칠하기"""
    pg = page(pdf, p).copy()
    S = 3
    # 형광 칠할 박스(소스 px): 날짜칸 + 채권최고액 줄 + 근저당권자 줄
    boxes = [(180 * S, (ky - 2) * S, 256 * S, (ky + 13) * S),
             (343 * S, (ky - 2) * S, 560 * S, (ky + 13) * S)]
    for w in words(f'/home/claude/rl/{pdf}.pdf', p):
        if w[4] == '근저당권자' and ky < w[1] < ky + 80:
            boxes.append((343 * S, (w[1] - 2) * S, 560 * S, (w[1] + 13) * S)); break
    hl = Image.new('RGBA', pg.size)
    cx, cy = 370 * S, (ky + 28) * S
    def fn(t):
        im = pg.copy()
        prog = ease((t - t_hl) / 0.55)
        if prog > 0:
            d = ImageDraw.Draw(hl); d.rectangle((0, 0) + pg.size, fill=(0, 0, 0, 0))
            for k, (a, b, c, e) in enumerate(boxes):
                pk = ease((t - t_hl - k * 0.18) / 0.45)
                if pk > 0: d.rectangle((a, b, a + (c - a) * pk, e), fill=(255, 214, 0, 120))
            im = Image.alpha_composite(im.convert('RGBA'), hl).convert('RGB')
        z = 1.0 + 0.18 * ease(t / dur)
        ww = 1380 / z; hh = ww * MID / W
        x0 = cx - ww / 2; y0 = cy - hh / 2
        return im.crop((x0, y0, x0 + ww, y0 + hh)).resize((W, MID), Image.LANCZOS)
    return fn


def info_chip(lines, y=TOP + MID - 150, col=NAVY):
    """서류 위 정보 라벨(왼쪽 아래)"""
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    f1, f2 = F(BLACK, 38), F(BOLD, 30)
    w_ = max(d.textlength(lines[0], font=f1), d.textlength(lines[1], font=f2)) + 56
    d.rounded_rectangle((36, y, 36 + w_, y + 116), 22, fill=col + (235,))
    d.rectangle((36, y + 20, 44, y + 96), fill=YEL)
    d.text((64, y + 12), lines[0], font=f1, fill=YEL)
    d.text((64, y + 64), lines[1], font=f2, fill=WHITE)
    return L


def with_alpha(L, a):
    if a >= 1: return L
    r, g, b, al = L.split(); al = al.point(lambda v: int(v * a)); return Image.merge('RGBA', (r, g, b, al))


# ---------- 장면 ----------
SC = []

# 1. 훅: 은행 접수 마감 + 카뱅 오픈런
def s1():
    dur = 3.6; ph = photo(2, dur, 1, dark=0.15)
    T = text_layer([('시중은행 주담대', 0), ("줄줄이 '접수 마감'", 1)],
                   ['카뱅만 보고 새벽 6시 오픈런', '그마저도 몇 초 만에 마감'], '출처: SBS Biz·YTN 보도 (2026.8)')
    st = Image.new('RGBA', (560, 220)); d = ImageDraw.Draw(st)
    d.rounded_rectangle((8, 8, 552, 212), 26, outline=RED + (255,), width=14)
    f = F(BLACK, 110); tw = d.textlength('접수 마감', font=f)
    d.text(((560 - tw) / 2, 30), '접수 마감', font=f, fill=RED + (255,))
    st = st.rotate(12, expand=True, resample=Image.BICUBIC)
    ck = Image.new('RGBA', (300, 90)); d = ImageDraw.Draw(ck)
    d.rounded_rectangle((0, 0, 300, 90), 45, fill=(0, 0, 0, 170))
    d.text((40, 12), 'AM 6:00', font=F(BLACK, 56), fill=WHITE)
    def fx(t, fr):
        if t > 0.35:
            p = ease((t - 0.35) / 0.18); s = 1.8 - 0.8 * p
            im = st.resize((int(st.width * s), int(st.height * s)))
            im = with_alpha(im, p)
            fr.alpha_composite(im, (int(W / 2 - im.width / 2), int(TOP + MID / 2 - im.height / 2)))
        if t > 1.4:
            fr.alpha_composite(with_alpha(ck, ease((t - 1.4) / 0.25)), (W - 340, TOP + 24))
    return dur, ph, T, fx
SC.append(s1)

# 2. 전환: 근데 대출 나간 집이 있다
def s2():
    dur = 3.0
    return dur, photo(0, dur, -1), text_layer([('근데 지금도', 0), ('대출 나간 집, 있어요', 1)],
                                              ['말로만 하는 거 아니고', '실제 등기부등본으로 보여드릴게요']), None
SC.append(s2)

# 3. 등기 6건 몽타주
DOCS = [('377edd53', '서울 강남구 · 아파트'), ('403326f4', '서울 강동구 · 아파트'), ('94358843', '서울 강서구 · 아파트'),
        ('c8b0fd77', '서울 성동구 · 연립'), ('a9bcf377', '경기 광명 · 신축'), ('67ae836a', '경기 고양 · 아파트')]
def s3():
    dur = 4.0
    bg = Image.new('RGB', (W, MID), (232, 226, 214)); d = ImageDraw.Draw(bg)
    for x in range(0, W, 6): d.line((x, 0, x, MID), fill=(226, 219, 206))   # 책상 느낌
    cards = []
    for pdf, lab in DOCS:
        pg = page(pdf, 1).crop((40, 120, 1746, 1180)).resize((820, 510), Image.LANCZOS)
        c = Image.new('RGBA', (840, 560), (0, 0, 0, 0)); c.paste(pg, (10, 10))
        dd = ImageDraw.Draw(c); f = F(BLACK, 32); tw = dd.textlength(lab, font=f)
        dd.rounded_rectangle((20, 470, 20 + tw + 40, 530), 18, fill=NAVY); dd.text((40, 476), lab, font=f, fill=YEL)
        sh = Image.new('RGBA', (900, 620)); ImageDraw.Draw(sh).rectangle((40, 44, 860, 574), fill=(0, 0, 0, 90))
        sh = sh.filter(ImageFilter.GaussianBlur(14)); sh.alpha_composite(c, (30, 30))
        cards.append(sh)
    rots = [-4, 3, -2, 4, -3, 1.5]
    def mid(t):
        im = bg.copy().convert('RGBA')
        for i, c in enumerate(cards):
            t0 = 0.15 + i * 0.55
            if t < t0: break
            p = ease((t - t0) / 0.32)
            r = c.rotate(rots[i] * (0.4 + 0.6 * p) + (1 - p) * 15, expand=True, resample=Image.BICUBIC)
            x = int((W - r.width) / 2 + (1 - p) * 900); y = int((MID - r.height) / 2 + 10)
            im.alpha_composite(r, (x, y))
        return im.convert('RGB')
    T = text_layer([('최근 대출 실행된 등기', 0), ('6건 직접 떼봤어요', 1)], ['아파트·신축·연립까지', '이름·동호수만 가렸어요'])
    return dur, mid, T, None
SC.append(s3)

# 4. 은행이 막힌 진짜 이유
def s4():
    dur = 3.4
    return dur, photo(2, dur, -1, dark=0.35), text_layer([('은행이 막힌 진짜 이유', 1)],
        ["은행마다 '1년 대출 총량'이 꽉 찬 것", '집이 문제가 아니라 창구가 닫힌 거예요']), None
SC.append(s4)

# 5. 우리는 전 금융권 비교
def s5():
    dur = 4.4; ph = photo(0, dur, 1, dark=0.62)
    items = [('시중은행', 0), ('인터넷은행', 0), ('신협', 1), ('새마을금고', 1), ('수협·농협', 1), ('저축은행', 1), ('캐피탈', 1), ('대부금융', 1)]
    chips = []
    for name, ok in items:
        c = Image.new('RGBA', (440, 104)); d = ImageDraw.Draw(c)
        d.rounded_rectangle((0, 0, 440, 104), 26, fill=(255, 255, 255, 240) if ok else (90, 100, 125, 230))
        d.text((30, 22), name, font=F(BLACK, 44), fill=NAVY if ok else (200, 205, 215))
        tag, col = ('가능', GREEN) if ok else ('막힘', RED)
        d.rounded_rectangle((300, 24, 418, 80), 18, fill=col); d.text((318, 26), tag, font=F(BLACK, 38), fill=WHITE)
        if not ok: d.line((26, 54, 30 + d.textlength(name, font=F(BLACK, 44)), 54), fill=RED, width=6)
        chips.append(c)
    def fx(t, fr):
        for i, c in enumerate(chips):
            t0 = 0.3 + i * 0.16
            if t < t0: continue
            p = ease((t - t0) / 0.25)
            x = 70 + (i % 2) * 490; y = TOP + 70 + (i // 2) * 130 + int((1 - p) * 40)
            fr.alpha_composite(with_alpha(c, p), (x, y))
    T = text_layer([('그럼 우리는 왜 될까?', 1)], ['은행 1곳이 아니라 전 금융권에', '동시에 넣고 되는 곳을 찾아요'], handle=False)
    return dur, ph, T, fx
SC.append(s5)

# 6. 당신은 A? B?
def s6():
    dur = 4.0
    bg = Image.new('RGB', (W, MID), NAVY2)
    def card(letter, l1, l2, col):
        c = Image.new('RGBA', (470, 560)); d = ImageDraw.Draw(c)
        d.rounded_rectangle((0, 0, 470, 560), 34, fill=(255, 255, 255, 250))
        d.ellipse((165, 40, 305, 180), fill=col); f = F(BLACK, 96); tw = d.textlength(letter, font=f)
        d.text((235 - tw / 2, 40), letter, font=f, fill=NAVY)
        for k, s in enumerate(l1):
            f = fit(d, s, BLACK, 44, 420); tw = d.textlength(s, font=f); d.text((235 - tw / 2, 220 + k * 64), s, font=f, fill=NAVY)
        f = F(BOLD, 32); tw = d.textlength(l2, font=f); d.text((235 - tw / 2, 470), l2, font=f, fill=(90, 100, 125))
        return c
    A = card('A', ['조건은 좋은데', '금리·한도가', '걱정이다'], '신용·소득 괜찮은 분', YEL)
    B = card('B', ['금리보다', '일단 나오는 게', '먼저다'], '급하거나 상황 안 좋은 분', CORAL)
    def mid(t):
        im = bg.copy().convert('RGBA')
        for i, c in enumerate((A, B)):
            p = ease((t - 0.2 - i * 0.35) / 0.35)
            if p <= 0: continue
            im.alpha_composite(with_alpha(c, p), (45 + i * 520, 50 + int((1 - p) * 80)))
        return im.convert('RGB')
    T = text_layer([('지금 내 상황은', 0), ('A? B?', 1)], ['둘 다 됩니다', '근데 가는 길이 완전히 달라요'], handle=False)
    return dur, mid, T, None
SC.append(s6)

# 7. A 상세 — 상호금융 1순위 (강동 명일 등기)
def s7():
    dur = 4.8
    T = text_layer([('금리·한도 둘 다 챙기기', 1)], ['신협·새마을금고 같은 상호금융', '1순위로 크게, 금리는 낮게'],
                   chip='A  조건 좋은 분', chipcol=YEL)
    C = info_chip(['서울 강동 · 81㎡ 아파트', '2026.4 신협 1순위 · 최고액 14.88억'])
    def fx(t, fr):
        if t > 1.3: fr.alpha_composite(with_alpha(C, ease((t - 1.3) / 0.3)))
    return dur, doc('403326f4', 9, 560.6, dur), T, fx
SC.append(s7)

# 8. B 상세 — 후순위·2금융 (광명 신축 → 강서 등촌)
def s8():
    dur = 5.6
    d1 = doc('a9bcf377', 3, 598.6, 2.8); d2 = doc('94358843', 13, 273.6, 2.8)
    T = text_layer([("일단 '나오게' 만들기", 1)], ['기존 대출 있어도 후순위로 추가', '저축은행·캐피탈로 승인 먼저'],
                   chip='B  상황이 급한 분', chipcol=CORAL)
    C1 = info_chip(['경기 광명 · 신축 49㎡', '10.23 설정 · 1순위 농협 + 후순위 2.47억'])
    C2 = info_chip(['서울 강서 · 85㎡ 아파트', '9.30 설정 · 압류 이력 있던 집도 3.5억'])
    def mid(t): return d1(t) if t < 2.8 else d2(t - 2.8)
    def fx(t, fr):
        if 1.0 < t < 2.8: fr.alpha_composite(with_alpha(C1, ease((t - 1.0) / 0.3)))
        if t > 3.8: fr.alpha_composite(with_alpha(C2, ease((t - 3.8) / 0.3)))
        if 2.8 <= t < 2.9: fr.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(200 * (1 - (t - 2.8) / 0.1)))))
    return dur, mid, T, fx
SC.append(s8)

# 9. A vs B 비교표
def s9():
    dur = 5.0
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    x0, x1, y0 = 30, 930, TOP + 36
    cols = [x0, x0 + 170, x0 + 535, x1]
    rows = [('이런 분', ['신용·소득 OK', '금리·한도 고민'], ['연체·기존대출', '급한 자금 필요']),
            ('금융사', ['신협·새마을금고', '수협·농협'], ['저축은행·캐피탈', '대부금융']),
            ('순위', ['1순위', '신규·대환'], ['후순위', '추가 가능']),
            ('핵심', ['한도↑ 금리↓', ''], ['승인·속도', '우선'])]
    rh = 168; hh = 96; y1 = y0 + hh + rh * len(rows)
    d.rounded_rectangle((x0, y0, x1, y1), 30, fill=(255, 255, 255, 250))
    d.rounded_rectangle((cols[1] + 8, y0 + 14, cols[2] - 8, y0 + hh - 6), 20, fill=YEL)
    d.rounded_rectangle((cols[2] + 8, y0 + 14, cols[3] - 14, y0 + hh - 6), 20, fill=CORAL)
    for lab, cx, col in (('A안', (cols[1] + cols[2]) / 2, NAVY), ('B안', (cols[2] + cols[3]) / 2, NAVY)):
        f = F(BLACK, 46); tw = d.textlength(lab, font=f); d.text((cx - tw / 2, y0 + 20), lab, font=f, fill=col)
    y = y0 + hh
    for lab, a, b in rows:
        d.line((x0 + 20, y, x1 - 20, y), fill=(215, 220, 230), width=2)
        f = F(BLACK, 36); tw = d.textlength(lab, font=f)
        d.text(((cols[0] + cols[1]) / 2 - tw / 2, y + rh / 2 - 28), lab, font=f, fill=(110, 120, 140))
        for vals, c0, c1 in ((a, cols[1], cols[2]), (b, cols[2], cols[3])):
            vs = [v for v in vals if v]; vy = y + (rh - len(vs) * 54) / 2 - 6
            for j, v in enumerate(vs):
                f = fit(d, v, BLACK if j == 0 else BOLD, 40, c1 - c0 - 30); tw = d.textlength(v, font=f)
                d.text(((c0 + c1) / 2 - tw / 2, vy), v, font=f, fill=NAVY if j == 0 else (70, 85, 115)); vy += 54
        y += rh
    d.line((cols[2], y0 + hh + 10, cols[2], y1 - 16), fill=(215, 220, 230), width=2)
    note = '금리·한도는 신용·소득·담보에 따라 달라요'; f = F(BOLD, 28); tw = d.textlength(note, font=f)
    d.text(((x0 + x1) / 2 - tw / 2, y1 + 26), note, font=f, fill=SUB)
    T = text_layer([('한눈에 비교', 0), ('A안 vs B안', 1)], [], handle=False)
    bg = Image.new('RGB', (W, MID), NAVY)
    def fx(t, fr):
        p = ease((t - 0.15) / 0.4)
        fr.alpha_composite(with_alpha(L, p), (0, int((1 - p) * 60)))
    return dur, (lambda t: bg), T, fx
SC.append(s9)

# 10. CTA
def s10():
    dur = 3.8
    sub = ["댓글에 '한도' 남겨주세요", 'A·B 중 맞는 길로 DM 드려요'] if V == 'ig' else ['채널 이름 누르고 프로필 링크', '우리 아파트 한도 1분이면 확인']
    return dur, photo(3, dur, 1), text_layer([('내 상황은 A? B?', 0), ('한도부터 확인하세요', 1)], sub), None
SC.append(s10)


def render_scene(i, fn):
    dur, mid, T, fx = fn()
    n = int(round(dur * FPS)); tmp = f'{OUT}/s{i:02d}.tmp.mp4'; out = f'{OUT}/s{i:02d}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    snaps = {int(n * 0.85)}
    for k in range(n):
        t = k / FPS
        fr = Image.new('RGBA', (W, H), NAVY + (255,))
        fr.paste(mid(t), (0, TOP))
        fr.alpha_composite(with_alpha(T, ease(t / 0.3)))
        if fx: fx(t, fr)
        rgb = fr.convert('RGB')
        if k in snaps: rgb.save(f'{OUT}/snap{i:02d}.jpg', quality=85)
        p.stdin.write(rgb.tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    return dur


if __name__ == '__main__':
    total = 0
    for i, fn in enumerate(SC):
        if ONLY and i + 1 not in ONLY:
            continue
        total += render_scene(i + 1, fn); print('scene', i + 1, 'ok', flush=True)
    print('total', total)
