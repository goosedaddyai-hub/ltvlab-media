# 네이버 블로그 이미지 — 잠실 래미안아이파크 계약취소 3가구 줍줍 (2026-11-18, 네이비)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blog_exit  # noqa: F401  (폰트 스텁 세팅)
from blog_seizure import Card, steps, table, kakao_card, CORAL, WHITE, RED

OUT = '/home/claude/blog_jamsil'
GREEN = (52, 210, 140)


def naver():
    o = f'{OUT}/naver'; os.makedirs(o, exist_ok=True)
    c = Card('naver', 800); c.y = 190
    c.chip('11/23 무순위 청약', center=True)
    c.title([('잠실 신축 84㎡가', 0), ('18억에 줍줍?', 1)], 100, center=True)
    c.text('잠실 래미안아이파크 계약취소 3가구 총정리', 40, center=True); c.save(f'{o}/00.jpg', fixed=True)

    c = Card('naver', 2200); c.chip('분양가 vs 시세')
    c.title([('3가구 분양가', 0), ('차익 12~24억', 1)])
    table(c, ['주택형', '분양가', '최근 거래'], [('43㎡\n일반 1가구', '11억 548만', '23억 8천\n(+12.7억)'),
                                            ('59㎡A\n일반 1가구', '15억 7,939만', '32억 7천\n(+16.9억)'),
                                            ('84㎡D\n신혼특공 1가구', '18억 5,607만', '입주권 43억\n(+24억)')], [0.30, 0.34, 0.36], rh=130)
    c.text('분양가상한제 단지라 최초 분양가 그대로 재공급', 28); c.save(f'{o}/01.jpg')

    c = Card('naver', 2200); c.chip('자격', CORAL)
    c.title([('누가 넣을 수 있어요?', 0), ('서울 무주택만', 1)])
    steps(c, [('일반공급 43·59㎡', '서울 거주 무주택 세대주 · 소득·자산 기준 없음'),
              ('신혼부부 특공 84㎡', '혼인 7년 이내 · 서울 무주택 가구원'),
              ('조건 되면 전부 추첨', '가점·소득 순위 없이 1가구씩')], numcol=CORAL, h=130)
    c.save(f'{o}/02.jpg')

    c = Card('naver', 2200); c.chip('일정')
    c.title([('다음 주라', 0), ('놓치면 끝', 1)])
    steps(c, [('11/23(월) 특별공급', '84㎡D 신혼부부 1가구'), ('11/24(화) 일반공급', '43㎡ · 59㎡A 각 1가구'),
              ('11/27 발표 → 12/4 계약', '2027년 1월 입주 예정')], h=130)
    c.text('실거주 2년 · 전매제한 3년 · 재당첨 제한 10년', 30, col=WHITE); c.save(f'{o}/03.jpg')

    c = Card('naver', 2200); c.chip('함정', RED)
    c.title([('계약금 30%에', 0), ('은행 대출은 막혀요', 1)])
    table(c, ['84㎡ 당첨 시', '금액'], [('총액(확장·옵션 포함)', '18억 7,879만'), ('계약금 30%', '약 5억 6,364만'),
                                       ('전세 12억 받는다고 가정', '- 12억'), ('내 현금 필요', '약 6억 7,879만')], [0.56, 0.44], rh=112)
    c.text('+ 취득세 별도 · 미등기라 일반 주담대 어려움', 28); c.save(f'{o}/04.jpg')

    c = Card('naver', 2200); c.chip('LTV연구소에서는', GREEN)
    c.title([('은행은 막혀도', 0), ('매매자금 최대 65%', 1)])
    c.text('당첨되면 잔금 현금 부족분부터 미리 계산해두세요', 32, col=WHITE)
    c.y += 10; kakao_card(c, secret=False)
    c.text('소득·신용·심사 조건에 따라 한도는 달라요', 26); c.save(f'{o}/05.jpg')


if __name__ == '__main__':
    naver(); print('ok', OUT)
