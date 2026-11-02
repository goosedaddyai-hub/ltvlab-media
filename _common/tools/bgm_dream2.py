# 드림코어 BGM v2 — 첫 박부터 바로 들어가는 버전 (자체 작곡, 저작권 없음)
# 사용: python3 bgm_dream2.py out.wav 초 [seed]
import sys, numpy as np, wave
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
out = sys.argv[1]; DUR = float(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 5
rng = np.random.default_rng(seed)
BPM = 90.0; beat = 60 / BPM; bar = beat * 4
N = int(SR * (DUR + 4))
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
# 버스: 신스(리버브 많이) / 드럼(리버브 조금)
SL, SR_ = np.zeros(N), np.zeros(N); DL, DR = np.zeros(N), np.zeros(N)

def add(sig, t0, pan=0.0, bus='s'):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    a, b = (SL, SR_) if bus == 's' else (DL, DR)
    a[i:i + n] += sig[:n] * np.sqrt(0.5 * (1 - pan)); b[i:i + n] += sig[:n] * np.sqrt(0.5 * (1 + pan))

def pad(m, dur, vel):
    n = int(SR * (dur + 1.2)); t = np.arange(n) / SR; f = mtof(m); s = np.zeros(n)
    for d in (-0.12, -0.05, 0.05, 0.12):  # 디튠 쏘우 느낌(배음 몇 개)
        ff = f * 2 ** (d / 12); ph = rng.uniform(0, 6.28)
        for k, a in ((1, 1), (2, .45), (3, .25), (4, .12)):
            s += a * np.sin(2 * np.pi * ff * k * t + ph * k)
    env = np.minimum(1, t / 0.06) * np.where(t > dur, np.exp(-(t - dur) * 3), 1)   # 어택 빠르게
    return s * env * vel / 6

def bell(m, vel):
    n = int(SR * 2.2); t = np.arange(n) / SR; f = mtof(m)
    s = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 4)
         + 0.3 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 6) + 0.15 * np.sin(2 * np.pi * f * 4.2 * t) * np.exp(-t * 9))
    return s * np.minimum(1, t / 0.002) * np.exp(-t * 2.2) * vel

def vox(m, dur, vel):
    """'우~' 하는 보컬 찹 느낌: 포먼트 비슷하게 배음 강조 + 비브라토"""
    n = int(SR * (dur + .4)); t = np.arange(n) / SR; f = mtof(m) * (1 + 0.006 * np.sin(2 * np.pi * 5.2 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(a * np.sin(k * ph) for k, a in ((1, 1), (2, .6), (3, .35), (4, .5), (5, .2)))
    env = np.minimum(1, t / 0.03) * np.where(t > dur, np.exp(-(t - dur) * 10), 1)
    return s * env * vel / 2.6

def kick(vel=0.9):
    n = int(SR * .45); t = np.arange(n) / SR
    f = 48 + 90 * np.exp(-t * 28); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return (s + 0.15 * rng.standard_normal(n) * np.exp(-t * 120)) * vel

def snare(vel=0.45):
    n = int(SR * .35); t = np.arange(n) / SR
    nz = sosfilt(butter(2, [900, 7000], 'band', fs=SR, output='sos'), rng.standard_normal(n))
    return (nz * np.exp(-t * 14) + 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 20)) * vel

def hat(vel=0.12, open_=False):
    n = int(SR * (.25 if open_ else .06)); t = np.arange(n) / SR
    nz = sosfilt(butter(2, 7500, 'high', fs=SR, output='sos'), rng.standard_normal(n))
    return nz * np.exp(-t * (14 if open_ else 70)) * vel

def sub(m, dur, vel=0.28):
    n = int(SR * (dur + .2)); t = np.arange(n) / SR; f = mtof(m)
    return np.sin(2 * np.pi * f * t) * np.minimum(1, t / .01) * np.where(t > dur, np.exp(-(t - dur) * 20), 1) * vel

# 진행: Dbmaj9 – Cm7 – Bbm9 – Ab(add9) 계열(반음 낮춰 몽환)
prog = [(49, [61, 65, 68, 72, 75]), (48, [60, 63, 67, 70, 74]), (46, [58, 61, 65, 68, 72]), (44, [56, 60, 63, 67, 70])]
arps = [[73, 77, 80, 84], [72, 75, 79, 82], [70, 73, 77, 80], [68, 72, 75, 79]]
hook = [[80, 82, 84, 82], [79, 77, 75, 77], [77, 75, 73, 72], [75, 77, 79, 80]]
t0 = 0.0; k = 0
while t0 < DUR + 1:
    root, ch = prog[k % 4]
    for j, m in enumerate(ch): add(pad(m, bar * .97, .085), t0, pan=(j - 2) * .3)
    # 베이스: 8분 쉼표 뒤 당김
    for b_ in (0, 1.5, 2, 3.5): add(sub(root - 12, beat * .45), t0 + b_ * beat, bus='d')
    # 종소리 16분 아르페지오 — 첫 박부터
    a = arps[k % 4]
    for j in range(16):
        m = a[j % 4] + (12 if j % 8 == 7 else 0)
        add(bell(m, .055 + .02 * (j % 4 == 0)), t0 + j * beat / 4 + rng.normal(0, .004), pan=.5 * np.sin(j))
    # 보컬 찹 훅(2마디마다 다르게)
    hk = hook[k % 4]
    for j, m in enumerate(hk): add(vox(m, beat * .42, .06), t0 + (j * 0.75 + (0.5 if j % 2 else 0)) * beat, pan=-.2 + .4 * (j % 2))
    # 드럼: 첫 마디부터 (킥 1·2.5·3, 스네어 2·4, 하이햇 8분 + 마지막 오픈)
    for b_ in (0, 1.5, 2.5): add(kick(.85 if b_ == 0 else .7), t0 + b_ * beat, bus='d')
    for b_ in (1, 3): add(snare(), t0 + b_ * beat, bus='d')
    for j in range(8): add(hat(.1 if j % 2 else .06, open_=(j == 7)), t0 + j * beat / 2, pan=.25, bus='d')
    t0 += bar; k += 1

# 사이드체인(킥 박마다 신스 볼륨 살짝 눌렀다 올림) → 펌핑감
tt = np.arange(N) / SR; ph = (tt % beat) / beat
duck = 1 - 0.38 * np.exp(-ph * 9)
SL *= duck; SR_ *= duck
# 리버브(신스만 길게)
ir_n = int(SR * 2.6); it = np.arange(ir_n) / SR
lp = butter(2, 6000, 'low', fs=SR, output='sos')
irL = sosfilt(lp, rng.standard_normal(ir_n) * np.exp(-it * 2.0)); irR = sosfilt(lp, rng.standard_normal(ir_n) * np.exp(-it * 2.0))
irL /= np.abs(irL).sum() ** .5 * 6; irR /= np.abs(irR).sum() ** .5 * 6
wL = fftconvolve(SL, irL)[:N]; wR = fftconvolve(SR_, irR)[:N]
dirL = fftconvolve(DL, irL * .25)[:N]; dirR = fftconvolve(DR, irR * .25)[:N]
L = .7 * SL + .8 * wL + DL + .5 * dirL; R = .7 * SR_ + .8 * wR + DR + .5 * dirR
# 로파이 질감: 아주 약한 테이프 노이즈 + 고역 살짝 깎기
hiss = sosfilt(butter(2, [2500, 9000], 'band', fs=SR, output='sos'), rng.standard_normal(N)) * .002
L = sosfilt(butter(2, 12000, 'low', fs=SR, output='sos'), L) + hiss; R = sosfilt(butter(2, 12000, 'low', fs=SR, output='sos'), R) + hiss
n = int(SR * DUR); mix = np.stack([L[:n], R[:n]], 1)
mix[:int(SR * .02)] *= np.linspace(0, 1, int(SR * .02))[:, None]   # 클릭 방지만, 바로 시작
mix = np.tanh(mix / np.abs(mix).max() * 1.4) ; mix /= np.abs(mix).max() / .9
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok', out, DUR)
