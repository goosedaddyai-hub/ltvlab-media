# 레퍼런스식 릴스: 위 네이비 띠(헤드라인) + 가운데 실사 사진(천천히 줌) + 아래 네이비 띠(자막)
# 사용: python3 make_reel.py <ig|yt>
import sys, os, subprocess, json
from PIL import Image, ImageDraw, ImageFont

V = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = '/home/claude/ltvlab-media/_raw/2026-10-26_jeonse-ban'
W, H = 1080, 1920
TOP, MID = 600, 660           # 위 띠 높이, 사진 높이 → 아래 띠는 1260부터
NAVY = (20, 33, 61); YEL = (255, 201, 40); WHITE = (255, 255, 255); SUB = (190, 202, 225)
BLACK = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
F = lambda p, s: ImageFont.truetype(p, s)
HANDLE = '@ltv_lab_kr' if V == 'yt' else '@ltv.lab'

# (사진, 헤드라인 줄들[(글, 강조)], 자막 줄들, 길이초, 출처)
S = [
 (0, [('내년 1월부터', 0), ('전세대출 막힙니다', 1)], 'TABLE', 5.0, '출처: 금융위원회 8·13 부동산 대책 (2026.8.13)'),
 (0, [('대상은 딱 이런 분', 0)], ['수도권·규제지역 아파트 1채 보유', '본인·배우자 모두 안 살아봤다면'], 4.0, ''),
 (1, [('2027년 1월 1일부터', 0), ('신규·연장 원칙적 금지', 1)], ['HF·HUG 전세보증에서 빠져', '은행 전세대출이 사실상 막혀요'], 4.0, '출처: 금융위원회 8·13 부동산 대책'),
 (2, [('영향권 최대', 0), ('6만건 · 9.3조원', 1)], ['실제 대상은 거주 이력이', '없는 분으로 좁혀져요'], 3.5, '수도권·규제지역 1주택자 전세대출 기준'),
 (4, [('한 번이라도 살았다면?', 1)], ['본인·배우자 실거주 이력 있으면 제외', '부모·자녀에게 세 준 집도 제외'], 4.0, ''),
 (1, [('1주택자 보증도 줄어요', 0)], ['수도권·규제지역  80% → 70%', '그 외 지역  90% → 80%'], 3.5, '전세대출 보증비율 · 무주택자는 그대로'),
 (3, [('그럼 방법은?', 1)], ['세입자 내보내고 내 집 입주', '퇴거자금 한도부터 확인하세요'], 3.5, ''),
]
if V == 'ig':
    S.append((3, [('우리 아파트 퇴거자금 한도', 0), ('궁금하면?', 1)], ["댓글에 '한도' 남겨주세요", 'DM으로 바로 보내드려요'], 3.5, ''))
elif V == 'fb':
    S.append((3, [('우리 아파트 퇴거자금 한도', 0), ('궁금하면?', 1)], ['프로필 링크에서', '1분이면 바로 확인돼요'], 3.5, ''))
else:
    S.append((3, [('우리 아파트 퇴거자금 한도', 0), ('궁금하면?', 1)], ['채널 이름 누르고 프로필 링크', '1분이면 바로 확인돼요'], 3.5, ''))


def fit(d, text, path, size, maxw):
    while size > 30:
        f = F(path, size)
        if d.textlength(text, font=f) <= maxw: return f
        size -= 2
    return F(path, size)


def frames(i, sc):
    _, head, sub, dur, src = sc
    bands = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(bands)
    d.rectangle((0, 0, W, TOP), fill=NAVY); d.rectangle((0, TOP + MID, W, H), fill=NAVY)
    # 위 띠 아래 얇은 포인트선
    d.rectangle((0, TOP - 6, W, TOP), fill=YEL)
    txt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); t = ImageDraw.Draw(txt)
    # 헤드라인: 위 띠 아랫부분(인스타 상단 UI 피해서 y 230~560)
    sizes = [F(BLACK, 88) for _ in head]
    fs = [fit(t, s, BLACK, 92, W - 120) for s, _ in head]
    lh = [f.size + 22 for f in fs]
    y = TOP - 60 - sum(lh)
    for (s, em), f, h in zip(head, fs, lh):
        tw = t.textlength(s, font=f)
        t.text(((W - tw) / 2, y), s, font=f, fill=YEL if em else WHITE)
        y += h
    if sub == 'TABLE':
        rows = [('시행', ['2027년 1월 1일부터']),
                ('대상', ['수도권·규제지역 아파트 1채 보유', '+ 본인·배우자 거주 이력 없음']),
                ('내용', ['HF·HUG 전세보증 제외', '신규·연장 원칙적 금지']),
                ('예외', ['한 번이라도 살았던 집', '부모·자녀에게 세 준 집']),
                ('보증비율', ['1주택자 10%p ↓', '수도권·규제 80→70% · 그 외 90→80%']),
                ('영향권', ['최대 6만건 · 9.3조원'])]
        x0, x1, y0 = 40, 900, TOP + 24
        rh = [96 if len(v) == 1 else 132 for _, v in rows]
        y1 = y0 + sum(rh) + 20
        t.rounded_rectangle((x0, y0, x1, y1), 28, fill=(255, 255, 255, 245))
        ttl = F(BOLD, 30); tw = t.textlength('한눈에 정리', font=ttl)
        t.rounded_rectangle((x0 + 24, y0 - 26, x0 + 24 + tw + 40, y0 + 22), 24, fill=YEL)
        t.text((x0 + 44, y0 - 22), '한눈에 정리', font=ttl, fill=NAVY)
        y = y0 + 20; lab = F(BLACK, 36)
        for k, ((lb, vals), h) in enumerate(zip(rows, rh)):
            if k: t.line((x0 + 24, y, x1 - 24, y), fill=(210, 216, 228, 255), width=2)
            t.rounded_rectangle((x0 + 24, y + 18, x0 + 214, y + h - 18), 16, fill=NAVY)
            lw = t.textlength(lb, font=lab)
            t.text((x0 + 119 - lw / 2, y + h / 2 - 26), lb, font=lab, fill=YEL)
            vy = y + (h - len(vals) * 50) / 2 - 4
            for j, v in enumerate(vals):
                f = fit(t, v, BOLD if j == 0 else BOLD, 38, x1 - x0 - 270)
                t.text((x0 + 240, vy), v, font=f, fill=NAVY if j == 0 else (60, 75, 105))
                vy += 50
            y += h
        if src:
            f = F(BOLD, 26); tw = t.textlength(src, font=f)
            t.text((470 - tw / 2, y1 + 22), src, font=f, fill=SUB)
        bands.save(f'{HERE}/b{i}.png'); txt.save(f'{HERE}/t{i}.png')
        return
    # 자막: 아래 띠, 오른쪽 버튼 영역(x>900) 피해서 x 60~880 가운데 정렬
    cx = 470; maxw = 820; y = TOP + MID + 60
    for k, s in enumerate(sub):
        f = fit(t, s, BOLD, 56, maxw)
        tw = t.textlength(s, font=f)
        t.text((cx - tw / 2, y), s, font=f, fill=WHITE if k == 0 else YEL)
        y += f.size + 26
    if src:
        f = F(BOLD, 26); tw = t.textlength(src, font=f)
        t.text((cx - tw / 2, y + 8), src, font=f, fill=SUB)
    # 사진 위 왼쪽 위 핸들 라벨
    f = F(BOLD, 28); tw = t.textlength(HANDLE, font=f)
    t.rounded_rectangle((40, TOP + 24, 40 + tw + 36, TOP + 72), 24, fill=(20, 33, 61, 190))
    t.text((58, TOP + 30), HANDLE, font=f, fill=WHITE)
    bands.save(f'{HERE}/b{i}.png'); txt.save(f'{HERE}/t{i}.png')


clips = []
for i, sc in enumerate(S):
    frames(i, sc)
    img, dur = sc[0], sc[3]
    fr = int(dur * 30)
    # 사진: 1080x660 영역에 꽉 채우고 천천히 줌(장면마다 방향 바꿈)
    zx = 'iw/2-(iw/zoom/2)' if i % 2 == 0 else 'iw/2-(iw/zoom/2)+on*0.4'
    vf = (f"scale=1980:-1,crop=1980:1210,zoompan=z='1+0.07*on/{fr}':x='{zx}':y='ih/2-(ih/zoom/2)':d={fr}:s=1080x660:fps=30,"
          f"pad=1080:1920:0:{TOP}:color=0x14213d")
    out = f'{HERE}/c{i}.mp4'
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', f'{IMG}/img{img}.png', '-loop', '1', '-t', str(dur), '-i', f'{HERE}/b{i}.png',
           '-loop', '1', '-t', str(dur), '-i', f'{HERE}/t{i}.png',
           '-filter_complex', f"[0:v]{vf}[p];[p][1:v]overlay[q];[2:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1[tt];[q][tt]overlay,format=yuv420p,setsar=1[v]",
           '-map', '[v]', '-t', str(dur), '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', out]
    subprocess.run(cmd, check=True); clips.append(out)

outro = f"/home/claude/ltvlab-media/_common/outro/outro_{'yt' if V == 'yt' else 'ig'}.mp4"
lst = f'{HERE}/list_{V}.txt'
with open(lst, 'w') as fh:
    for c in clips: fh.write(f"file '{c}'\n")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', outro, '-filter_complex',
                '[1:v]scale=1080:1920,fps=30,format=yuv420p,setsar=1[o];[0:v][o]concat=n=2:v=1:a=0[v]', '-map', '[v]',
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', f'{HERE}/video_{V}.mp4'], check=True)
total = sum(s[3] for s in S) + 8
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{HERE}/video_{V}.mp4', '-i', f'{HERE}/bgm_norm.wav',
                '-filter_complex', f"[1:a]atrim=0:{total},afade=t=out:st={total-1.5}:d=1.5[a]", '-map', '0:v', '-map', '[a]',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', f'{HERE}/reel_{V}.mp4'], check=True)
print(V, 'done', total)
