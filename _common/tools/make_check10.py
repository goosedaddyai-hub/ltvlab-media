# 저장각 체크리스트 카드 릴스 — "집 사기 전 대출 체크리스트 10"
# 사용: python3 make_check10.py ig|yt   (frames 만: python3 make_check10.py ig still)
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

V = sys.argv[1]; STILL = len(sys.argv) > 2
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = '/home/claude/goosedaddyai-hub/ltvlab-media/_raw/2026-10-26_jeonse-ban'
OUTRO = f"/home/claude/goosedaddyai-hub/ltvlab-media/_common/outro/outro_{'yt' if V == 'yt' else 'ig'}.mp4"
W, H = 1080, 1920
NAVY = (20, 33, 61); YEL = (255, 201, 40); WHITE = (255, 255, 255); INK = (22, 30, 48); GRAY = (92, 104, 128)
HL = (255, 236, 160); RED = (214, 52, 52)
BLACK = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
MED = '/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc'
EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
F = lambda p, s: ImageFont.truetype(p, s)
HANDLE = '@ltv_lab_kr' if V == 'yt' else '@ltv.lab'

# (아이콘, 제목, [(설명, 강조여부)...])  — 설명은 한 줄, 강조 부분은 노란 형광
ITEMS = [
    ('🏠', 'LTV부터 확인', [('시세 × LTV, ', 0), ('지역마다 달라요', 1)]),
    ('🧮', 'DSR 먼저 계산', [('연소득 대비 원리금 = ', 0), ('진짜 한도', 1)]),
    ('📈', '변동금리면 한도↓', [('스트레스 DSR ', 1), ('가산 적용', 0)]),
    ('🔒', '고정 vs 변동', [('갈아탈 계획 ', 0), ('있으면 변동도 OK', 1)]),
    ('📊', '상환방식 고르기', [('원리금균등 ', 1), ('vs 원금균등', 0)]),
    ('⏱️', '중도상환수수료', [('3년 내 상환 ', 0), ('예정이면 필수', 1)]),
    ('🎁', '정책대출 자격 먼저', [('디딤돌·보금자리·', 0), ('신생아특례', 1)]),
    ('🏦', '1금융 → 2금융 순서', [('부족분은 ', 0), ('보험·저축·캐피탈', 1)]),
    ('📅', '잔금일 역산 신청', [('잔금 ', 0), ('3~4주 전', 1), (' 신청', 0)]),
    ('🔑', '전입·실거주 조건', [('전입 의무 기간 ', 1), ('꼭 확인', 0)]),
]


def emoji(ch, size):
    f = F(EMO, 109); im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor='mm')
    im = im.crop(im.getbbox()); r = size / max(im.size)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def fit(d, text, path, size, maxw, minsize=20):
    while size > minsize:
        f = F(path, size)
        if d.textlength(text, font=f) <= maxw: return f
        size -= 1
    return F(path, minsize)


def cover(img, w, h):
    r = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.LANCZOS)
    x = (im.width - w) // 2; y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


# ---------- 레이어 1: 배경(사진 + 네이비) ----------
HEAD_Y0, HEAD_Y1 = 0, 640           # 헤더 영역(사진)
GRID_Y0 = 590                       # 체크리스트 패널 시작
bg = Image.new('RGB', (W, H), NAVY)
photo = cover(Image.open(f'{RAW}/img2.png').convert('RGB'), W, HEAD_Y1)
# 사진 왼쪽은 글씨 자리라 네이비로 그라데이션
grad = Image.new('L', (W, HEAD_Y1))
gd = ImageDraw.Draw(grad)
for x in range(W):
    a = int(255 * max(0, min(1, (x - 360) / 520)))
    gd.line((x, 0, x, HEAD_Y1), fill=a)
navy_l = Image.new('RGB', (W, HEAD_Y1), NAVY)
head = Image.composite(photo, navy_l, grad)
# 아래로 갈수록 네이비로
vg = Image.new('L', (W, HEAD_Y1)); vd = ImageDraw.Draw(vg)
for y in range(HEAD_Y1):
    vd.line((0, y, W, y), fill=int(255 * min(1, max(0, (HEAD_Y1 - 40 - y) / 260))))
head = Image.composite(head, navy_l, vg)
bg.paste(head, (0, 0))
bg.save(f'{HERE}/bg_{V}.png')

# ---------- 레이어 2: 헤더 글씨 ----------
hd = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(hd)
# 인스타 상단 UI(~220px) 아래부터
pill = 'LTV연구소가 정리한'; pf = F(BOLD, 34); pw = d.textlength(pill, font=pf)
d.rounded_rectangle((60, 236, 60 + pw + 48, 292), 28, fill=RED)
d.text((84, 240), pill, font=pf, fill=WHITE)
d.text((58, 302), '집 사기 전', font=F(BLACK, 92), fill=WHITE)
d.text((58, 410), '대출 체크 10', font=F(BLACK, 104), fill=YEL)
d.text((62, 534), '계약서 사인 전에 이것만 확인하세요', font=F(BOLD, 36), fill=(214, 224, 242))
# 핸들 라벨(사진 오른쪽 위, 상단 UI 아래)
hf = F(BOLD, 28); hw = d.textlength(HANDLE, font=hf)
d.rounded_rectangle((W - 60 - hw - 36, 244, W - 60, 292), 24, fill=(20, 33, 61, 200))
d.text((W - 60 - hw - 18, 250), HANDLE, font=hf, fill=WHITE)
hd.save(f'{HERE}/head_{V}.png')

# ---------- 레이어 3~: 패널 + 항목(하나씩 등장) ----------
PX0, PX1 = 36, 884                  # 오른쪽 버튼 영역(x>900) 피함
PY0 = GRID_Y0 + 24
panel = Image.new('RGBA', (W, H), (0, 0, 0, 0)); p = ImageDraw.Draw(panel)
# 타이틀 띠
ttl = '꼭 저장해두세요 · 핵심 체크리스트'
tf = F(BLACK, 38); tw = p.textlength(ttl, font=tf)
COLW = (PX1 - PX0 - 36) // 2        # 칸 너비
ROW_H = 146; GRID_TOP = PY0 + 84
PY1 = GRID_TOP + ROW_H * 5 + 16
p.rounded_rectangle((PX0, PY0, PX1, PY1), 30, fill=(255, 255, 255, 250))
p.rounded_rectangle((PX0, PY0, PX1, PY0 + 74), 30, fill=YEL)
p.rectangle((PX0, PY0 + 44, PX1, PY0 + 74), fill=YEL)
p.text(((PX0 + PX1) / 2 - tw / 2, PY0 + 10), ttl, font=tf, fill=NAVY)
# 칸 구분선
for r in range(1, 5):
    y = GRID_TOP + r * ROW_H
    p.line((PX0 + 24, y, PX1 - 24, y), fill=(226, 230, 238, 255), width=2)
p.line(((PX0 + PX1) / 2, GRID_TOP + 10, (PX0 + PX1) / 2, PY1 - 22), fill=(226, 230, 238, 255), width=2)
# 아래 한 줄 메시지
BY0 = PY1 + 26
p.rounded_rectangle((PX0, BY0, PX1, BY0 + 116), 26, fill=(11, 20, 40, 255), outline=YEL, width=3)
bulb = emoji('💡', 60); panel.alpha_composite(bulb, (PX0 + 28, BY0 + 28))
m1 = '같은 집·같은 소득이어도'; m2a = "대출 받는 '순서'"; m2b = '에 따라 한도가 달라져요'
p.text((PX0 + 110, BY0 + 10), m1, font=F(BOLD, 36), fill=WHITE)
f2 = F(BLACK, 40); x = PX0 + 110
p.text((x, BY0 + 56), m2a, font=f2, fill=YEL); x += p.textlength(m2a, font=f2)
p.text((x, BY0 + 56), m2b, font=fit(p, m2b, BOLD, 38, PX1 - 24 - x), fill=WHITE)
panel.save(f'{HERE}/panel_{V}.png')
assert BY0 + 116 <= 1620, BY0  # 하단 캡션 영역 위에서 끝나야 함
print('panel bottom', BY0 + 116)

for i, (ic, title, desc) in enumerate(ITEMS):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); q = ImageDraw.Draw(lay)
    col, row = i // 5, i % 5          # 왼쪽 1~5, 오른쪽 6~10
    x0 = PX0 + 18 + col * (COLW + 36 - 18); y0 = GRID_TOP + row * ROW_H
    # 번호 배지
    q.rounded_rectangle((x0 + 4, y0 + 20, x0 + 58, y0 + 74), 14, fill=NAVY)
    nf = F(BLACK, 34); ns = str(i + 1); nw = q.textlength(ns, font=nf)
    q.text((x0 + 31 - nw / 2, y0 + 24), ns, font=nf, fill=YEL)
    # 아이콘
    em = emoji(ic, 44); lay.alpha_composite(em, (x0 + 10 + (44 - em.width) // 2, y0 + 86))
    tx = x0 + 74; maxw = COLW - 74 - 8
    q.text((tx, y0 + 16), title, font=fit(q, title, BLACK, 36, maxw), fill=INK)
    # 설명(강조 부분 형광펜)
    full = ''.join(s for s, _ in desc); df = fit(q, full, BOLD, 27, maxw)
    x = tx; y = y0 + 76
    for s, em_ in desc:
        w = q.textlength(s, font=df)
        if em_:
            q.rectangle((x - 2, y + 14, x + w + 2, y + df.size + 8), fill=HL)
        q.text((x, y), s, font=df, fill=RED if em_ else GRAY)
        x += w
    lay.save(f'{HERE}/it{i}_{V}.png')

if STILL:
    im = Image.open(f'{HERE}/bg_{V}.png').convert('RGBA')
    for n in [f'head_{V}', f'panel_{V}'] + [f'it{i}_{V}' for i in range(10)]:
        im.alpha_composite(Image.open(f'{HERE}/{n}.png'))
    im.convert('RGB').save(f'{HERE}/still_{V}.png'); sys.exit()

# ---------- 렌더: 사진 천천히 줌 + 패널 0.5s 등장 + 항목 0.22s 간격 팝 ----------
MAIN = 11.0; fr = int(MAIN * 30)
inputs = ['-loop', '1', '-framerate', '30', '-t', str(MAIN), '-i', f'{HERE}/bg_{V}.png']
for n in [f'head_{V}', f'panel_{V}'] + [f'it{i}_{V}' for i in range(10)]:
    inputs += ['-loop', '1', '-framerate', '30', '-t', str(MAIN), '-i', f'{HERE}/{n}.png']
fc = [f"[0:v]crop=1080:640:0:0,scale=1180:-1,zoompan=z='1+0.06*on/{fr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x698:fps=30,crop=1080:640:0:0[ph]",
      "[0:v]setsar=1[base]", "[base][ph]overlay=0:0[b0]",
      "[1:v]format=rgba[h]", "[b0][h]overlay[b1]",
      "[2:v]format=rgba,fade=t=in:st=0.35:d=0.35:alpha=1[pn]", "[b1][pn]overlay[b2]"]
last = 'b2'
for i in range(10):
    st = 0.75 + i * 0.22
    fc.append(f"[{3 + i}:v]format=rgba,fade=t=in:st={st:.2f}:d=0.2:alpha=1[i{i}]")
    fc.append(f"[{last}][i{i}]overlay[c{i}]"); last = f'c{i}'
fc.append(f"[{last}]format=yuv420p,setsar=1[v]")
tmp = f'{HERE}/main_{V}.tmp.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(fc), '-map', '[v]', '-t', str(MAIN),
                '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', tmp], check=True)
os.replace(tmp, f'{HERE}/main_{V}.mp4')
# 본편 + 엔딩(8초) 이어붙이고, BGM 하나를 끝까지 깔아 엔딩에서도 음악이 안 바뀌게
total = MAIN + 8
tmp = f'{HERE}/video_{V}.tmp.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{HERE}/main_{V}.mp4', '-i', OUTRO, '-filter_complex',
                '[1:v]scale=1080:1920,fps=30,format=yuv420p,setsar=1[o];[0:v][o]concat=n=2:v=1:a=0[v]', '-map', '[v]',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', tmp], check=True)
os.replace(tmp, f'{HERE}/video_{V}.mp4')
name = 'reel_insta' if V == 'ig' else 'shorts_youtube'
tmp = f'{HERE}/{name}.tmp.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{HERE}/video_{V}.mp4', '-i', f'{HERE}/bgm_norm.wav',
                '-filter_complex', f"[1:a]atrim=0:{total},afade=t=out:st={total - 1.8}:d=1.8[a]", '-map', '0:v', '-map', '[a]',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', tmp], check=True)
os.replace(tmp, f'{HERE}/{name}.mp4')
print(V, 'done', total)
