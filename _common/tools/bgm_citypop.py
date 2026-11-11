# 'CityPop' BGM — 로즈 7th 코드 + 펑키 베이스 + 가벼운 드럼, 밝은 시티팝 그루브 (자체 합성, 저작권 없음)
# 사용: python3 bgm_citypop.py out.wav 총초 [seed] [BPM] [sfx 종류:초,...]  (4=팝 5=딩)
import sys, numpy as np, wave
from scipy.signal import butter, sosfilt

SR = 44100
out = sys.argv[1]; DUR = float(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7
BPM = float(sys.argv[4]) if len(sys.argv) > 4 else 104
SFX = [tuple(map(float, s.split(':'))) for s in (sys.argv[5].split(',') if len(sys.argv) > 5 and sys.argv[5] else [])]
rng = np.random.default_rng(seed)
beat = 60 / BPM; bar = beat * 4
N = int(SR * (DUR + 2))
L, R = np.zeros(N), np.zeros(N)
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)


def add(sig, t0, pan=0.0, g=1.0):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    L[i:i + n] += sig[:n] * g * np.sqrt(0.5 * (1 - pan)); R[i:i + n] += sig[:n] * g * np.sqrt(0.5 * (1 + pan))


def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)


def rhodes(m, dur, vel):
    n = int(SR * (dur + 0.4)); t = np.arange(n) / SR; f = mtof(m)
    s = np.sin(2 * np.pi * f * t + 1.2 * np.exp(-t * 6) * np.sin(2 * np.pi * f * 2 * t))
    s += 0.25 * np.sin(2 * np.pi * f * 3 * t) * np.exp(-t * 4)
    e = np.minimum(t / 0.004, 1) * np.exp(-t / 1.1); e[int(SR * dur):] *= np.exp(-np.arange(n - int(SR * dur)) / SR / 0.12)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    return s * e * trem * vel


def bass(m, dur, vel):
    n = int(SR * dur); t = np.arange(n) / SR; f = mtof(m)
    s = np.tanh(2.2 * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)))
    return s * np.minimum(t / 0.003, 1) * np.exp(-t / 0.35) * vel


def kick():
    n = int(SR * .35); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (50 * t + 90 * (1 - np.exp(-t * 30)) / 30)) * np.exp(-t * 9)


hp = butter(2, 6000, 'hp', fs=SR, output='sos'); bp = butter(2, [900, 5000], 'bp', fs=SR, output='sos')
def hat(o=False):
    n = int(SR * (.25 if o else .05)); return sosfilt(hp, rng.standard_normal(n)) * np.exp(-np.arange(n) / SR / (.08 if o else .015))
def snare():
    n = int(SR * .25); t = np.arange(n) / SR
    return (sosfilt(bp, rng.standard_normal(n)) * np.exp(-t * 18) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25))


# 키 랜덤(seed) — Fmaj7 계열 진행: IVmaj7 - iii7 - vi7 - V7sus (Just the two of us 아님, 단순 다이어토닉)
root = 60 + int(rng.integers(-3, 4))
prog = [[5, 9, 12, 16], [4, 7, 11, 14], [-3, 0, 4, 7], [2, 7, 9, 12]]   # 상대 반음
bassr = [5, 4, -3, 2]
t = 0.0; k = 0
while t < DUR + 1:
    ch = prog[k % 4]; b = root - 24 + bassr[k % 4]
    for hit, ln in ((0, 1.4), (1.5, .4), (2.5, 1.2)):      # 싱코페이션 코드 컴핑
        for j, n_ in enumerate(ch): add(rhodes(root + n_ - 12, ln * beat, .16 + .03 * rng.random()), t + hit * beat + j * 0.008, pan=-.3 + .2 * j)
    for p, (off, ln, oc) in enumerate(((0, .9, 0), (1, .4, 12), (1.75, .4, 0), (2.5, .9, 0), (3.5, .4, 7))):
        add(bass(b + oc, ln * beat, .32), t + off * beat)
    for q in range(4):
        add(kick(), t + q * beat, g=.55 if q % 2 == 0 else .35)
        if q % 2: add(snare(), t + q * beat, g=.32)
        for e8 in range(2): add(hat(e8 == 1 and q == 3), t + q * beat + e8 * beat / 2, pan=.3, g=.10 + .04 * e8)
    t += bar; k += 1

for kind, ts in SFX:          # 4=팝 5=딩
    if kind == 4:
        n = int(SR * .12); tt = np.arange(n) / SR; add(np.sin(2 * np.pi * (900 - 2500 * tt) * tt) * np.exp(-tt * 40), ts, g=.35)
    elif kind == 5:
        n = int(SR * .8); tt = np.arange(n) / SR; add((np.sin(2 * np.pi * 1568 * tt) + .4 * np.sin(2 * np.pi * 2352 * tt)) * np.exp(-tt * 5), ts, g=.22)

n = int(SR * DUR); mix = np.stack([L[:n], R[:n]], 1)
fi, fo = int(SR * .05), int(SR * 1.5)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]; mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.3) * 0.8
w = wave.open(out, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
