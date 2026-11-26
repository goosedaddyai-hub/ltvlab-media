# 쇼츠: 11/26 기준금리 0.25%p 인상 → 주담대 부담·은행 금리 전가·갈아타기 (2026-11-26)
# 스타일: 11/23 rate-outlook 계열(어두운 실사 + 상단 로고 + 칩·헤드라인 + 하단 자막), 나레이션 Supertonic M1 1.3배
# 사용: python3 make_hike.py ig|yt tts | snap | render [n...] | build
import sys, os, re, json, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

V = sys.argv[1]; CMD = sys.argv[2] if len(sys.argv) > 2 else 'render'
ONLY = [int(x) for x in sys.argv[3:] if x.isdigit()]
W, H, FPS = 1080, 1920, 30
NAVY = (14, 24, 48); WHITE = (255, 255, 255); ORG = (255, 138, 40); RED = (240, 72, 66)
BLUE = (84, 160, 255); GRAY = (170, 182, 205); GREEN = (52, 210, 140); YEL = (255, 201, 40)
TOOLS = os.path.dirname(os.path.abspath(__file__))
FD = f'{TOOLS}/../fonts'; BLACK = f'{FD}/Pretendard-Black.otf'; XB = f'{FD}/Pretendard-ExtraBold.otf'; BOLD = f'{FD}/Pretendard-Bold.otf'
IMG = f'{TOOLS}/../../_raw/2026-11-11_rate-compare'
WORK = '/home/claude/hike'; OUT = f'{WORK}/out_{V}'; TTS = f'{WORK}/tts_{V}'
os.makedirs(OUT, exist_ok=True); os.makedirs(TTS, exist_ok=True)
_fc = {}
def F(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]
ease = lambda x: 1 - (1 - max(0.0, min(1.0, x))) ** 3
COL = {'o': ORG, 'r': RED, 'b': BLUE, 'g': GREEN, 'y': YEL, 'w': WHITE}
SUBX = 480          # 자막 중심 (오른쪽 버튼 구간 회피)


def segs(s, base):
    return [(m.group(3), base) if m.group(3) else (m.group(2), COL[m.group(1)])
            for m in re.finditer(r'\[([a-z])\](.*?)\[/\]|([^\[]+)', s)]


def ctext(d, cx, y, s, path, size, maxw, base=WHITE, stroke=0, alpha=255):
    sg = segs(s, base)
    while size > 22 and sum(d.textlength(a, font=F(path, size)) for a, _ in sg) > maxw: size -= 2
    f = F(path, size); tw = sum(d.textlength(a, font=f) for a, _ in sg); x = cx - tw / 2
    for a, c in sg:
        if stroke: d.text((x, y), a, font=f, fill=c + (alpha,), stroke_width=stroke, stroke_fill=(10, 16, 34, alpha))
        else: d.text((x, y), a, font=f, fill=c + (alpha,))
        x += d.textlength(a, font=f)
    return f


def with_alpha(L, a):
    if a >= 1: return L
    r, g, b, al = L.split(); return Image.merge('RGBA', (r, g, b, al.point(lambda v: int(v * a))))


# ---------- 배경 ----------
_grad = None
def grad():
    global _grad
    if _grad is None:
        a = np.zeros((H,), np.float32)
        for y in range(H):
            a[y] = 0.62 + 0.30 * max(0, (y - 700) / 1220) + 0.12 * max(0, 1 - y / 500)
        a = np.clip(a, 0, 0.97)
        A = (np.repeat(a[:, None], W, 1) * 255).astype(np.uint8)
        _grad = Image.merge('RGBA', [Image.new('L', (W, H), c) for c in NAVY] + [Image.fromarray(A)])
    return _grad


_src = {}
def bg(name, t, dur, dirn=1):
    if name not in _src:
        _src[name] = Image.open(f'{IMG}/{name}.jpg').convert('RGB').resize((W + 120, H + 214)).filter(ImageFilter.GaussianBlur(3))
    src = _src[name]; z = 1 + 0.06 * t / dur
    cw, ch = src.width / z, src.height / z
    x0 = (src.width - cw) / 2 + dirn * (src.width - cw) * 0.35; y0 = (src.height - ch) / 2
    fr = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR).convert('RGBA')
    fr.alpha_composite(grad()); return fr


# ---------- 공통 ----------
def logo(d):
    x, y = 64, 92
    d.line((x, y + 22, x + 22, y + 2, x + 44, y + 22), fill=WHITE, width=5, joint='curve')
    d.line((x + 7, y + 17, x + 7, y + 44, x + 37, y + 44, x + 37, y + 17), fill=WHITE, width=5)
    d.rectangle((x + 17, y + 30, x + 27, y + 44), fill=WHITE)
    d.text((x + 58, y + 2), 'LTV연구소', font=F(XB, 36), fill=WHITE)


def header(d, chip, lines, y0=270, chipcol=RED, a=255):
    y = y0
    if chip:
        tag, rest = chip if isinstance(chip, tuple) else (chip, '')
        cf = F(XB, 36); tw = d.textlength(tag, font=cf); rw = d.textlength(rest, font=cf) if rest else 0
        tot = tw + 48 + (rw + 18 if rest else 0); x = (W - tot) / 2
        d.rounded_rectangle((x, y, x + tw + 48, y + 62), 31, fill=chipcol + (a,))
        d.text((x + 24, y + 9), tag, font=cf, fill=WHITE + (a,))
        if rest: d.text((x + tw + 66, y + 9), rest, font=cf, fill=WHITE + (a,))
        y += 96
    for s in lines:
        f = ctext(d, W / 2, y, s, BLACK, 84, W - 110, alpha=a); y += f.size + 20
    return y


def subtitle(d, s, a=255):
    lines = s.split('\n'); y = 1370 - (len(lines) - 1) * 34
    for ln in lines:
        f = ctext(d, SUBX, y, ln, XB, 50, 850, stroke=5, alpha=a); y += f.size + 18


def foot(d, s, y=1250, x=80):
    d.text((x, y), s, font=F(BOLD, 26), fill=GRAY)


def handle(d):
    h = '@ltv_lab_kr' if V == 'yt' else '@ltv.lab'
    d.text((W - 64 - d.textlength(h, font=F(BOLD, 30)), 98), h, font=F(BOLD, 30), fill=(210, 218, 235))


def panel(x0, y0, x1, y1, fill=(20, 34, 66, 225)):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((x0, y0, x1, y1), 30, fill=fill); return L, d


# ---------- 장면 정의: (배경, 방향, [(자막, 읽기)], draw(t, T)) ----------
#   T = 각 자막 청크 시작시각 리스트 (TTS 길이로 결정)
SC = []
def scene(bgname, dirn, chunks):
    def deco(fn): SC.append((bgname, dirn, chunks, fn)); return fn
    return deco


CTA_IG = [("댓글에 '[o]한도[/]' 남기면", '댓글에 한도 남기면'),
          ('우리 집 [o]최대 한도[/]랑\n[o]갈아타면 줄어드는 이자[/]까지 DM으로', '우리 집 최대 한도랑, 갈아타면 줄어드는 이자까지 디엠으로 보내드려요.')]
CTA_YT = [('[o]채널 이름[/] 누르고 프로필 링크', '채널 이름 누르고 프로필 링크에서'),
          ('우리 집 [o]한도[/]·[o]갈아타기 이자[/]\n1분이면 확인돼요', '우리 집 한도랑 갈아타기 이자, 1분이면 확인돼요.')]


@scene('c10', 1, [('처음 받을 땐 [o]3%[/]였던 주담대', '처음 받을 땐 삼 퍼센트였던 주담대.'),
                  ('이제 [r]7% 코앞[/]인데', '이제 칠 퍼센트 코앞인데,'),
                  ('[r]오늘 또 올랐어요[/]', '오늘 또 올랐어요.')])
def s1(t, T):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    header(d, ('속보', '11/26 · 기준금리 인상'), ['3%로 받은 주담대', '지금 [r]7% 코앞[/]?'])
    # 카운터 3.0 → 6.9
    p = ease((t - T[1] + 0.2) / 1.1)
    v = 3.0 + 3.9 * p if t > T[1] - 0.2 else 3.0
    col = tuple(int(ORG[i] + (RED[i] - ORG[i]) * p) for i in range(3))
    s = f'{v:.1f}%'; f = F(BLACK, 250); tw = d.textlength(s, font=f)
    d.text(((W - tw) / 2, 590), s, font=f, fill=col, stroke_width=8, stroke_fill=(10, 16, 34))
    lab = '처음 받을 때 금리' if p < 0.5 else '지금 은행 금리 상단'
    lf = F(XB, 40); d.text(((W - d.textlength(lab, font=lf)) / 2, 885), lab, font=lf, fill=GRAY)
    if t > T[2]:
        q = ease((t - T[2]) / 0.25); st = Image.new('RGBA', (520, 170)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle((6, 6, 514, 164), 24, outline=RED, width=12)
        sf = F(BLACK, 96); sd.text((260 - sd.textlength('또 인상', font=sf) / 2, 20), '또 인상', font=sf, fill=RED)
        st = st.rotate(-8, expand=True, resample=Image.BICUBIC); sc = 1.6 - 0.6 * q
        st = with_alpha(st.resize((int(st.width * sc), int(st.height * sc))), q)
        L.alpha_composite(st, (int(W / 2 - st.width / 2), int(1010 - st.height / 2 + 60)))
    foot(d, '※ 7%: 시중은행 주담대 금리 상단 기준 (고정형 상단 6.65%, 10월 말)', 1265)
    return L


@scene('c11', -1, [('오늘 한국은행이 기준금리를', '오늘 한국은행이 기준금리를'),
                   ('[o]3.25%[/]로 [r]0.25%p[/] 올렸어요', '삼 점 이오 퍼센트로, 영 점 이오 퍼센트 포인트 올렸어요.'),
                   ('하반기에만 [r]벌써 세 번째[/]', '하반기에만 벌써 세 번째.'),
                   ('2년여 만에 [o]최고 수준[/]이에요', '이 년여 만에 최고 수준이에요.')])
def s2(t, T):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    header(d, ('속보', '11/26 금통위'), ['기준금리 [r]또 인상[/]'])
    p = ease((t - T[1]) / 0.4)
    fa, fb = F(BLACK, 92), F(BLACK, 140)
    wa, wb = d.textlength('3.00%', font=fa), d.textlength('3.25%', font=fb); x = (W - (wa + 110 + wb)) / 2
    d.text((x, 535), '3.00%', font=fa, fill=GRAY)
    d.line((x + wa + 18, 590, x + wa + 70, 590), fill=GRAY, width=10); d.polygon(((x + wa + 70, 570), (x + wa + 96, 590), (x + wa + 70, 610)), fill=GRAY)
    if p > 0:
        f = fb; s = '3.25%'
        d.text((x + wa + 110 - (1 - p) * 40, 500), s, font=f, fill=ORG + (int(255 * p),), stroke_width=6, stroke_fill=(10, 16, 34, int(255 * p)))
        bf = F(XB, 40); b = '+0.25%p'; bw = d.textlength(b, font=bf)
        d.rounded_rectangle((x + wa + 110 + wb / 2 - bw / 2 - 22, 680, x + wa + 110 + wb / 2 + bw / 2 + 22, 742), 31, fill=RED + (int(255 * p),))
        d.text((x + wa + 110 + wb / 2 - bw / 2, 688), b, font=bf, fill=WHITE + (int(255 * p),))
    # 타임라인
    q = ease((t - T[2] + 0.1) / 0.4)
    if q > 0:
        P, pd = panel(80, 800, 920, 1150); L.alpha_composite(with_alpha(P, q)); d = ImageDraw.Draw(L)
        d.text((120, 830), '2026 기준금리 흐름', font=F(XB, 34), fill=(210, 218, 235, int(255 * q)))
        items = [('7월', '2.75', 1), ('8월', '3.00', 1), ('10월', '동결', 0), ('11월', '3.25', 1)]
        for k, (m, v, up) in enumerate(items):
            r = ease((t - T[2] - 0.1 - k * 0.22) / 0.3)
            if r <= 0: continue
            cx = 190 + k * 210; col = RED if up else (120, 132, 160)
            d.ellipse((cx - 62, 900, cx + 62, 1024), fill=col + (int(255 * r),))
            ar = '▲' if up else '–'
            af = F(BLACK, 40); d.text((cx - d.textlength(ar, font=af) / 2, 912), ar, font=af, fill=WHITE + (int(255 * r),))
            vf = F(BLACK, 34); d.text((cx - d.textlength(v, font=vf) / 2, 960), v, font=vf, fill=WHITE + (int(255 * r),))
            mf = F(XB, 34); d.text((cx - d.textlength(m, font=mf) / 2, 1050), m, font=mf, fill=(225, 230, 240, int(255 * r)))
    foot(d, '출처: 한국은행 금통위(11/26) · 연합뉴스·파이낸셜뉴스 보도', 1180)
    return L


@scene('c9', 1, [('기준금리가 오르면 [o]은행 조달비용[/]이 오르고', '기준금리가 오르면 은행이 돈 구하는 비용이 오르고,'),
                 ('그게 [o]코픽스[/]로 이어져서', '그게 코픽스로 이어져서,'),
                 ('변동금리는 [r]재산정 때[/] 그대로 반영돼요', '변동금리는 재산정 때 그대로 반영돼요.')])
def s3(t, T):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    header(d, ('구조', '기준금리 오르면 내 대출은?'), ['이렇게 [o]번져요[/]'], chipcol=(70, 96, 150))
    steps = [('기준금리 ▲', '한국은행 결정', RED, 0), ('은행채·예금금리 ▲', '은행이 돈 구하는 비용', ORG, 0),
             ('코픽스 ▲', '변동금리의 기준 (10월 3.62%)', ORG, 1), ('내 주담대 금리 ▲', '변동형은 재산정 시점에 반영', RED, 2)]
    for k, (a, b, col, ci) in enumerate(steps):
        r = ease((t - (T[ci] + 0.15 + (k if ci == 0 else 0) * 0.5)) / 0.35)
        if r <= 0: continue
        y = 520 + k * 172
        B = Image.new('RGBA', (W, H)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((110, y, 900, y + 132), 28, fill=(255, 255, 255, 240))
        bd.rectangle((110, y + 26, 122, y + 114), fill=col)
        bd.text((150, y + 18), a, font=F(BLACK, 52), fill=NAVY); bd.text((152, y + 86), b, font=F(BOLD, 30), fill=(100, 110, 135))
        if k < 3:
            bd.polygon(((485, y + 138), (525, y + 138), (505, y + 164)), fill=(210, 218, 235))
        L.alpha_composite(with_alpha(B, r), (int(60 * (1 - r)), 0))
    d = ImageDraw.Draw(L)
    foot(d, '출처: 은행연합회 코픽스(11/16 공시)', 1250)
    return L


@scene('c3', -1, [('5월부터 10월까지 기준금리는 [o]0.5%p[/] 올랐는데', '오월부터 시월까지 기준금리는 영 점 오 퍼센트 포인트 올랐는데,'),
                  ('은행 주담대 평균은 [r]0.66%p[/] 올랐어요', '은행 주담대 평균은 영 점 육육 퍼센트 포인트 올랐어요.'),
                  ('인상 전에 [o]미리 반영[/]하거든요', '은행이 인상을 미리 반영하거든요.'),
                  ('[r]14년 7개월[/] 만에 최고치', '그래서 십사 년 칠 개월 만에 최고치예요.')])
def s4(t, T):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    header(d, ('팩트', '올해 5월 → 10월'), ['은행은 [r]더 많이[/] 올렸어요'], chipcol=(70, 96, 150))
    P, _ = panel(80, 505, 920, 1110); L.alpha_composite(P); d = ImageDraw.Draw(L)
    rows = [('기준금리', '2.50 → 3.00%', 0.50, BLUE, 0), ('주담대 평균', '4.32 → 4.98%', 0.66, RED, 1)]
    for k, (nm, rng, dv, col, ci) in enumerate(rows):
        y = 555 + k * 235; r = ease((t - T[ci] - 0.2) / 0.8)
        d.text((130, y), nm, font=F(BLACK, 50), fill=WHITE); d.text((130, y + 62), rng, font=F(XB, 34), fill=GRAY)
        bw = int(470 * dv / 0.66 * r)
        if bw > 0:
            d.rounded_rectangle((130, y + 120, 130 + bw, y + 190), 18, fill=col)
            s = f'+{dv * r:.2f}%p'; f = F(BLACK, 46)
            d.text((130 + bw + 16, y + 126), s, font=f, fill=col)
    if t > T[3]:
        q = ease((t - T[3]) / 0.3); s = '주담대 4.98% · 14년 7개월 만에 최고'; f = F(XB, 36); sw = d.textlength(s, font=f)
        d.rounded_rectangle((500 - sw / 2 - 26, 1020, 500 + sw / 2 + 26, 1084), 32, fill=RED + (int(255 * q),))
        d.text((500 - sw / 2, 1029), s, font=f, fill=WHITE + (int(255 * q),))
    foot(d, '출처: 한국은행 금융기관 가중평균금리(11/25 발표, 신규취급액)', 1150)
    return L


@scene('c8', 1, [('시중은행 변동금리 [r]상단 6.5%[/]', '시중은행 변동금리 상단은 이미 육 점 오 퍼센트.'),
                 ('오늘 인상분은 [o]이제부터[/] 반영돼요', '오늘 인상분은 이제부터 반영돼요.')])
def s5(t, T):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    header(d, ('11/17', '시중은행 6개월 변동형'), ['변동금리 [r]상단[/]'], chipcol=(70, 96, 150))
    f = F(BLACK, 210); s = '6.51%'
    d.text(((W - d.textlength(s, font=f)) / 2, 470), s, font=f, fill=RED, stroke_width=8, stroke_fill=(10, 16, 34))
    P, _ = panel(80, 790, 920, 1150); L.alpha_composite(P); d = ImageDraw.Draw(L)
    rows = [('NH농협', 4.51, 6.51), ('KB국민', 4.85, 6.25), ('우리', 5.04, 6.24)]
    for k, (nm, lo, hi) in enumerate(rows):
        r = ease((t - 0.4 - k * 0.25) / 0.5); y = 830 + k * 102
        d.text((120, y + 6), nm, font=F(XB, 40), fill=WHITE)
        x0 = 290 + (lo - 4.4) * 150; x1 = x0 + (hi - lo) * 150 * r
        d.rounded_rectangle((x0, y + 8, max(x0 + 20, x1), y + 58), 14, fill=(RED if k == 0 else BLUE))
        if r > 0.95:
            s2 = f'{lo:.2f}~{hi:.2f}%'; f2 = F(XB, 32)
            d.text((x1 + 14, y + 13), s2, font=f2, fill=WHITE)
    foot(d, '출처: 중도일보 11/18 (10월 코픽스 3.62% 반영, 11/17 적용)', 1180)
    return L


@scene('c12', -1, [('[o]3억[/] 빌렸다면 3%일 땐 [o]월 126만 원[/]', '삼억 빌렸다면, 삼 퍼센트일 땐 월 백이십육만 원.'),
                   ('7%면 [r]월 200만 원[/]', '칠 퍼센트면 월 이백만 원.'),
                   ('한 달 [r]73만 원[/], 1년이면 [r]877만 원[/] 더 내요', '한 달에 칠십삼만 원, 일 년이면 팔백칠십칠만 원 더 내요.')])
def s6(t, T):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    header(d, ('계산', '3억 · 30년 · 원리금균등'), ['내 이자, [r]얼마나[/] 늘었나'], chipcol=(70, 96, 150))
    bars = [('3%', 126.5, BLUE, 0), ('5%', 161.0, ORG, 0), ('7%', 199.6, RED, 1)]
    base = 1010
    for k, (lb, v, col, ci) in enumerate(bars):
        r = ease((t - T[ci] - (0.2 + k * 0.35 if ci == 0 else 0.1)) / 0.6)
        if k == 1: r = ease((t - T[0] - 0.9) / 0.6)
        if r <= 0: continue
        cx = 230 + k * 270; h = int(v * 2.15 * r)
        d.rounded_rectangle((cx - 85, base - h, cx + 85, base), 18, fill=col)
        s = f'월 {v * r:.0f}만'; f = F(BLACK, 46); d.text((cx - d.textlength(s, font=f) / 2, base - h - 62), s, font=f, fill=WHITE)
        lf = F(BLACK, 48); d.text((cx - d.textlength(lb, font=lf) / 2, base + 16), lb, font=lf, fill=col)
    if t > T[2]:
        q = ease((t - T[2]) / 0.3); s = '3% → 7%  월 +73만 · 연 +877만'; f = F(BLACK, 44); sw = d.textlength(s, font=f)
        d.rounded_rectangle((500 - sw / 2 - 30, 1112, 500 + sw / 2 + 30, 1188), 38, fill=RED + (int(255 * q),))
        d.text((500 - sw / 2, 1122), s, font=f, fill=WHITE + (int(255 * q),))
    foot(d, '※ 단순 계산 예시 · 0.25%p만 더 올라도 월 약 5만 원 (7% 기준)', 1215)
    return L


@scene('c11', 1, [('시장에선 내년에 [r]한 번 더[/] 올려서', '시장에선 내년에 한 번 더 올려서,'),
                  ('[r]3.5%[/]까지 갈 거란 관측이 많아요', '삼 점 오 퍼센트까지 갈 거란 관측이 많아요.')])
def s7(t, T):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    header(d, ('전망', '시장 관측'), ['그런데 [r]또 오른다[/]?'], chipcol=(70, 96, 150))
    P, _ = panel(80, 480, 920, 1130); L.alpha_composite(P); d = ImageDraw.Draw(L)
    pts = [('6월', 2.50), ('7월', 2.75), ('8월', 3.00), ('11월', 3.25), ('내년', 3.50)]
    X = lambda k: 170 + k * 175; Y = lambda v: 1000 - (v - 2.4) * 360
    r = ease((t - 0.3) / 1.4)
    for k, (m, v) in enumerate(pts):
        mf = F(XB, 32); d.text((X(k) - d.textlength(m, font=mf) / 2, 1050), m, font=mf, fill=GRAY)
    nseg = (len(pts) - 2) * r
    for k in range(len(pts) - 2):
        f = max(0.0, min(1.0, nseg - k))
        if f <= 0: break
        x0, y0, x1, y1 = X(k), Y(pts[k][1]), X(k + 1), Y(pts[k + 1][1])
        d.line((x0, y0, x0 + (x1 - x0) * f, y0 + (y1 - y0) * f), fill=ORG, width=10)
    for k in range(len(pts) - 1):
        if nseg >= k - 0.05:
            x, y = X(k), Y(pts[k][1]); d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=WHITE, outline=ORG, width=6)
            s = f'{pts[k][1]:.2f}'; vf = F(BLACK, 38); d.text((x - d.textlength(s, font=vf) / 2, y - 66), s, font=vf, fill=WHITE)
    if t > T[1]:
        q = ease((t - T[1]) / 0.5)
        x0, y0, x1, y1 = X(3), Y(3.25), X(4), Y(3.5)
        n = 8
        for j in range(n):
            a, b = j / n, (j + 0.5) / n
            if a > q: break
            b = min(b, q); d.line((x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b), fill=RED, width=10)
        if q > 0.9:
            d.ellipse((x1 - 18, y1 - 18, x1 + 18, y1 + 18), fill=RED)
            s = '3.50?'; vf = F(BLACK, 42); d.text((x1 - d.textlength(s, font=vf) / 2 - 10, y1 - 74), s, font=vf, fill=RED)
    foot(d, '출처: 뉴시스 11/26 (시장 관측) · 6월 이전 2.50%', 1170)
    return L


@scene('c5', 1, [('갈아타기 전에 [o]딱 3가지[/]만 보세요', '그럼 갈아타야 할까? 딱 세 가지만 보세요.'),
                 ('대출 [o]3년[/] 지나서 [o]중도상환수수료[/] 면제인지', '대출 삼 년 지나서 중도상환수수료가 면제인지,'),
                 ('고정·변동 차이 [o]거의 없으니[/] 고정으로 묶을지', '고정이랑 변동 차이가 거의 없으니, 고정으로 묶을지,'),
                 ('[r]다음 재산정 전[/]에 미리 비교하기', '그리고 다음 재산정 전에 미리 비교하는 거예요.')])
def s8(t, T):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    header(d, ('그럼', '갈아타야 할까?'), ['갈아타기 전 [o]3가지[/] 체크'], chipcol=GREEN)
    items = [('대출 3년 지났나?', '중도상환수수료 면제 여부'), ('고정 vs 변동 차이', '상단 기준 0.2%p 안팎 → 고정 검토'),
             ('다음 금리 재산정 언제?', '오르기 전에 미리 비교')]
    for k, (a, b) in enumerate(items):
        r = ease((t - T[k + 1] + 0.05) / 0.35)
        if r <= 0: continue
        y = 560 + k * 175
        B = Image.new('RGBA', (W, H)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((80, y, 920, y + 150), 28, fill=(255, 255, 255, 242))
        bd.ellipse((112, y + 39, 184, y + 111), fill=GREEN); bd.line((130, y + 76, 144, y + 91, 168, y + 60), fill=WHITE, width=10)
        bd.text((212, y + 22), a, font=F(BLACK, 50), fill=NAVY); bd.text((214, y + 90), b, font=F(BOLD, 32), fill=(100, 110, 135))
        L.alpha_composite(with_alpha(B, r), (int(60 * (1 - r)), 0))
    d = ImageDraw.Draw(L)
    foot(d, '※ 수수료·금리는 은행·상품·개인 조건마다 달라요 (고정·변동 상단차: 뉴스1 10월 말)', 1120, x=80)
    return L


@scene('c1', -1, CTA_IG if V == 'ig' else CTA_YT)
def s9(t, T):
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    if V == 'ig':
        header(d, ('팔로우', '+ 댓글'), ["댓글에 '[o]한도[/]'", '남기면 DM으로 보내드려요'], chipcol=ORG)
    else:
        header(d, ('구독', '+ 프로필 링크'), ['[o]채널 이름[/] 누르고', '프로필 링크 클릭'], chipcol=ORG)
    r = ease((t - 0.3) / 0.4)
    P, pd = panel(100, 620, 900, 1110, fill=(255, 255, 255, 245)); L.alpha_composite(with_alpha(P, r)); d = ImageDraw.Draw(L)
    a = int(255 * r)
    d.text((150, 660), 'LTV연구소에서 확인', font=F(XB, 38), fill=NAVY + (a,))
    for k, s in enumerate(['우리 아파트 최대 한도', '갈아타면 줄어드는 이자', '부족한 금액까지']):
        q = ease((t - 0.6 - k * 0.3) / 0.3)
        if q <= 0: continue
        y = 760 + k * 105; aa = int(255 * q)
        d.ellipse((150, y, 206, y + 56), fill=GREEN + (aa,)); d.line((164, y + 29, 176, y + 41, 194, y + 17), fill=WHITE + (aa,), width=8)
        d.text((232, y + 2), s, font=F(BLACK, 46), fill=NAVY + (aa,))
    return L


# ---------- TTS ----------
def tts_all():
    from supertonic import TTS as T_
    tts = T_(model='supertonic-2'); st = tts.get_voice_style('M1')
    meta = {}
    for i, (_, _, chunks, _) in enumerate(SC):
        for j, (_, say) in enumerate(chunks):
            wav, _d = tts.synthesize(say, voice_style=st, speed=1.3, lang='ko')
            a = np.asarray(wav, np.float32).reshape(-1)
            sr = getattr(tts, 'sample_rate', 44100)
            thr = 0.02 * np.abs(a).max(); idx = np.where(np.abs(a) > thr)[0]
            a = a[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)]
            np.save(f'{TTS}/{i + 1:02d}_{j}.npy', a); meta[f'{i + 1:02d}_{j}'] = len(a) / sr
    meta['sr'] = sr
    json.dump(meta, open(f'{TTS}/meta.json', 'w'), indent=1); print(meta)


GAP, PRE, POST = 0.12, 0.3, 0.45
def timing(i):
    meta = json.load(open(f'{TTS}/meta.json'))
    chunks = SC[i - 1][2]; T = []; t = PRE
    for j in range(len(chunks)):
        T.append(t); t += meta[f'{i:02d}_{j}'] + GAP
    return T, t - GAP + POST


def frame(i, t):
    bgname, dirn, chunks, fn = SC[i - 1]; T, dur = timing(i)
    fr = bg(bgname, t, dur, dirn)
    L = fn(t, T); d = ImageDraw.Draw(L); logo(d); handle(d)
    cur = max([j for j, s in enumerate(T) if t >= s - 0.05] or [0])
    subtitle(d, chunks[cur][0])
    fr.alpha_composite(with_alpha(L, 1 if i == 1 else ease(t / 0.22)))
    return fr.convert('RGB'), dur


def render_scene(i):
    _, dur = timing(i); n = int(round(dur * FPS))
    tmp = f'{OUT}/s{i:02d}.tmp.mp4'; out = f'{OUT}/s{i:02d}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    for k in range(n):
        im, _ = frame(i, k / FPS); p.stdin.write(im.tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)


def build():
    meta = json.load(open(f'{TTS}/meta.json')); sr = int(meta['sr'])
    OUTRO = os.path.abspath(f'{TOOLS}/../outro/outro_{V}.mp4')
    t0 = 0.0; starts = []; lst = []
    for i in range(1, len(SC) + 1):
        T, dur = timing(i); starts.append((i, t0, T)); lst.append(f"file '{OUT}/s{i:02d}.mp4'")
        # 실제 인코딩 길이 기준
        t0 += round(dur * FPS) / FPS
    main = t0; total = main + 8.0
    open(f'{OUT}/list.txt', 'w').write('\n'.join(lst + [f"file '{OUTRO}'"]))
    # 나레이션 트랙
    voice = np.zeros(int((total + 1) * sr), np.float32)
    for i, s0, T in starts:
        for j, tj in enumerate(T):
            a = np.load(f'{TTS}/{i:02d}_{j}.npy'); k = int((s0 + tj) * sr); voice[k:k + len(a)] += a[:len(voice) - k]
    voice = voice / (np.abs(voice).max() + 1e-9) * 0.92
    # BGM: noir — 드롭=2장면 시작, 리프트=8장면(갈아타기) 시작, 도장 sfx
    drop = starts[1][1]; lift = starts[7][1]
    sfx = [f'1:{starts[0][1] + starts[0][2][2]:.2f}', f'1:{starts[1][1] + starts[1][2][1]:.2f}', f'1:{starts[5][1] + starts[5][2][2]:.2f}']
    subprocess.run(['python3', f'{TOOLS}/bgm_noir.py', f'{OUT}/bgm.wav', f'{total:.2f}', f'{drop:.2f}', f'{lift:.2f}', '26', ','.join(sfx)], check=True)
    with wave.open(f'{OUT}/bgm.wav') as w:
        bsr = w.getframerate(); ch = w.getnchannels()
        b = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, ch) / 32768
    if bsr != sr:
        x = np.linspace(0, len(b) - 1, int(len(b) * sr / bsr)); b = np.stack([np.interp(x, np.arange(len(b)), b[:, c]) for c in range(ch)], 1)
    n = min(len(b), len(voice)); b = b[:n]; v = voice[:n]
    env = np.convolve(np.abs(v), np.ones(int(0.25 * sr)) / int(0.25 * sr), 'same'); env = env / (env.max() + 1e-9)
    duck = np.where(np.arange(n) / sr < main, 0.75 - 0.5 * np.clip(env * 4, 0, 1), 1.0)   # 엔딩은 BGM만
    b = b / (np.abs(b).max() + 1e-9) * 0.55
    mix = b * duck[:, None] + v[:, None]
    mix = mix[:int(total * sr)]; mix = mix / max(1.0, np.abs(mix).max() / 0.97)
    fade = int(1.2 * sr); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
    with wave.open(f'{OUT}/mix.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-an', '-vf', f'fps={FPS},scale={W}:{H},setsar=1',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', f'{OUT}/video.mp4'], check=True)
    final = f'{OUT}/final_{V}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/video.mp4', '-i', f'{OUT}/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final], check=True)
    print('built', final, round(total, 2), 'drop', round(drop, 2), 'lift', round(lift, 2))


if __name__ == '__main__':
    if CMD == 'tts': tts_all()
    elif CMD == 'snap':
        for i in (ONLY or range(1, len(SC) + 1)):
            T, dur = timing(i); im, _ = frame(i, dur - 0.1); im.save(f'{OUT}/snap{i:02d}.jpg', quality=88)
    elif CMD == 'render':
        for i in (ONLY or range(1, len(SC) + 1)): render_scene(i); print('scene', i, 'ok', flush=True)
    elif CMD == 'build': build()
