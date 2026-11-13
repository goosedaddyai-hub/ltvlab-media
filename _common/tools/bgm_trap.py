# 'Trap' BGM — 마이너 벨 피아노 + 808 글라이드 + 트랩 하이햇 롤(하프타임), 긴장감 있는 정보형 (자체 합성, 저작권 없음)
# 사용: python3 bgm_trap.py out.wav 총초 [seed] [BPM] [sfx 종류:초,...]  (1=도장 4=팝 5=딩)
import sys, numpy as np, wave
from scipy.signal import butter, sosfilt

SR = 44100
out = sys.argv[1]; DUR = float(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 3
BPM = float(sys.argv[4]) if len(sys.argv) > 4 else 140
SFX = [tuple(map(float, s.split(':'))) for s in (sys.argv[5].split(',') if len(sys.argv) > 5 and sys.argv[5] else [])]
rng = np.random.default_rng(seed)
beat = 60 / BPM; bar = beat * 4
N = int(SR * (DUR + 3))
L, R = np.zeros(N), np.zeros(N)
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)


def add(sig, t0, pan=0.0, g=1.0):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    L[i:i + n] += sig[:n] * g * np.sqrt(0.5 * (1 - pan)); R[i:i + n] += sig[:n] * g * np.sqrt(0.5 * (1 + pan))


def bell(m, dur, vel):
    n = int(SR * (dur + 0.8)); t = np.arange(n) / SR; f = mtof(m)
    s = np.sin(2 * np.pi * f * t + 2.0 * np.exp(-t * 5) * np.sin(2 * np.pi * f * 3.5 * t))
    s += 0.3 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 3)
    return s * np.minimum(t / 0.003, 1) * np.exp(-t / 0.9) * vel


def pad(ms, dur, vel):
    n = int(SR * dur); t = np.arange(n) / SR; s = np.zeros(n)
    for m in ms:
        for dt in (-0.12, 0.12):
            ph = 2 * np.pi * mtof(m + dt) * t; s += (2 * ((ph / (2 * np.pi)) % 1) - 1)
    s = sosfilt(butter(2, 1400, 'lp', fs=SR, output='sos'), s)
    e = np.minimum(t / 0.4, 1) * np.minimum((dur - t) / 0.4, 1)
    return s * e * vel / len(ms)


def b808(m, m2, dur, vel):
    n = int(SR * dur); t = np.arange(n) / SR
    f = mtof(m) + (mtof(m2) - mtof(m)) * np.clip((t - dur * 0.55) / (dur * 0.25), 0, 1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.tanh(2.5 * np.sin(ph)) + 0.2 * np.sin(2 * ph)
    pk = np.sin(2 * np.pi * 120 * t) * np.exp(-t * 60)
    return (s * np.minimum(t / 0.004, 1) * np.exp(-t / 1.4) + pk) * vel


def kick():
    n = int(SR * .3); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (45 * t + 110 * (1 - np.exp(-t * 35)) / 35)) * np.exp(-t * 12)


hp = butter(2, 7000, 'hp', fs=SR, output='sos'); bp = butter(2, [1000, 6000], 'bp', fs=SR, output='sos')
def hat(o=False):
    n = int(SR * (.2 if o else .04)); return sosfilt(hp, rng.standard_normal(n)) * np.exp(-np.arange(n) / SR / (.06 if o else .012))
def clap():
    n = int(SR * .3); t = np.arange(n) / SR; nz = sosfilt(bp, rng.standard_normal(n))
    e = np.exp(-t * 14) + sum(np.exp(-np.maximum(t - d, 0) * 120) * (t >= d) * .6 for d in (0, .011, .022))
    return nz * e * 0.6


root = 50 + int(rng.integers(-2, 3))           # D 단조 근처
prog = [[0, 3, 7], [-4, 0, 3], [-2, 2, 5], [-5, -2, 2]]    # i - VI - VII - v
bassr = [0, -4, -2, -5]
mel = [[12, 15, 14, 10], [12, 8, 10, 7], [14, 10, 12, 15], [10, 7, 9, 7]]
t = 0.0; k = 0
while t < DUR + 2:
    ch = prog[k % 4]; b = root - 12 + bassr[k % 4]; intro = k == 0
    add(pad([root + 12 + n_ for n_ in ch], bar, .22), t)
    for j, mm in enumerate(mel[k % 4]):
        add(bell(root + 12 + mm, beat * .9, .17 if not intro else .12), t + j * beat, pan=.25 * (-1) ** j)
    nb = b808(b, b + (bassr[(k + 1) % 4] - bassr[k % 4]), bar * .9, .42)
    if not intro:
        add(nb, t); add(kick(), t, g=.6); add(kick(), t + beat * 2.5, g=.45)
        add(clap(), t + beat * 2, g=.5)
        roll = (k % 2 == 1)
        for s16 in range(16):
            if roll and s16 >= 12:   # 마지막 박 32분 롤
                for r in range(2): add(hat(), t + (s16 + r / 2) * beat / 4, pan=.35, g=.09)
            elif s16 % 2 == 0 or rng.random() < .25:
                add(hat(s16 == 14 and not roll), t + s16 * beat / 4, pan=.35, g=.11 if s16 % 4 == 0 else .08)
    else:
        add(nb, t, g=.5)
    t += bar; k += 1

for kind, ts in SFX:          # 1=도장 4=팝 5=딩
    if kind == 1:
        n = int(SR * .35); tt = np.arange(n) / SR
        add(np.sin(2 * np.pi * (70 + 120 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14) + .3 * sosfilt(bp, rng.standard_normal(n)) * np.exp(-tt * 30), ts, g=.55)
    elif kind == 4:
        n = int(SR * .12); tt = np.arange(n) / SR; add(np.sin(2 * np.pi * (900 - 2500 * tt) * tt) * np.exp(-tt * 40), ts, g=.35)
    elif kind == 5:
        n = int(SR * .8); tt = np.arange(n) / SR; add((np.sin(2 * np.pi * 1568 * tt) + .4 * np.sin(2 * np.pi * 2352 * tt)) * np.exp(-tt * 5), ts, g=.22)

n = int(SR * DUR); mix = np.stack([L[:n], R[:n]], 1)
fi, fo = int(SR * .05), int(SR * 1.5)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]; mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.4) * 0.8
w = wave.open(out, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
