# v2: 훅(전체 카드) → 1~10번 하나씩 설명 → 전체 카드 다시(저장 유도) → 엔딩
# 사용: python3 make_check10_v2.py ig|yt [still]
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont

V = sys.argv[1]; STILL = len(sys.argv) > 2
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = '/home/claude/goosedaddyai-hub/ltvlab-media/_raw/2026-10-26_jeonse-ban'
OUTRO = f"/home/claude/goosedaddyai-hub/ltvlab-media/_common/outro/outro_{'yt' if V == 'yt' else 'ig'}.mp4"
W, H = 1080, 1920
NAVY = (20, 33, 61); YEL = (255, 201, 40); WHITE = (255, 255, 255); INK = (22, 30, 48); GRAY = (92, 104, 128)
SUB = (190, 202, 225); HL = (255, 236, 160); RED = (214, 52, 52)
BLACK = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
F = lambda p, s: ImageFont.truetype(p, s)
HANDLE = '@ltv_lab_kr' if V == 'yt' else '@ltv.lab'

# 카드 레이어(v1 스크립트가 만든 것) 준비
subprocess.run(['python3', f'{HERE}/make_check10.py', V, 'still'], check=True, capture_output=True)
card = Image.open(f'{HERE}/still_{V}.png').convert('RGB')

# (아이콘, 헤드라인, 사진, 예시카드[(글, 스타일)], 자막 2줄)
# 스타일: 'chip' 위 라벨 / 'big' 큰 강조 / 'mid' 보통 / 'small' 회색 작은 글
SC = [
 ('🏠', 'LTV부터 확인', 0, [('LTV = 집값 대비 대출 비율', 'chip'), ('시세 5억 × LTV 70%', 'mid'), ('= 최대 3.5억', 'big'), ('※ 이해를 돕기 위한 예시', 'small')],
  ['지역·규제지역·생애최초 여부에', '따라 비율이 달라져요']),
 ('🧮', 'DSR 먼저 계산', 1, [('DSR = 연소득 대비 원리금', 'chip'), ('연소득 5천 × 40%', 'mid'), ('= 1년 원리금 2천까지', 'big'), ('은행(1금융) 기준 40%', 'small')],
  ['LTV가 넉넉해도', 'DSR에 걸리면 거기까지예요']),
 ('📈', '변동금리면 한도↓', 2, [('스트레스 DSR', 'chip'), ('실제 금리 + 스트레스 금리', 'mid'), ('= 더 높은 금리로 심사', 'big'), ('변동 > 혼합 > 고정 순으로 많이 붙어요', 'small')],
  ['금리가 오를 걸 미리 가정해서', '변동금리일수록 한도가 줄어요']),
 ('🔒', '고정 vs 변동', 3, [('어떤 걸 고를까?', 'chip'), ('오래 갚을 계획 → 고정', 'mid'), ('몇 년 뒤 갈아탈 계획 → 변동', 'mid'), ('금리 전망보다 내 계획이 기준', 'small')],
  ['고정은 마음이 편하고', '변동은 갈아탈 때 유리해요']),
 ('📊', '상환방식 고르기', 1, [('같은 3억, 같은 금리라도', 'chip'), ('원리금균등: 매달 같은 금액', 'mid'), ('원금균등: 처음↑ 총이자↓', 'mid'), ('첫 부담이냐, 총이자냐의 선택', 'small')],
  ['초반 생활비가 빠듯하면 원리금균등', '이자를 아끼고 싶으면 원금균등']),
 ('⏱️', '중도상환수수료', 2, [('일찍 갚으면 내는 수수료', 'chip'), ('보통 대출 후 3년 이내', 'mid'), ('남은 기간만큼 줄어요', 'big'), ('요율·면제 조건은 상품마다 달라요', 'small')],
  ['곧 갈아타거나 갚을 계획이면', '수수료 조건부터 비교하세요']),
 ('🎁', '정책대출 자격 먼저', 4, [('조건 맞으면 금리가 확 낮아요', 'chip'), ('디딤돌 · 보금자리론', 'mid'), ('신생아 특례', 'big'), ('소득·집값·주택 수 조건 확인', 'small')],
  ['일반 대출 알아보기 전에', '정책대출 자격부터 체크']),
 ('🏦', '1금융 → 2금융 순서', 2, [('이 순서로 채우세요', 'chip'), ('① 은행에서 최대한', 'mid'), ('② 부족분만 보험·저축·캐피탈', 'mid'), ('2금융부터 쓰면 DSR을 먼저 잡아먹어요', 'small')],
  ['순서를 바꾸면', '한도·금리 둘 다 손해볼 수 있어요']),
 ('📅', '잔금일 역산 신청', 1, [('잔금일에서 거꾸로 계산', 'chip'), ('잔금일 − 3~4주', 'mid'), ('= 대출 신청일', 'big'), ('심사·감정·서류 보완에 시간이 걸려요', 'small')],
  ['잔금 직전에 알아보면', '늦을 수 있어요']),
 ('🔑', '전입·실거주 조건', 4, [('대출 받은 뒤 지켜야 할 것', 'chip'), ('규제지역·정책대출은', 'mid'), ('전입 의무 기한 확인', 'big'), ('안 지키면 대출 회수될 수 있어요', 'small')],
  ['계약 전에', '이사 일정부터 맞춰보세요']),
]
TOP, MID = 600, 560   # 위 띠 / 사진 영역(600~1160) / 아래 띠(1160~)


def emoji(ch, size):
    im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=F(EMO, 109), embedded_color=True, anchor='mm')
    im = im.crop(im.getbbox()); r = size / max(im.size)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def fit(d, text, path, size, maxw, minsize=20):
    while size > minsize:
        f = F(path, size)
        if d.textlength(text, font=f) <= maxw: return f
        size -= 1
    return F(path, minsize)


def scene_layers(i):
    ic, head, _, box, sub = SC[i]
    bands = Image.new('RGBA', (W, H), (0, 0, 0, 0)); b = ImageDraw.Draw(bands)
    b.rectangle((0, 0, W, TOP), fill=NAVY); b.rectangle((0, TOP + MID, W, H), fill=NAVY)
    b.rectangle((0, TOP - 6, W, TOP), fill=YEL)
    # 사진 위 살짝 어둡게(예시 카드 잘 보이게)
    b.rectangle((0, TOP, W, TOP + MID), fill=(10, 16, 32, 70))
    txt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); t = ImageDraw.Draw(txt)
    # 진행 점 10개 (상단 UI 아래)
    for k in range(10):
        x = 60 + k * 42
        t.rounded_rectangle((x, 250, x + 30, 262), 6, fill=YEL if k <= i else (70, 86, 120))
    # 체크 번호 + 헤드라인
    lab = f'체크 {i + 1}'; lf = F(BLACK, 40); lw = t.textlength(lab, font=lf)
    t.rounded_rectangle((60, 300, 60 + lw + 48, 362), 31, fill=YEL)
    t.text((84, 304), lab, font=lf, fill=NAVY)
    em = emoji(ic, 60); txt.alpha_composite(em, (60 + int(lw) + 70, 301))
    hf = fit(t, head, BLACK, 100, W - 140)
    t.text((60, 392), head, font=hf, fill=WHITE)
    # 예시 카드: 사진 영역 가운데 (x 60~880)
    rows = []
    for s, st in box:
        f = {'chip': F(BOLD, 32), 'big': fit(t, s, BLACK, 58, 740), 'mid': fit(t, s, BLACK, 44, 740), 'small': fit(t, s, BOLD, 28, 740)}[st]
        rows.append((s, st, f, {'chip': 70, 'big': 84, 'mid': 66, 'small': 50}[st]))
    ch = sum(r[3] for r in rows) + 40
    cx0, cx1 = 60, 880; cy0 = TOP + (MID - ch) // 2; cy1 = cy0 + ch
    t.rounded_rectangle((cx0, cy0, cx1, cy1), 30, fill=(255, 255, 255, 246))
    y = cy0 + 22
    for s, st, f, h in rows:
        tw = t.textlength(s, font=f); x = (cx0 + cx1) / 2 - tw / 2
        if st == 'chip':
            t.rounded_rectangle((x - 22, y, x + tw + 22, y + 50), 25, fill=NAVY); t.text((x, y + 3), s, font=f, fill=YEL)
        elif st == 'big':
            t.rectangle((x - 6, y + 40, x + tw + 6, y + 72), fill=HL); t.text((x, y), s, font=f, fill=RED)
        elif st == 'mid':
            t.text((x, y + 4), s, font=f, fill=INK)
        else:
            t.text((x, y + 8), s, font=f, fill=GRAY)
        y += h
    # 핸들(사진 왼쪽 위)
    f = F(BOLD, 28); hw = t.textlength(HANDLE, font=f)
    t.rounded_rectangle((40, TOP + 18, 40 + hw + 36, TOP + 64), 23, fill=(20, 33, 61, 200)); t.text((58, TOP + 23), HANDLE, font=f, fill=WHITE)
    # 자막: 아래 띠, x 60~880 가운데
    y = TOP + MID + 64
    for k, s in enumerate(sub):
        f = fit(t, s, BOLD, 58, 800)
        tw = t.textlength(s, font=f); t.text((470 - tw / 2, y), s, font=f, fill=WHITE if k == 0 else YEL); y += f.size + 30
    assert y < 1600, y
    return bands, txt


def enc(cmd, out):
    tmp = out[:-4] + '.tmp.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *cmd, '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], check=True)
    os.replace(tmp, out)


DUR = 3.0
if STILL:
    for i in (0, 4, 7):
        bands, txt = scene_layers(i)
        ph = Image.open(f'{RAW}/img{SC[i][2]}.png').convert('RGB')
        r = W / ph.width; ph = ph.resize((W, int(ph.height * r)))
        if ph.height < MID: ph = ph.resize((int(ph.width * MID / ph.height), MID))
        base = Image.new('RGBA', (W, H), NAVY); y0 = (ph.height - MID) // 2
        base.paste(ph.crop((0, y0, W, y0 + MID)), (0, TOP))
        base.alpha_composite(bands); base.alpha_composite(txt); base.convert('RGB').save(f'{HERE}/v2_s{i}_{V}.png')
    sys.exit()

clips = []
# 1) 훅: 전체 카드 2.5초 (v1 애니메이션 앞부분 재사용 대신 완성 카드 + 아주 느린 줌)
card.save(f'{HERE}/card_{V}.png')
out = f'{HERE}/k_hook_{V}.mp4'
enc(['-framerate', '30', '-i', f'{HERE}/card_{V}.png', '-vf', "loop=-1:1,trim=duration=2.5,setsar=1"], out); clips.append(out)
# 2) 1~10 설명
for i in range(10):
    bands, txt = scene_layers(i)
    bands.save(f'{HERE}/sb{i}_{V}.png'); txt.save(f'{HERE}/st{i}_{V}.png')
    fr = int(DUR * 30)
    zx = 'iw/2-(iw/zoom/2)' if i % 2 == 0 else 'iw/2-(iw/zoom/2)+on*0.4'
    vf = (f"scale=1980:-1,crop=1980:1026,zoompan=z='1+0.06*on/{fr}':x='{zx}':y='ih/2-(ih/zoom/2)':d={fr}:s=1080x{MID}:fps=30,"
          f"pad=1080:1920:0:{TOP}:color=0x14213d")
    out = f'{HERE}/k{i}_{V}.mp4'
    enc(['-i', f'{RAW}/img{SC[i][2]}.png', '-loop', '1', '-framerate', '30', '-t', str(DUR), '-i', f'{HERE}/sb{i}_{V}.png',
         '-loop', '1', '-framerate', '30', '-t', str(DUR), '-i', f'{HERE}/st{i}_{V}.png',
         '-filter_complex', f"[0:v]{vf}[p];[p][1:v]overlay[q];[2:v]format=rgba,fade=t=in:st=0:d=0.25:alpha=1[tt];[q][tt]overlay,setsar=1[v]",
         '-map', '[v]', '-t', str(DUR)], out)
    clips.append(out)
# 3) 마무리: 전체 카드 + "저장" 스티커 3초
end = card.copy().convert('RGBA'); d = ImageDraw.Draw(end)
msg = '💾 저장해두고 계약 전에 꺼내보세요'
f = F(BLACK, 44); tw = d.textlength(msg[2:], font=f)
d.rounded_rectangle((36, 1470, 884, 1586), 26, fill=RED, outline=YEL, width=3)
bx0 = 460 - (tw + 66) / 2
end.alpha_composite(emoji('💾', 52), (int(bx0), 1502)); d.text((bx0 + 66, 1496), msg[2:], font=f, fill=WHITE)
end.convert('RGB').save(f'{HERE}/card_end_{V}.png')
out = f'{HERE}/k_end_{V}.mp4'
enc(['-framerate', '30', '-i', f'{HERE}/card_end_{V}.png', '-vf', "loop=-1:1,trim=duration=3,setsar=1"], out); clips.append(out)
# 엔딩
out = f'{HERE}/k_outro_{V}.mp4'
enc(['-i', OUTRO, '-vf', 'scale=1080:1920,fps=30,setsar=1', '-an'], out); clips.append(out)

lst = f'{HERE}/list2_{V}.txt'
with open(lst, 'w') as fh:
    for c in clips: fh.write(f"file '{c}'\n")
tmp = f'{HERE}/v2video_{V}.tmp.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', tmp], check=True)
os.replace(tmp, f'{HERE}/v2video_{V}.mp4')
total = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{HERE}/v2video_{V}.mp4'],
                             capture_output=True, text=True).stdout)
name = ('reel_insta' if V == 'ig' else 'shorts_youtube') + '_v2'
tmp = f'{HERE}/{name}.tmp.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{HERE}/v2video_{V}.mp4', '-i', f'{HERE}/bgm2_norm.wav',
                '-filter_complex', f"[1:a]atrim=0:{total},afade=t=out:st={total - 2}:d=2[a]", '-map', '0:v', '-map', '[a]',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', tmp], check=True)
os.replace(tmp, f'{HERE}/{name}.mp4')
print(V, 'done', total)
