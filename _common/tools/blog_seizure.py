# 블로그 이미지 3세트 (네이버=네이비 / 구글=틸 카드 / 티스토리=퍼플 카드) — 압류·연체 대출 편, 서로 중복 없음
import sys, os
sys.argv = ['x', 'yt']; sys.path.insert(0, os.path.dirname(__file__))
import make_seizure as M
from PIL import Image, ImageDraw, ImageFilter

F, fit = M.F, M.fit
BLACK, BOLD = M.BLACK, M.BOLD
OUT = '/home/claude/rl/blog'
YEL = (255, 201, 40); CORAL = (255, 122, 89); WHITE = (255, 255, 255); RED = (232, 65, 58); GREEN = (46, 196, 125)

THEMES = {
    'naver':   dict(bg=(20, 33, 61), card=None, acc=YEL, sub=(190, 202, 225), W=1080),
    'google':  dict(bg=(236, 241, 246), card=(12, 56, 72), acc=(110, 231, 196), sub=(178, 214, 210), W=1200),
    'tistory': dict(bg=(40, 26, 58), card=(52, 33, 80), acc=(255, 168, 76), sub=(205, 190, 230), W=1200),
}


class Card:
    """테마별 캔버스. naver=전체 배경, google/tistory=바깥 배경 위 카드"""
    def __init__(self, theme, h):
        self.t = THEMES[theme]; self.theme = theme; W = self.t['W']
        if theme == 'naver':
            self.im = Image.new('RGB', (W, h), self.t['bg']); self.x0, self.y0, self.x1 = 70, 40, W - 70
        else:
            self.im = Image.new('RGB', (W, h), self.t['bg'])
            d = ImageDraw.Draw(self.im)
            if theme == 'google':
                d.rectangle((0, 0, 10, h), fill=(240, 205, 90))
                d.text((48, 24), 'LTV연구소', font=F(BOLD, 26), fill=(60, 80, 95))
                cx0, cy0, cx1, cy1 = 60, 72, W - 60, h - 40
            else:
                for i in range(0, h, 4):
                    d.line((0, i, W, i), fill=(40 + i * 10 // h, 26, 58 + i * 20 // h))
                cx0, cy0, cx1, cy1 = 70, 40, W - 70, h - 50
            sh = Image.new('RGBA', (W, h)); ImageDraw.Draw(sh).rounded_rectangle((cx0 + 8, cy0 + 12, cx1 + 8, cy1 + 12), 26, fill=(0, 0, 0, 70))
            self.im.paste(sh.filter(ImageFilter.GaussianBlur(12)), (0, 0), sh.filter(ImageFilter.GaussianBlur(12)))
            d.rounded_rectangle((cx0, cy0, cx1, cy1), 26, fill=self.t['card'])
            self.x0, self.y0, self.x1 = cx0 + 50, cy0 + 30, cx1 - 50
            if theme == 'tistory':
                f = F(BOLD, 24); tw = d.textlength('LTV연구소', font=f)
                d.rounded_rectangle((W - 60 - tw - 30, h - 40, W - 60, h - 6), 17, fill=WHITE)
                d.text((W - 60 - tw - 15, h - 39), 'LTV연구소', font=f, fill=(40, 26, 58))
        self.d = ImageDraw.Draw(self.im); self.y = self.y0
        f = F(BOLD, 22); tw = self.d.textlength('LTV연구소', font=f)
        if theme != 'tistory':
            self.d.rounded_rectangle((self.x0 - 10, self.y, self.x0 + tw + 20, self.y + 34), 17, fill=(235, 225, 200))
            self.d.text((self.x0 + 5, self.y + 2), 'LTV연구소', font=f, fill=(20, 33, 61))
        self.y += 56

    @property
    def W(self): return self.t['W']

    def chip(self, s, col=None, center=False):
        f = F(BLACK, 30); tw = self.d.textlength(s, font=f)
        x = (self.W - tw) / 2 - 22 if center else self.x0
        self.d.rounded_rectangle((x, self.y, x + tw + 44, self.y + 52), 26, fill=col or self.t['acc'])
        self.d.text((x + 22, self.y + 6), s, font=f, fill=(20, 33, 61)); self.y += 72

    def title(self, lines, size=64, center=False):
        for s, em in lines:
            f = fit(self.d, s, BLACK, size, self.x1 - self.x0); tw = self.d.textlength(s, font=f)
            x = (self.W - tw) / 2 if center else self.x0
            self.d.text((x, self.y), s, font=f, fill=self.t['acc'] if em else WHITE); self.y += f.size + 18
        self.y += 6

    def text(self, s, size=32, col=None, center=False, font=BOLD):
        f = fit(self.d, s, font, size, self.x1 - self.x0); tw = self.d.textlength(s, font=f)
        self.d.text(((self.W - tw) / 2 if center else self.x0, self.y), s, font=f, fill=col or self.t['sub']); self.y += f.size + 16

    def box(self, h, fill=(255, 255, 255)):
        b = (self.x0, self.y, self.x1, self.y + h); self.d.rounded_rectangle(b, 22, fill=fill); self.y += h + 20; return b

    def paste_doc(self, pdf, p, cy_pt, rows, col=(255, 214, 0), h=460, cx_pt=300, win_pt=470, stamp=None, label=None):
        pg = M.page(pdf, p).copy().convert('RGBA'); S = 3
        hl = Image.new('RGBA', pg.size); dd = ImageDraw.Draw(hl)
        for a, b in rows: dd.rectangle((78 * S, a * S, 560 * S, b * S), fill=col + (95,))
        pg = Image.alpha_composite(pg, hl).convert('RGB')
        w = self.x1 - self.x0; ww = win_pt * S; hh = ww * h / w
        crop = pg.crop((cx_pt * S - ww / 2, cy_pt * S - hh / 2, cx_pt * S + ww / 2, cy_pt * S + hh / 2)).resize((w, h), Image.LANCZOS)
        m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w, h), 18, fill=255)
        self.im.paste(crop, (self.x0, self.y), m)
        if stamp:
            st = M.stamp(stamp, RED, 96, -9); self.im.paste(st, (self.x1 - st.width - 30, self.y + h // 2 - st.height // 2), st)
        if label:
            f1, f2 = F(BLACK, 30), F(BOLD, 24); lw = max(self.d.textlength(label[0], font=f1), self.d.textlength(label[1], font=f2)) + 44
            ly = self.y + h - 104
            self.d.rounded_rectangle((self.x0 + 16, ly, self.x0 + 16 + lw, ly + 90), 16, fill=(20, 33, 61))
            self.d.rectangle((self.x0 + 16, ly + 16, self.x0 + 22, ly + 74), fill=YEL)
            self.d.text((self.x0 + 38, ly + 8), label[0], font=f1, fill=YEL); self.d.text((self.x0 + 38, ly + 50), label[1], font=f2, fill=WHITE)
        self.y += h + 24

    def save(self, path, fixed=False):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im = self.im
        if not fixed:
            if self.theme == 'naver':
                im = im.crop((0, 0, self.W, min(im.height, self.y + 50)))
            else:
                cx0, cy0, cx1 = (60, 72, self.W - 60) if self.theme == 'google' else (70, 40, self.W - 70)
                bottom_m = 40 if self.theme == 'google' else 50
                card_b = self.y + 30; nh = card_b + bottom_m
                n = Card(self.theme, nh)
                n.im.paste(im.crop((cx0, cy0 + 26, cx1, card_b - 26)), (cx0, cy0 + 26))
                im = n.im
        im.save(path, quality=90)


def steps(c, items, numcol=None, h=118):
    for i, (a, b) in enumerate(items):
        x0, y0, x1, y1 = c.x0, c.y, c.x1, c.y + h
        c.d.rounded_rectangle((x0, y0, x1, y1), 22, fill=WHITE)
        c.d.ellipse((x0 + 24, y0 + 24, x0 + 94, y0 + 94), fill=numcol or c.t['acc'])
        f = F(BLACK, 40); n = str(i + 1); tw = c.d.textlength(n, font=f); c.d.text((x0 + 59 - tw / 2, y0 + 30), n, font=f, fill=(20, 33, 61))
        c.d.text((x0 + 120, y0 + 16), a, font=fit(c.d, a, BLACK, 40, x1 - x0 - 150), fill=(20, 33, 61))
        c.d.text((x0 + 122, y0 + 70), b, font=fit(c.d, b, BOLD, 27, x1 - x0 - 150), fill=(90, 100, 125))
        c.y += h + 16


def table(c, head, rows, colw, rh=96):
    x = c.x0; W_ = c.x1 - c.x0; y = c.y
    c.d.rounded_rectangle((x, y, c.x1, y + 70 + rh * len(rows)), 22, fill=WHITE)
    cx = x
    for k, (hname, w) in enumerate(zip(head, colw)):
        ww = W_ * w
        if k: c.d.rounded_rectangle((cx + 6, y + 10, cx + ww - 6, y + 62), 16, fill=c.t['acc'] if k == 1 else CORAL)
        f = F(BLACK, 30); tw = c.d.textlength(hname, font=f); c.d.text((cx + ww / 2 - tw / 2, y + 16), hname, font=f, fill=(20, 33, 61) if k else (110, 120, 140))
        cx += ww
    yy = y + 70
    for r in rows:
        c.d.line((x + 16, yy, c.x1 - 16, yy), fill=(220, 225, 232), width=2); cx = x
        for k, (v, w) in enumerate(zip(r, colw)):
            ww = W_ * w; lines = v.split('\n'); fy = yy + (rh - len(lines) * 38) / 2 - 4
            for j, s in enumerate(lines):
                f = fit(c.d, s, BLACK if (k == 0 or j == 0) else BOLD, 30 if k else 28, ww - 24); tw = c.d.textlength(s, font=f)
                c.d.text((cx + ww / 2 - tw / 2, fy), s, font=f, fill=(110, 120, 140) if k == 0 else ((20, 33, 61) if j == 0 else (80, 95, 120))); fy += 38
            cx += ww
        yy += rh
    c.y = yy + 20


def kakao_card(c, h=330, secret=True):
    KY = (254, 229, 0); BR = (58, 29, 29)
    x0, y0, x1 = c.x0, c.y, c.x1
    c.d.rounded_rectangle((x0, y0, x1, y0 + 96), 48, fill=WHITE, outline=KY, width=7)
    c.d.ellipse((x0 + 34, y0 + 26, x0 + 78, y0 + 70), outline=BR, width=6); c.d.line((x0 + 72, y0 + 64, x0 + 92, y0 + 84), fill=BR, width=8)
    c.d.text((x0 + 116, y0 + 18), 'LTV연구소', font=F(BLACK, 50), fill=(25, 25, 30))
    yy = y0 + 116
    c.d.rounded_rectangle((x0, yy, x1, yy + 150), 26, fill=WHITE)
    c.d.ellipse((x0 + 24, yy + 22, x0 + 130, yy + 128), fill=(20, 33, 61))
    c.d.line([(x0 + 52, yy + 78), (x0 + 77, yy + 52), (x0 + 102, yy + 78)], fill=(232, 214, 180), width=7)
    c.d.line([(x0 + 60, yy + 72), (x0 + 60, yy + 100), (x0 + 94, yy + 100), (x0 + 94, yy + 72)], fill=(232, 214, 180), width=7)
    c.d.text((x0 + 156, yy + 26), 'LTV연구소', font=F(BLACK, 46), fill=(20, 20, 26))
    tw = c.d.textlength('LTV연구소', font=F(BLACK, 46))
    c.d.rounded_rectangle((x0 + 170 + tw, yy + 36, x0 + 250 + tw, yy + 76), 12, fill=KY); c.d.text((x0 + 183 + tw, yy + 36), '채널', font=F(BLACK, 26), fill=BR)
    c.d.text((x0 + 158, yy + 88), '아파트 대출 한도·시세 상담', font=F(BOLD, 28), fill=(120, 120, 128))
    c.d.rounded_rectangle((x1 - 190, yy + 46, x1 - 30, yy + 106), 30, fill=KY); c.d.text((x1 - 145, yy + 52), '채팅', font=F(BLACK, 34), fill=BR)
    c.y = yy + 170
    if secret:
        f = F(BLACK, 40); s = '상담 요청·내용 기밀 엄수'; tw = c.d.textlength(s, font=f)
        bx = (c.W - tw - 100) / 2
        c.d.rounded_rectangle((bx, c.y, bx + tw + 100, c.y + 76), 38, fill=YEL)
        lx, ly = bx + 26, c.y + 18
        c.d.arc((lx + 4, ly - 4, lx + 30, ly + 24), 180, 360, fill=(20, 33, 61), width=6)
        c.d.line((lx + 4, ly + 10, lx + 4, ly + 18), fill=(20, 33, 61), width=6); c.d.line((lx + 30, ly + 10, lx + 30, ly + 18), fill=(20, 33, 61), width=6)
        c.d.rounded_rectangle((lx, ly + 16, lx + 34, ly + 46), 6, fill=(20, 33, 61))
        c.d.text((bx + 74, c.y + 10), s, font=f, fill=(20, 33, 61)); c.y += 96


# ================= 네이버 =================
def naver():
    o = f'{OUT}/naver'
    c = Card('naver', 800); c.y = 190
    c.chip('세무서 압류 · 카드 연체 중인데', center=True)
    c.title([('대출, 진짜', 0), ('끝난 걸까?', 1)], 110, center=True)
    c.text('실제 등기부등본 2건으로 본 해법', 40, center=True); c.save(f'{o}/00.jpg', fixed=True)

    c = Card('naver', 2200); c.chip('기준')
    c.title([('은행이 보는 것 vs', 0), ('담보대출이 보는 것', 1)])
    c.text('연체·압류 기록이 있으면 심사 기준이 완전히 달라져요', 30); c.y += 20
    rows = [('신용점수·연체', '바로 부결 사유', '참고 사항'), ('압류·가압류', '실행 어려움', '정리 조건으로 진행'),
            ('핵심 기준', '신용·소득', '집 시세 · 남은 한도'), ('주로 가는 곳', '은행·상호금융', '저축은행·캐피탈·대부')]
    table(c, ['', '은행', '담보대출(2금융)'], rows, [0.28, 0.36, 0.36], rh=150)
    c.text('※ 금융사·상품마다 기준이 달라요', 26); c.save(f'{o}/01.jpg')

    c = Card('naver', 2200); c.chip('CASE 1', CORAL)
    c.title([('세금 밀려서', 0), ('세무서 압류 걸린 집', 1)])
    c.text('갑구 5번 · 2026년 8월 국세 압류(권리자: 국)', 30); c.y += 10
    c.paste_doc('suwon', 3, 410, [(427, 459)], col=(255, 90, 80), h=640, stamp='압류', label=('경기 수원 권선 · 73㎡ 구축', '2015년 압류는 해제(말소) → 2026년 다시 압류'))
    c.text('등기 출처: 2026.11 열람 등기사항전부증명서 · 개인정보 가림', 24); c.save(f'{o}/02.jpg')

    c = Card('naver', 2200); c.chip('해법')
    c.title([('대출금으로 세금부터 내고', 0), ('압류 풀면서 진행', 1)])
    c.text("'압류 해제 조건부' 실행 흐름", 32); c.y += 14
    steps(c, [('시세·선순위 확인', '하나은행 1순위 + 대부 후순위 → 남은 한도 계산'), ('체납액 확인', '세무서 체납 세액 확정 (가산금 포함)'),
              ('대출 실행 = 세금 납부', '실행 당일 대출금에서 체납액 먼저 납부'), ('압류 해제(말소)', '세무서 해제 → 등기에서 압류 지움'),
              ('남은 돈으로 정리', '고금리 후순위 대환 등')], h=130)
    c.save(f'{o}/03.jpg')

    c = Card('naver', 2200); c.chip('CASE 2', CORAL)
    c.title([('카드값 밀려 가압류 2건', 0), ('한 달 뒤 경매 개시', 1)])
    c.paste_doc('sadang', 4, 625, [(557, 612), (635, 690)], h=420, label=('서울 동작 사당 · 59㎡ 공유지분 1/5', '1월 국민카드 · 2월 하나카드 가압류 (약 6,770만원)'))
    c.paste_doc('sadang', 5, 185, [(154, 214)], col=(255, 90, 80), h=300, stamp='경매')
    c.save(f'{o}/04.jpg')

    c = Card('naver', 2200); c.chip('정리')
    c.title([('압류·연체 있을 때', 0), ('상황별 길 찾기', 1)])
    c.y += 10
    steps(c, [('연체 중', '은행 대신 저축은행·캐피탈·대부 담보대출로 길 찾기'), ('세금 압류', '대출금으로 세금 납부 → 압류 해제 조건 실행'),
              ('카드 가압류', '채무 상환 후 가압류 해제 → 대환'), ('경매 개시', '매각(낙찰) 전에 대환으로 상환 → 취하 진행')], numcol=CORAL, h=150)
    c.text('※ 한도·금리는 시세·선순위·연체 규모에 따라 달라요', 26); c.save(f'{o}/05.jpg')

    c = Card('naver', 2200); c.chip('상담')
    c.title([('댓글 부담되면', 0), ("카톡에서 'LTV연구소'", 1)])
    c.y += 10; kakao_card(c); c.text('검색 → 채널 추가 → 채팅으로 1:1 상담 신청', 30, center=True); c.save(f'{o}/kakao.jpg')

    c = Card('naver', 520); c.y = 110
    c.title([('우리 집 남은 한도', 0), ('1분이면 확인', 1)], 72, center=True)
    c.text('ltvlab.vercel.app  ·  시세 · 실거래 · 한도 계산', 34, col=WHITE, center=True); c.save(f'{o}/banner.jpg', fixed=True)


# ================= 구글 블로그 =================
def google():
    o = f'{OUT}/google'
    c = Card('google', 760); c.y += 60
    c.chip('국세 체납 압류', center=True)
    c.title([('세금 압류 걸린 집도', 0), ('담보대출 될까?', 1)], 92, center=True)
    c.text('압류 해제 조건부 대출 구조와 체크포인트', 36, center=True); c.save(f'{o}/00.jpg', fixed=True)

    c = Card('google', 2200); c.chip('개념')
    c.title([('국세 압류가 등기에', 0), ('올라가는 순서', 1)])
    c.y += 10
    steps(c, [('세금 체납', '납부기한이 지나도 안 낸 세금'), ('독촉장 발송', '세무서가 기한을 정해 납부 독촉'),
              ('부동산 압류 등기', "갑구에 '압류 · 권리자 국'으로 기록"), ('그래도 안 내면', '공매 절차로 넘어갈 수 있음')], h=128)
    c.save(f'{o}/01.jpg')

    c = Card('google', 2200); c.chip('실제 등기')
    c.title([('압류 집에 이미 있던', 0), ('근저당 2건', 1)])
    c.text('을구 · 하나은행 1순위 + 대부업체 후순위', 30); c.y += 6
    c.paste_doc('suwon', 5, 430, [(350, 380), (493, 512)], h=600, label=('경기 수원 권선 · 73㎡', '하나은행 최고액 1억 5,160만 · 대부 최고액 1억 8,200만'))
    c.text('※ 채권최고액은 실제 대출금보다 보통 20~30% 높게 잡혀요', 24); c.save(f'{o}/02.jpg')

    c = Card('google', 2200); c.chip('계산')
    c.title([('대출이 되느냐는', 0), ("'남은 한도'로 갈려요", 1)])
    c.y += 10
    bx = c.box(560); d = c.d; x0, y0, x1, _ = bx
    items = [('시세(KB 등)', '집값 기준', (20, 33, 61)), ('− 선순위 대출 잔액', '1순위·후순위 실제 잔액', (90, 100, 125)),
             ('− 체납 세금', '실행 때 먼저 납부', RED), ('= 남은 여력', '이게 플러스여야 진행 가능', (12, 120, 100))]
    yy = y0 + 30
    for a, b, col in items:
        d.text((x0 + 40, yy), a, font=F(BLACK, 46), fill=col); d.text((x0 + 44, yy + 62), b, font=F(BOLD, 28), fill=(110, 120, 140)); yy += 130
    c.save(f'{o}/03.jpg')

    c = Card('google', 2200); c.chip('체크리스트')
    c.title([('상담 전에', 0), ('이것만 알아두세요', 1)])
    c.y += 10
    steps(c, [('체납 세액', '세목·금액 (홈택스·세무서 확인)'), ('기존 대출 잔액', '은행·대부 각각 남은 금액'),
              ('연체 기간', '언제부터 몇 회 밀렸는지'), ('급한 날짜', '공매·경매 일정이 잡혔는지')], numcol=(240, 205, 90), h=128)
    c.save(f'{o}/04.jpg')

    c = Card('google', 2200); c.chip('상담')
    c.title([("카카오톡 'LTV연구소'", 0), ('1:1 비공개 상담', 1)])
    c.y += 6; kakao_card(c); c.save(f'{o}/05.jpg')


# ================= 티스토리 =================
def tistory():
    o = f'{OUT}/tistory'
    c = Card('tistory', 740); c.y += 70
    c.chip('카드 연체 → 경매 개시', center=True)
    c.title([('가압류에서 경매까지', 0), ('딱 6주', 1)], 96, center=True)
    c.text('실제 등기로 본 타임라인과 경매 취하 타이밍', 36, center=True); c.save(f'{o}/00.jpg', fixed=True)

    c = Card('tistory', 2200); c.chip('타임라인')
    c.title([('등기에 찍힌 날짜', 0), ('순서대로 보면', 1)])
    c.y += 10
    ev = [('2025.10', '지분 담보 근저당 설정', '공유지분 1/5에 대부 최고액 1.6억'), ('2026.01.20', '국민카드 가압류', '청구 약 2,997만원'),
          ('2026.02.02', '하나카드 가압류', '청구 약 3,771만원'), ('2026.03.04', '임의경매 개시결정', '근저당권자가 경매 신청'),
          ('2026.09.18', '근저당 채권 양도', '다른 대부업체로 넘어감')]
    x = c.x0 + 40; d = c.d
    d.line((x, c.y + 20, x, c.y + 20 + 150 * (len(ev) - 1)), fill=c.t['acc'], width=6)
    for i, (dt, a, b) in enumerate(ev):
        yy = c.y + i * 150
        col = RED if '경매' in a else c.t['acc']
        d.ellipse((x - 18, yy + 2, x + 18, yy + 38), fill=col)
        d.text((x + 44, yy - 4), dt, font=F(BLACK, 30), fill=col)
        d.text((x + 230, yy - 6), a, font=F(BLACK, 38), fill=WHITE); d.text((x + 232, yy + 46), b, font=F(BOLD, 28), fill=c.t['sub'])
    c.y += 150 * len(ev); c.save(f'{o}/01.jpg')

    c = Card('tistory', 2200); c.chip('실제 등기')
    c.title([('을구에 남은', 0), ('지분 근저당 1억 6천', 1)])
    c.paste_doc('sadang', 7, 690, [(649, 700)], h=330)
    c.paste_doc('sadang', 8, 360, [(324, 345), (389, 410)], h=300, label=('서울 동작 사당 · 59㎡', '근저당 이전(확정채권양도) 2026.9'))
    c.save(f'{o}/02.jpg')

    c = Card('tistory', 2200); c.chip('용어')
    c.title([('압류 · 가압류 · 경매', 0), ('뭐가 다를까?', 1)])
    c.y += 10
    rows = [('압류', '세금(국가)·확정 판결', '바로 공매·경매로\n갈 수 있음'), ('가압류', '카드사 등 채권자', '재산 묶어두기\n(판결 전 보전)'),
            ('임의경매', '근저당권자', '담보 실행\n→ 매각')]
    table(c, ['', '누가 거나', '의미'], rows, [0.24, 0.38, 0.38], rh=150)
    c.save(f'{o}/03.jpg')

    c = Card('tistory', 2200); c.chip('타이밍')
    c.title([('경매 취하,', 0), ('언제까지 되나', 1)])
    c.y += 10
    steps(c, [('경매 개시 ~ 매각기일 전', '빚 갚으면 채권자가 경매 취하 (가장 수월)'), ('매각기일 ~ 대금 납부 전', '최고가매수인 동의까지 필요해서 어려워짐'),
              ('대금 납부 후', '소유권 넘어감 → 사실상 끝')], numcol=c.t['acc'], h=150)
    c.text('※ 경매 일정·채권액에 따라 달라요. 날짜부터 확인하세요', 26); c.save(f'{o}/04.jpg')

    c = Card('tistory', 2200); c.chip('상담')
    c.title([('경매 날짜 잡혔다면', 0), ('카톡으로 먼저 물어보세요', 1)])
    c.y += 6; kakao_card(c); c.save(f'{o}/05.jpg')


if __name__ == '__main__':
    for fn in sys.argv[1:] or ['naver', 'google', 'tistory']:
        pass
    naver(); google(); tistory(); print('ok')
