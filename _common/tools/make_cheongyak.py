# 릴스: 11~12월 청약 총정리 (2026-11-07)
# 사용: python3 make_cheongyak.py ig|yt [snap]   (snap = 장면별 대표 프레임만 저장)
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont

V = sys.argv[1]; SNAP = 'snap' in sys.argv[2:]
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
IMG = f'{ROOT}/_raw/2026-10-26_jeonse-ban'
OUTRO = f"{ROOT}/_common/outro/outro_{'yt' if V == 'yt' else 'ig'}.mp4"
OUT = f'/home/claude/cy/out_{V}'; os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
TOP, MID = 600, 660
NAVY = (20, 33, 61); NAVY2 = (31, 49, 89); YEL = (255, 201, 40); WHITE = (255, 255, 255)
SUB = (190, 202, 225); RED = (232, 65, 58); CORAL = (255, 122, 89); GREEN = (46, 196, 125); INK = (22, 30, 48); GRAY = (98, 110, 135)
FD = f'{ROOT}/_common/fonts'
BLACK, XB, BOLD = f'{FD}/Pretendard-Black.otf', f'{FD}/Pretendard-ExtraBold.otf', f'{FD}/Pretendard-Bold.otf'
_fc = {}
def F(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]
HANDLE = '@ltv_lab_kr' if V == 'yt' else '@ltv.lab'
ease = lambda x: 1 - (1 - max(0, min(1, x))) ** 3


def fit(d, text, path, size, maxw):
    while size > 24 and d.textlength(text, font=F(path, size)) > maxw: size -= 2
    return F(path, size)


def alpha(L, a):
    if a >= 1: return L
    r, g, b, al = L.split(); return Image.merge('RGBA', (r, g, b, al.point(lambda v: int(v * a))))


def text_layer(head, sub, src='', chip=None, chipcol=YEL, handle=True):
    L = Image.new('RGBA', (W, H)); t = ImageDraw.Draw(L)
    t.rectangle((0, TOP - 6, W, TOP), fill=YEL)
    fs = [fit(t, s, BLACK, 96, W - 120) for s, _ in head]; lh = [f.size + 24 for f in fs]
    y = TOP - 58 - sum(lh)
    if chip:
        cf = F(BLACK, 40); cw = t.textlength(chip, font=cf)
        t.rounded_rectangle(((W - cw) / 2 - 28, y - 88, (W + cw) / 2 + 28, y - 24), 32, fill=chipcol)
        t.text(((W - cw) / 2, y - 81), chip, font=cf, fill=NAVY)
    for (s, em), f, h in zip(head, fs, lh):
        tw = t.textlength(s, font=f); t.text(((W - tw) / 2, y), s, font=f, fill=YEL if em else WHITE); y += h
    cx = 470; y = TOP + MID + 58
    for k, s in enumerate(sub):
        f = fit(t, s, XB, 56, 820); tw = t.textlength(s, font=f)
        t.text((cx - tw / 2, y), s, font=f, fill=WHITE if k == 0 else YEL); y += f.size + 26
    if src:
        f = F(BOLD, 27); tw = t.textlength(src, font=f); t.text((cx - tw / 2, y + 8), src, font=f, fill=SUB)
    assert y < 1560, y
    if handle:
        f = F(BOLD, 28); tw = t.textlength(HANDLE, font=f)
        t.rounded_rectangle((40, TOP + 24, 40 + tw + 36, TOP + 72), 24, fill=(20, 33, 61, 190))
        t.text((58, TOP + 30), HANDLE, font=f, fill=WHITE)
    return L


def photo(idx, dur, dirn=1, dark=0.0):
    src = Image.open(f'{IMG}/img{idx}.png').convert('RGB')
    sw, sh = src.size; ar = W / MID
    bw, bh = (sw, sw / ar) if sw / sh < ar else (sh * ar, sh)
    veil = Image.new('RGB', (W, MID), NAVY)
    def fn(t):
        z = 1 + 0.08 * t / dur; cw, ch = bw / z, bh / z
        x0 = (sw - cw) / 2 + dirn * (bw - cw) * 0.3; y0 = (sh - ch) / 2
        im = src.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, MID), Image.BILINEAR)
        return Image.blend(im, veil, dark) if dark else im
    return fn


def apt_card(tag, name, line, badge=None, tagcol=YEL, w=840, h=176):
    """단지 카드: 지역 태그 / 단지명 / 한 줄 정보 / (오른쪽 배지)"""
    c = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w, h), 28, fill=(255, 255, 255, 248))
    d.rounded_rectangle((0, 0, 14, h), 7, fill=tagcol)
    f = F(XB, 30); tw = d.textlength(tag, font=f)
    d.rounded_rectangle((36, 20, 36 + tw + 32, 66), 23, fill=NAVY); d.text((52, 24), tag, font=f, fill=tagcol)
    bw = 0
    if badge:
        bf = F(BLACK, 34); bw = d.textlength(badge, font=bf) + 40
        d.rounded_rectangle((w - bw - 24, 20, w - 24, 70), 25, fill=RED); d.text((w - bw - 4, 25), badge, font=bf, fill=WHITE)
    nf = fit(d, name, BLACK, 50, w - 70); d.text((36, 74), name, font=nf, fill=INK)
    lf = fit(d, line, BOLD, 32, w - 70); d.text((36, 74 + nf.size + 12), line, font=lf, fill=GRAY)
    return c


def card_list(cards, t0=0.35, gap=0.3, x=40):
    hs = [c.height for c in cards]; sp = 22
    y0 = TOP + (MID - sum(hs) - sp * (len(cards) - 1)) // 2
    def fx(t, fr):
        y = y0
        for i, c in enumerate(cards):
            p = ease((t - t0 - i * gap) / 0.32)
            if p > 0: fr.alpha_composite(alpha(c, p), (x + int((1 - p) * 140), y))
            y += c.height + sp
    return fx


SC = []

# 1. 훅: 11월에만 5.6만 가구
def s1():
    dur = 3.6; ph = photo(0, dur, 1, dark=0.35)
    T = text_layer([('11~12월 청약', 0), ('올해 마지막 막차', 1)],
                   ['11월에만 5만6천 가구 쏟아져요', '작년 11월보다 89% 늘었어요'], '출처: 부동산R114 (2026.10.28)', handle=False)
    def fx(t, fr):
        p = ease((t - 0.2) / 1.4); n = int(56533 * p)
        L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
        s = f'{n:,}'; f = F(BLACK, 168); tw = d.textlength(s, font=f) + d.textlength('가구', font=F(BLACK, 80)) + 16
        x = (W - tw) / 2; y = TOP + 200
        d.text((x + 4, y + 6), s, font=f, fill=(0, 0, 0, 120)); d.text((x, y), s, font=f, fill=YEL)
        x2 = x + d.textlength(s, font=f) + 16
        d.text((x2, y + 74), '가구', font=F(BLACK, 80), fill=WHITE)
        lab = '11월 전국 분양 예정'; lf = F(XB, 42); lw = d.textlength(lab, font=lf)
        d.rounded_rectangle(((W - lw) / 2 - 26, TOP + 112, (W + lw) / 2 + 26, TOP + 176), 32, fill=(20, 33, 61, 220))
        d.text(((W - lw) / 2, TOP + 118), lab, font=lf, fill=WHITE)
        if t > 1.7:
            q = ease((t - 1.7) / 0.25); up = '전년 대비 +89%'; uf = F(BLACK, 50); uw = d.textlength(up, font=uf)
            d.rounded_rectangle(((W - uw) / 2 - 30, TOP + 420, (W + uw) / 2 + 30, TOP + 496), 38, fill=RED + (int(255 * q),))
            d.text(((W - uw) / 2, TOP + 428), up, font=uf, fill=WHITE + (int(255 * q),))
        fr.alpha_composite(L)
    return dur, ph, T, fx
SC.append(s1)

# 2. 서울 대장: 디에이치 반포124
def s2():
    dur = 4.4; ph = photo(3, dur, -1, dark=0.15)
    T = text_layer([('서울 대장은 여기', 0), ('디에이치 반포124', 1)],
                   ['반포주공1단지 재건축, 총 5,007가구', '일반분양만 1,832가구'], '청약은 11월 말 이후 예정 (블로터 2026.11)')
    rows = [('위치', '서울 서초구 반포동'), ('규모', '총 5,007가구'), ('일반분양', '1,832가구 (59~130㎡)'), ('시공', '현대건설')]
    L = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(L)
    x0, x1, y0 = 60, 860, TOP + 150; rh = 92
    d.rounded_rectangle((x0, y0, x1, y0 + rh * len(rows) + 30), 30, fill=(255, 255, 255, 245))
    for k, (a, b) in enumerate(rows):
        y = y0 + 22 + k * rh
        if k: d.line((x0 + 30, y - 4, x1 - 30, y - 4), fill=(222, 226, 235), width=2)
        d.text((x0 + 40, y + 18), a, font=F(XB, 34), fill=GRAY)
        f = fit(d, b, BLACK, 44, 480); bw = d.textlength(b, font=f)
        if k == 2: d.rectangle((x1 - 40 - bw - 6, y + 46, x1 - 34, y + 72), fill=(255, 236, 160))
        d.text((x1 - 40 - bw, y + 16), b, font=f, fill=RED if k == 2 else INK)
    def fx(t, fr):
        p = ease((t - 0.4) / 0.4); fr.alpha_composite(alpha(L, p), (0, int((1 - p) * 60)))
    return dur, ph, T, fx
SC.append(s2)

# 3. 11월 서울 라인업
def s3():
    dur = 4.4; ph = photo(0, dur, -1, dark=0.6)
    cards = [apt_card('종로 교남동', '경희궁 에피트', '도심 재개발 · 광화문 직주근접', '11월'),
             apt_card('영등포 문래동', '해링턴 플레이스 문래', '218가구 전부 일반분양', '11월'),
             apt_card('서초 서초동', '서초 롯데캐슬 아트팰리스', '835가구 규모', '11월')]
    T = text_layer([('11월 서울 라인업', 1)], ['강남부터 도심까지', '서울만 7,240가구 예정'], '출처: 부동산R114·직방 (2026.10~11)', handle=False)
    return dur, ph, T, card_list(cards)
SC.append(s3)

# 4. 12월 서울
def s4():
    dur = 4.4; ph = photo(3, dur, 1, dark=0.6)
    cards = [apt_card('동대문 용두동', '용두동 롯데캐슬', '417가구 중 340가구 일반분양', '12월', CORAL),
             apt_card('성북 동선동', '동선2구역 재개발', '계룡건설 · 연내 분양 준비', '12월', CORAL),
             apt_card('강남 대치동', '남서울종합시장 정비사업', '포스코이앤씨 · 70가구 일반분양', '12월', CORAL)]
    T = text_layer([('12월엔 여기', 1)], ['연말까지 정비사업 물량 계속', '일정은 사업 상황 따라 바뀔 수 있어요'], chip=None, handle=False)
    return dur, ph, T, card_list(cards)
SC.append(s4)

# 5. 경기·인천
def s5():
    dur = 4.4; ph = photo(0, dur, 1, dark=0.6)
    cards = [apt_card('경기 의정부', '의정부역 펠리스타워 양우내안애', '최고 49층 · 아파트 1,252가구', '11월', GREEN),
             apt_card('인천 검단', '검단 센트레빌 그랑포레', '843가구 · 검단 첫 민간공원 특례', '11월', GREEN),
             apt_card('인천 송도', '송도 대광로제비앙 모아엘가', '592가구', '11월', GREEN)]
    T = text_layer([('경기·인천', 0), ('경기만 2만 가구', 1)], ['11월 전국 시·도 중 경기가 최다', '2만278가구 분양 예정'], '출처: 부동산R114 (2026.10.28)', handle=False)
    return dur, ph, T, card_list(cards)
SC.append(s5)

# 6. 지방
def s6():
    dur = 4.2; ph = photo(3, dur, -1, dark=0.6)
    cards = [apt_card('세종 합강동', '세종스마트시티 엘 수자인', '84㎡ 2,191가구 전부 일반분양', '최대어', YEL),
             apt_card('울산 울주', '힐스테이트 울산역리버포레', '84㎡ 436가구 일반분양', '11월', YEL),
             apt_card('부산 연제', '연산역 수자인 센트리오', '335가구 중 139가구 일반분양', '11월', YEL)]
    T = text_layer([('지방은', 0), ('세종이 최대어', 1)], ['지방 물량도 작년보다 3.7배', '세종·경북·부산에 몰려요'], '출처: 부동산R114 (2026.10.28)', handle=False)
    return dur, ph, T, card_list(cards)
SC.append(s6)

# 7. 반전: 당첨보다 무서운 건 잔금
def s7():
    dur = 3.8; ph = photo(1, dur, 1, dark=0.2)
    T = text_layer([('근데 당첨보다', 0), ('무서운 건 잔금', 1)],
                   ['당첨돼도 돈 못 맞추면 끝', '자금 계획부터 세우고 넣으세요'])
    st = Image.new('RGBA', (600, 200)); d = ImageDraw.Draw(st)
    d.rounded_rectangle((8, 8, 592, 192), 26, outline=RED + (255,), width=14)
    f = F(BLACK, 96); tw = d.textlength('잔금 체크', font=f); d.text(((600 - tw) / 2, 36), '잔금 체크', font=f, fill=RED + (255,))
    st = st.rotate(-10, expand=True, resample=Image.BICUBIC)
    def fx(t, fr):
        if t > 0.6:
            p = ease((t - 0.6) / 0.18); s = 1.7 - 0.7 * p
            im = alpha(st.resize((int(st.width * s), int(st.height * s))), p)
            fr.alpha_composite(im, (int(470 - im.width / 2), int(TOP + MID / 2 - im.height / 2)))
    return dur, ph, T, fx
SC.append(s7)

# 8. 청약 전 자금 체크 3
def s8():
    dur = 4.6; ph = photo(2, dur, -1, dark=0.62)
    def chk(n, a, b):
        c = Image.new('RGBA', (840, 176)); d = ImageDraw.Draw(c)
        d.rounded_rectangle((0, 0, 840, 176), 28, fill=(255, 255, 255, 248))
        d.ellipse((30, 40, 126, 136), fill=YEL); f = F(BLACK, 60); tw = d.textlength(n, font=f); d.text((78 - tw / 2, 48), n, font=f, fill=NAVY)
        d.text((156, 30), a, font=fit(d, a, BLACK, 50, 650), fill=INK); d.text((156, 100), b, font=fit(d, b, BOLD, 32, 650), fill=GRAY)
        return c
    cards = [chk('1', '계약금 현금', '보통 분양가의 10~20%, 대출 안 돼요'),
             chk('2', '중도금 대출 조건', '모집공고에서 집단대출 여부 확인'),
             chk('3', '잔금대출 한도', '입주 때 시세·LTV·DSR로 다시 심사')]
    T = text_layer([('청약 넣기 전', 0), ('돈 체크 3가지', 1)], ['이거 안 보고 넣으면', '당첨이 독이 될 수 있어요'], handle=False)
    return dur, ph, T, card_list(cards, gap=0.45)
SC.append(s8)

# 9. CTA
def s9():
    dur = 3.8
    sub = ["댓글에 '한도' 남겨주세요", '단지별 잔금 한도 DM 드려요'] if V == 'ig' else ['채널 이름 누르고 프로필 링크', '우리 단지 한도 1분이면 확인']
    T = text_layer([('저장해두고', 0), ('잔금 한도부터 확인', 1)], sub)
    sv = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(sv)
    msg = '📌 저장 필수'; f = F(BLACK, 54); s = '저장 필수'; tw = d.textlength(s, font=f)
    d.rounded_rectangle((470 - tw / 2 - 40, TOP + 280, 470 + tw / 2 + 40, TOP + 370), 45, fill=RED, outline=YEL, width=4)
    d.text((470 - tw / 2, TOP + 290), s, font=f, fill=WHITE)
    def fx(t, fr):
        if t > 0.5:
            p = ease((t - 0.5) / 0.2); fr.alpha_composite(alpha(sv, p))
    return dur, photo(4, dur, 1), T, fx
SC.append(s9)


def render_scene(i, fn):
    dur, mid, T, fx = fn()
    n = int(round(dur * FPS))
    if SNAP:
        k = int(n * 0.85); t = k / FPS
        fr = Image.new('RGBA', (W, H), NAVY + (255,)); fr.paste(mid(t), (0, TOP)); fr.alpha_composite(T)
        if fx: fx(t, fr)
        fr.convert('RGB').save(f'{OUT}/snap{i:02d}.jpg', quality=88); return dur
    tmp, out = f'{OUT}/s{i:02d}.tmp.mp4', f'{OUT}/s{i:02d}.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS
        fr = Image.new('RGBA', (W, H), NAVY + (255,)); fr.paste(mid(t), (0, TOP))
        fr.alpha_composite(alpha(T, ease(t / 0.3)))
        if fx: fx(t, fr)
        p.stdin.write(fr.convert('RGB').tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    return dur


if __name__ == '__main__':
    total = sum(render_scene(i + 1, fn) for i, fn in enumerate(SC))
    print('scenes', total)
    if SNAP: sys.exit()
    o = f'{OUT}/s99.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', OUTRO, '-vf', 'scale=1080:1920,fps=30,setsar=1', '-an',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', f'{OUT}/s99.tmp.mp4'], check=True)
    os.replace(f'{OUT}/s99.tmp.mp4', o)
    with open(f'{OUT}/list.txt', 'w') as fh:
        for i in range(len(SC)): fh.write(f"file 's{i + 1:02d}.mp4'\n")
        fh.write("file 's99.mp4'\n")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-c', 'copy', f'{OUT}/video.mp4'], check=True)
    tot = total + 8
    bgm = '/home/claude/cy/bgm.wav'
    name = 'reel_insta' if V == 'ig' else 'shorts_youtube'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}/video.mp4', '-i', bgm,
                    '-filter_complex', f'[1:a]atrim=0:{tot},volume=0.9,afade=t=out:st={tot - 1.8}:d=1.8[a]', '-map', '0:v', '-map', '[a]',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', f'{OUT}/{name}.tmp.mp4'], check=True)
    os.replace(f'{OUT}/{name}.tmp.mp4', f'{OUT}/{name}.mp4')
    print('done', f'{OUT}/{name}.mp4', tot)
