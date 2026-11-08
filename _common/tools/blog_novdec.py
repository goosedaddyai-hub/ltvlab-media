# 블로그 이미지 3세트 — 11~12월 청약 편 (네이버=네이비 / 구글=틸 / 티스토리=퍼플), 서로 내용·디자인 중복 없음
import sys, os, types
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/blog_novdec'
from PIL import ImageFont
_fc = {}
def _F(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]
def _fit(d, text, path, size, maxw):
    while size > 20 and d.textlength(text, font=_F(path, size)) > maxw: size -= 2
    return _F(path, size)
stub = types.ModuleType('make_seizure')
stub.F, stub.fit = _F, _fit
stub.BLACK = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'; stub.BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
sys.modules['make_seizure'] = stub
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blog_seizure as B
from blog_seizure import Card, steps, table, kakao_card, F, fit, BLACK, BOLD, YEL, CORAL, WHITE, RED, GREEN

NAVYT = (20, 33, 61)


def bars(c, items, maxv, col, unit='가구', bh=64, gap=30, lw=200):
    """가로 막대: (라벨, 값, 강조여부)"""
    W_ = c.x1 - c.x0 - lw - 170
    for lab, v, em in items:
        y = c.y
        c.d.text((c.x0, y + 8), lab, font=fit(c.d, lab, BLACK, 36, lw - 10), fill=WHITE)
        w = max(16, int(W_ * v / maxv))
        c.d.rounded_rectangle((c.x0 + lw, y, c.x0 + lw + w, y + bh), 14, fill=col if em else (120, 135, 160))
        s = f'{v:,}{unit}'; c.d.text((c.x0 + lw + w + 16, y + 10), s, font=F(BLACK, 34), fill=col if em else c.t['sub'])
        c.y += bh + gap
    c.y += 10


# ================= 네이버 (네이비, 전체 단지 가이드) =================
def naver():
    o = f'{OUT}/naver'
    c = Card('naver', 800); c.y = 190
    c.chip('2026년 11~12월 청약', center=True)
    c.title([('올해 마지막 막차', 0), ('어디 넣을까?', 1)], 110, center=True)
    c.text('서울·경기·인천·지방 주요 단지 한 번에 정리', 40, center=True); c.save(f'{o}/00.jpg', fixed=True)

    c = Card('naver', 2200); c.chip('물량')
    c.title([('11월에만', 0), ('5만6,533가구', 1)])
    c.text('작년 11월(2만9,895가구)보다 89% 늘었어요', 30); c.y += 16
    bars(c, [('경기', 20278, 1), ('서울', 7240, 0), ('인천', 4499, 0), ('지방 전체', 24516, 1)], 24516, YEL)
    c.text('출처: 부동산R114 (2026.10.28 집계, 분양 예정 기준)', 24); c.save(f'{o}/01.jpg')

    c = Card('naver', 2200); c.chip('서울')
    c.title([('서울은 정비사업', 0), ('11월 → 12월 순서로', 1)])
    rows = [('11월', '디에이치 반포124', '서초 반포 · 일반 1,832'), ('11월', '경희궁 에피트', '종로 교남동 · 도심'),
            ('11월', '해링턴플레이스 문래', '영등포 · 218가구 전부 일반'), ('11월', '서초 롯데캐슬\n아트팰리스', '서초동 · 835가구'),
            ('12월', '용두동 롯데캐슬', '동대문 · 일반 340'), ('12월', '동선2구역 재개발', '성북 동선동'),
            ('12월', '남서울종합시장', '강남 대치동 · 일반 70')]
    table(c, ['', '단지', '포인트'], rows, [0.16, 0.42, 0.42], rh=104)
    c.text('※ 일정은 사업 상황에 따라 바뀔 수 있어요', 24); c.save(f'{o}/02.jpg')

    c = Card('naver', 2200); c.chip('경기·인천·지방')
    c.title([('수도권 밖까지', 0), ('주요 단지 체크', 1)])
    rows = [('의정부', '의정부역 펠리스타워\n양우내안애', '최고 49층 · 1,252가구'), ('인천 검단', '검단 센트레빌\n그랑포레', '843가구'),
            ('인천 송도', '송도 대광로제비앙\n모아엘가', '592가구'), ('세종', '세종스마트시티\n엘 수자인', '84㎡ 2,191가구\n전부 일반분양'),
            ('울산', '힐스테이트\n울산역리버포레', '84㎡ 436가구'), ('부산', '연산역 수자인\n센트리오', '일반 139가구')]
    table(c, ['', '단지', '규모'], rows, [0.2, 0.44, 0.36], rh=118)
    c.save(f'{o}/03.jpg')

    c = Card('naver', 2200); c.chip('자금', CORAL)
    c.title([('청약 넣기 전', 0), ('돈 체크 3가지', 1)])
    c.y += 10
    steps(c, [('계약금 현금', '보통 분양가의 10~20% · 대출 안 돼요'), ('중도금 대출 조건', '모집공고에서 집단대출 여부·이자후불 확인'),
              ('잔금대출 한도', '입주 때 시세·LTV·DSR로 다시 심사')], numcol=CORAL, h=140)
    c.text('당첨돼도 잔금 못 맞추면 계약금까지 위험해요', 30, col=WHITE); c.save(f'{o}/04.jpg')


# ================= 구글 (틸, 물량 데이터 분석) =================
def google():
    o = f'{OUT}/google'
    c = Card('google', 760); c.y += 60
    c.chip('2026년 11월 분양시장', center=True)
    c.title([('분양 5.6만 가구,', 0), ('어디에 몰렸나', 1)], 92, center=True)
    c.text('지역별 물량과 집계 기관별 차이 정리', 36, center=True); c.save(f'{o}/00.jpg', fixed=True)

    c = Card('google', 2200); c.chip('전년 대비')
    c.title([('작년 11월 vs', 0), ('올해 11월', 1)])
    c.y += 6
    bars(c, [('25년 11월', 29895, 0), ('26년 10월', 16396, 0), ('26년 11월', 56533, 1)], 56533, c.t['acc'], lw=220)
    c.text('전국 분양 예정 · 부동산R114 (2026.10.28)', 26); c.save(f'{o}/01.jpg')

    c = Card('google', 2200); c.chip('집계 차이')
    c.title([('R114 vs 직방', 0), ('숫자가 다른 이유', 1)])
    rows = [('전국 예정', '5만6,533가구', '4만4,358가구\n(60개 단지)'), ('비교 기준', '작년 11월 예정', '작년 11월 실제 분양'),
            ('증가율', '+89.1%', '+58%'), ('지방', '2만4,516가구', '2만4,507가구')]
    table(c, ['', '부동산R114', '직방'], rows, [0.24, 0.38, 0.38], rh=130)
    c.text('※ 집계 시점·포함 단지가 달라 숫자 차이가 나요', 26); c.save(f'{o}/02.jpg')

    c = Card('google', 2200); c.chip('지역 비중')
    c.title([('수도권 56.6%', 0), ('경기가 최다', 1)])
    c.y += 6
    bars(c, [('경기', 20278, 1), ('서울', 7240, 0), ('인천', 4499, 0), ('경북*', 6083, 0), ('부산*', 4567, 0), ('세종*', 3547, 0)], 20278, c.t['acc'])
    c.text('경기·서울·인천: R114 / *지방: 직방 집계', 24); c.save(f'{o}/03.jpg')

    c = Card('google', 2200); c.chip('체크리스트')
    c.title([('모집공고 열면', 0), ('이것부터 보세요', 1)])
    c.y += 10
    steps(c, [('청약 일정', '특별공급 → 1순위 → 2순위 → 당첨자 발표'), ('분양가·납부 일정', '계약금·중도금·잔금 비율과 날짜'),
              ('중도금 대출', '집단대출 알선 여부 · 이자후불제 여부'), ('전매·거주 조건', '전매제한·실거주 의무 기간')], numcol=(240, 205, 90), h=128)
    c.save(f'{o}/04.jpg')


# ================= 티스토리 (퍼플, 당첨 후 돈 흐름) =================
def tistory():
    o = f'{OUT}/tistory'
    c = Card('tistory', 740); c.y += 70
    c.chip('11~12월 청약 당첨자라면', center=True)
    c.title([('당첨부터 입주까지', 0), ('돈 흐름 한 장 정리', 1)], 90, center=True)
    c.text('계약금 · 중도금 · 잔금대출 체크리스트', 36, center=True); c.save(f'{o}/00.jpg', fixed=True)

    c = Card('tistory', 2200); c.chip('타임라인')
    c.title([('당첨 후', 0), ('돈 나가는 순서', 1)])
    c.y += 10
    ev = [('당첨 발표', '서류 제출', '자격 검증 · 부적격이면 취소'), ('계약', '계약금 납부', '보통 분양가의 10~20%, 현금'),
          ('공사 기간', '중도금 납부', '보통 60%, 집단대출로 나눠 냄'), ('입주', '잔금 + 중도금 상환', '잔금대출로 한 번에 정리'),
          ('입주 후', '등기 · 전입', '소유권이전 · 취득세 납부')]
    x = c.x0 + 40; d = c.d
    d.line((x, c.y + 20, x, c.y + 20 + 150 * (len(ev) - 1)), fill=c.t['acc'], width=6)
    for i, (dt, a, b) in enumerate(ev):
        yy = c.y + i * 150; col = RED if '잔금' in a else c.t['acc']
        d.ellipse((x - 18, yy + 2, x + 18, yy + 38), fill=col)
        d.text((x + 44, yy - 2), dt, font=F(BLACK, 30), fill=col)
        d.text((x + 240, yy - 6), a, font=F(BLACK, 38), fill=WHITE); d.text((x + 242, yy + 46), b, font=F(BOLD, 28), fill=c.t['sub'])
    c.y += 150 * len(ev); c.save(f'{o}/01.jpg')

    c = Card('tistory', 2200); c.chip('비교')
    c.title([('계약금·중도금·잔금', 0), ('뭘로 내나', 1)])
    rows = [('계약금', '내 현금', '대출 안 됨\n가장 먼저 준비'), ('중도금', '집단대출', '모집공고에서\n알선 여부 확인'),
            ('잔금', '잔금대출\n+ 내 돈', '입주 시점\n시세로 재심사')]
    table(c, ['', '재원', '주의'], rows, [0.24, 0.34, 0.42], rh=150)
    c.text('※ 비율·조건은 단지 모집공고마다 달라요', 26); c.save(f'{o}/02.jpg')

    c = Card('tistory', 2200); c.chip('잔금대출')
    c.title([('잔금대출 한도는', 0), ('이 4개로 정해져요', 1)])
    c.y += 10
    steps(c, [('입주 시점 시세', '분양가가 아니라 그때 감정·시세 기준'), ('지역 LTV', '규제지역 여부·주택 수에 따라 달라요'),
              ('DSR', '연소득 대비 연간 원리금 한도'), ('중도금 상환액', '잔금대출로 중도금부터 갚아요')], numcol=c.t['acc'], h=136)
    c.save(f'{o}/03.jpg')

    c = Card('tistory', 2200); c.chip('상담')
    c.title([('우리 단지 잔금 한도', 0), ('카톡으로 물어보세요', 1)])
    c.y += 6; kakao_card(c, secret=False); c.save(f'{o}/04.jpg')


if __name__ == '__main__':
    naver(); google(); tistory(); print('ok', OUT)
