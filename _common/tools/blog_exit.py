# 블로그 이미지 3세트 — 퇴거자금·2027 비거주 1주택 편 (네이버=네이비 / 구글=틸 / 티스토리=퍼플), 서로 내용·디자인 중복 없음
import sys, os, types
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/blog_exit'
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

NAVYT = (20, 33, 61)


def pm(P, r, n=360):
    r /= 1200; return P * r / (1 - (1 + r) ** -n)
def need(dep_eok, rate):   # DSR 40% 필요 연소득(만원)
    return pm(dep_eok * 1e8, rate) * 12 / 0.4 / 1e4
def man(v):
    v = int(round(v / 10) * 10); e, m = divmod(v, 10000)
    return (f'{e}억 ' if e else '') + (f'{m:,}만' if m else '')


# ================= 네이버 (네이비, 영상 내용 풀버전: 청구3차 케이스) =================
def naver():
    o = f'{OUT}/naver'
    c = Card('naver', 800); c.y = 190
    c.chip('2027.1.1부터 달라지는 것', center=True)
    c.title([('세입자 내보내야 하는데', 0), ('은행은 1억만?', 1)], 100, center=True)
    c.text('노원 중계 청구3차로 직접 계산해봤어요', 40, center=True); c.save(f'{o}/00.jpg', fixed=True)

    c = Card('naver', 2200); c.chip('8·13 대책', CORAL)
    c.title([('비거주 1주택자', 0), ('전세대출 막혀요', 1)])
    steps(c, [('수도권·규제지역 아파트 1채', '부부 합산 1주택'), ('그 집은 세를 줬고', '직계 가족에게 준 건 제외'),
              ('부부 둘 다 산 적 없음', '전입 이력 한 번도 없음')], numcol=CORAL, h=130)
    c.text('3개 모두 해당하면 전세대출 신규·연장 X', 34, col=WHITE); c.save(f'{o}/01.jpg')

    c = Card('naver', 2200); c.chip('지역별 한도')
    c.title([('우리 동네', 0), ('퇴거자금 얼마까지?', 1)])
    table(c, ['', '퇴거자금 상한', 'LTV'], [('서울 전역\n경기 규제지역', '원칙 1억', '40%'), ('인천·경기\n나머지', '원칙 1억', '70%'),
                                           ('지방', '상한 없음\n보증금까지', '70%')], [0.34, 0.36, 0.30], rh=130)
    c.text('1주택자 기준 · 규제지역: 서울·과천·분당·광명·하남·동탄·구리 등', 26); c.save(f'{o}/02.jpg')

    c = Card('naver', 2200); c.chip('예외', (52, 210, 140))
    c.title([('예전 계약이면', 0), ('1억 넘게 가능', 1)])
    steps(c, [('세입자 계약 2025.6.27 이전', '지금 세입자와의 최초 임대차 계약'), ('내가 산 날도 6.27 이전', '매매계약 또는 소유권 이전등기'),
              ('둘 다 OK → 1억 초과 + LTV 70%', '하나라도 이후면 1억 · LTV 40%')], numcol=(52, 210, 140), h=130)
    c.save(f'{o}/03.jpg')

    c = Card('naver', 2200); c.chip('실제 계산')
    c.title([('중계 청구3차 84㎡', 0), ('같은 집, 7억 차이', 1)])
    table(c, ['', '예전 계약', '6.27 이후'], [('돌려줄 보증금', '8억', '8억'), ('LTV 한도', '9억 7,650만\n(70%)', '1억 상한'),
                                         ('받을 수 있는 돈', '8억 전액', '1억'), ('부족한 돈', '0원', '7억')], [0.34, 0.33, 0.33], rh=118)
    c.text('KB시세 13억 9,500만(2026.10) · 보증금 8억 가정 · DSR 별도', 26); c.save(f'{o}/04.jpg')

    c = Card('naver', 2200); c.chip('은행 조건', CORAL)
    c.title([('예전 계약도', 0), ('조건은 깐깐해요', 1)])
    steps(c, [('내 돈으로 못 돌려줄 때만', "'자력 반환 불가' 확인"), ('1개월 내 전입 + 2년 거주', '들어가 살 거면 실거주 의무'),
              ('돈은 세입자에게 직접', '보증금 반환 외 사용 금지'), ('DSR 40% 통과', '8억이면 연소득 약 1.2억 필요')], numcol=CORAL, h=124)
    c.save(f'{o}/05.jpg')


# ================= 구글 (틸, 규제 타임라인 + DSR 계산표) =================
def google():
    o = f'{OUT}/google'
    c = Card('google', 760); c.y += 60
    c.chip('전세퇴거자금대출 규제 흐름', center=True)
    c.title([('6·27부터 2027년까지', 0), ('한눈에 보는 타임라인', 1)], 84, center=True)
    c.text('규제 시점별 변화 + 보증금별 필요 연소득 계산', 34, center=True); c.save(f'{o}/00.jpg', fixed=True)

    c = Card('google', 2200); c.chip('타임라인')
    c.title([('퇴거자금 규제', 0), ('이렇게 쌓였어요', 1)])
    ev = [('2025.6.28', '6·27 대책', '수도권·규제지역 생활안정자금 주담대 최대 1억'),
          ('2025.10.16', '10·15 대책', '서울 전역·경기 12곳 규제지역, LTV 40%'),
          ('2025.10.16', '스트레스 DSR', '수도권·규제지역 하한 1.5% → 3.0%'),
          ('2026.7.1', '규제지역 추가', '화성 동탄구·용인 기흥구·구리시'),
          ('2026.8.13', '8·13 대책', '1억 한도·반환대출 규제는 유지'),
          ('2027.1.1', '시행', '비거주 1주택 전세대출 제한 등')]
    x = c.x0 + 30; d = c.d
    d.line((x, c.y + 20, x, c.y + 20 + 140 * (len(ev) - 1)), fill=c.t['acc'], width=6)
    for i, (dt, a, b) in enumerate(ev):
        yy = c.y + i * 140; col = (240, 205, 90) if dt.startswith('2027') else c.t['acc']
        d.ellipse((x - 16, yy + 4, x + 16, yy + 36), fill=col)
        d.text((x + 40, yy - 2), dt, font=F(BLACK, 30), fill=col)
        d.text((x + 260, yy - 6), a, font=F(BLACK, 38), fill=WHITE); d.text((x + 262, yy + 46), b, font=fit(d, b, BOLD, 28, c.x1 - x - 270), fill=c.t['sub'])
    c.y += 140 * len(ev); c.save(f'{o}/01.jpg')

    c = Card('google', 2200); c.chip('DSR 계산')
    c.title([('보증금별', 0), ('필요 연소득은?', 1)])
    rows = [(f'{e}억', man(need(e, 4.4)), man(need(e, 5.9))) for e in (1, 3, 5, 8)]
    table(c, ['퇴거자금', '금리 4.4%', '4.4%+1.5%p'], rows, [0.28, 0.36, 0.36], rh=104)
    c.text('30년 원리금균등 · DSR 40% · 다른 대출 0 단순 계산', 26); c.save(f'{o}/02.jpg')

    c = Card('google', 2200); c.chip('2027.1.1 시행')
    c.title([('내년부터', 0), ('바뀌는 4가지', 1)])
    steps(c, [('비거주 1주택자 전세대출 제한', '수도권·규제지역 아파트 · 실거주 이력 없으면'), ('1주택자 전세보증비율 축소', '수도권·규제 80→70% · 그 외 90→80%'),
              ('DSR 소득 산정 변경', '소득 20%↑ 2년 평균 · 30%↑ 3년 평균'), ('고위험 주담대 위험가중치↑', '은행 대출 여력에 영향')], numcol=(240, 205, 90), h=128)
    c.save(f'{o}/03.jpg')

    c = Card('google', 2200); c.chip('체크리스트')
    c.title([('상담 전에', 0), ('이 서류부터', 1)])
    steps(c, [('임대차계약서', '최초 계약일이 2025.6.27 이전인지'), ('매매계약서·등기부등본', '취득일(계약·등기) 확인'),
              ('소득 증빙 2~3년치', '2027년부터 평균 소득 적용 가능'), ('기존 대출 내역', 'DSR 계산에 모두 합산')], numcol=c.t['acc'], h=124)
    c.save(f'{o}/04.jpg')


# ================= 티스토리 (퍼플, 비거주 1주택 자가진단 + 예외) =================
def tistory():
    o = f'{OUT}/tistory'
    c = Card('tistory', 740); c.y += 70
    c.chip('2027년 1월 시행 전 체크', center=True)
    c.title([('내 전세대출,', 0), ('내년에 막힐까?', 1)], 92, center=True)
    c.text('비거주 1주택자 자가진단 + 예외 5가지', 36, center=True); c.save(f'{o}/00.jpg', fixed=True)

    c = Card('tistory', 2200); c.chip('자가진단')
    c.title([('3개 다 YES면', 0), ('제한 대상이에요', 1)])
    qs = [('Q1', '수도권·규제지역 아파트 1채를 갖고 있나요?', '부부 합산 기준'),
          ('Q2', '그 집을 남에게 세 줬나요?', '부모·자녀 등 직계 가족에게 준 건 제외'),
          ('Q3', '부부 둘 다 그 집에 산 적이 없나요?', '한 번이라도 전입했으면 제외')]
    for q, a, b in qs:
        d = c.d; y0 = c.y
        d.rounded_rectangle((c.x0, y0, c.x1, y0 + 150), 22, fill=WHITE)
        d.rounded_rectangle((c.x0 + 24, y0 + 40, c.x0 + 114, y0 + 110), 18, fill=c.t['acc'])
        d.text((c.x0 + 40, y0 + 46), q, font=F(BLACK, 40), fill=(40, 26, 58))
        d.text((c.x0 + 140, y0 + 30), a, font=fit(d, a, BLACK, 36, c.x1 - c.x0 - 170), fill=(40, 26, 58))
        d.text((c.x0 + 142, y0 + 90), b, font=F(BOLD, 28), fill=(110, 100, 130)); c.y += 170
    c.text('→ 전세대출 신규·만기연장 원칙 금지 (2027.1.1~)', 32, col=WHITE); c.save(f'{o}/01.jpg')

    c = Card('tistory', 2200); c.chip('예외')
    c.title([('대상이어도', 0), ('되는 경우 5가지', 1)])
    rows = [('토허구역 세 낀 집 매수 등\n법적 실거주 예정', '신규·연장'), ('임대차 승계 조건 매수\n기존 계약 안 끝남', '승계 계약\n종료일까지 연장'),
            ('집주인이 보증금 미반환', '연장'), ('퇴거 예정인데\n이사 일정 조정', '단기 연장\n(예: 6개월)'), ('여신심사위원회가\n불가피성 인정', '신규·연장')]
    table(c, ['사유', '허용 범위'], rows, [0.62, 0.38], rh=116)
    c.text('출처: 금융위 부동산 시장 안정 금융 종합대책', 24); c.save(f'{o}/02.jpg')

    c = Card('tistory', 2200); c.chip('대응')
    c.title([('해당된다면', 0), ('선택지는 3개', 1)])
    steps(c, [('내 집으로 들어가기', '세입자 보증금 → 퇴거자금 필요 (수도권 원칙 1억)'), ('예외 사유 확인', '승계 계약·보증금 미반환 등 서류 준비'),
              ('은행 여신심사 문의', '불가피한 비거주 사유면 개별 심사')], numcol=c.t['acc'], h=136)
    c.save(f'{o}/03.jpg')

    c = Card('tistory', 2200); c.chip('상담')
    c.title([('우리 집 퇴거자금 한도', 0), ('카톡으로 물어보세요', 1)])
    c.y += 6; kakao_card(c, secret=False); c.save(f'{o}/04.jpg')


if __name__ == '__main__':
    for s in ('naver', 'google', 'tistory'): os.makedirs(f'{OUT}/{s}', exist_ok=True)
    naver(); google(); tistory(); print('ok', OUT)
