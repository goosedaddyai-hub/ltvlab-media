# 'Marimba' BGM — 밝은 트로피컬 하우스(마림바 리프·서브베이스·클랩·셰이커), 연말 축제 느낌 (자체 합성, 저작권 없음)
# 사용: python3 bgm_marimba.py out.wav 총초 [seed] [BPM]
import sys, numpy as np, wave
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
out = sys.argv[1]; DUR = float(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 5
BPM = float(sys.argv[4]) if len(sys.argv) > 4 else 108.0
rng = np.random.default_rng(seed)
beat = 60 / BPM; s16 = beat / 4; bar = beat * 4
N = int(SR * (DUR + 2))
L, R = np.zeros(N), np.zeros(N); VL, VR = np.zeros(N), np.zeros(N)
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)


def add(sig, t0, pan=0.0, verb=0.0):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0: return
    l, r = np.sqrt(.5 * (1 - pan)), np.sqrt(.5 * (1 + pan))
    L[i:i + n] += sig[:n] * l; R[i:i + n] += sig[:n] * r
    if verb: VL[i:i + n] += sig[:n] * l * verb; VR[i:i + n] += sig[:n] * r * verb


def marimba(m, vel):
    f = mtof(m); n = int(SR * .9); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + .35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30) \
        + .12 * np.sin(2 * np.pi * f * 9.9 * t) * np.exp(-t * 60)
    s[:40] *= np.linspace(0, 1, 40)
    return s * vel


def bass(m, dur):
    f = mtof(m); n = int(SR * dur); t = np.arange(n) / SR
    env = np.minimum(1, t / .01) * np.exp(-t * 2.2); env[-300:] *= np.linspace(1, 0, 300)
    return (np.sin(2 * np.pi * f * t) + .25 * np.sin(4 * np.pi * f * t)) * env * .55


def kick():
    n = int(SR * .35); t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * .9


def clap():
    n = int(SR * .25); t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    env = sum(np.exp(-np.maximum(0, t - d) * 60) * (t >= d) for d in (0, .011, .022)) * np.exp(-t * 14)
    return sosfilt(butter(2, [900, 5000], 'band', fs=SR, output='sos'), nz) * env * .55


def shaker(v):
    n = int(SR * .07); t = np.arange(n) / SR
    return sosfilt(butter(2, 6500, 'high', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t * 70) * v


def pad(ms, dur):
    n = int(SR * dur); t = np.arange(n) / SR; s = np.zeros(n)
    for m in ms:
        for dt in (-0.08, 0.08):
            s += np.sin(2 * np.pi * mtof(m + dt) * t)
    env = np.minimum(1, t / .4) * np.minimum(1, (dur - t) / .4)
    return s * env * .035


# I–V–vi–IV in F major (밝고 신나는 진행)
CH = [(53, [65, 69, 72]), (60, [64, 67, 72]), (62, [65, 69, 74]), (58, [62, 65, 70])]
RIFF = [0, None, 2, 1, None, 2, 0, None, 1, None, 2, None, 0, 1, None, 2]   # 화음 구성음 인덱스
K, C = kick(), clap()
nb = int(DUR / bar) + 1
for b in range(nb):
    root, ch = CH[b % 4]; t0 = b * bar
    intro = t0 < bar * 1          # 첫 마디는 마림바+패드만(훅 대사 살리기)
    add(pad(ch, bar), t0, verb=.4)
    for k, idx in enumerate(RIFF):
        if idx is None: continue
        m = ch[idx] + (12 if (b % 2 and k in (6, 14)) else 0)
        add(marimba(m, .32 * (1.15 if k % 4 == 0 else .9)), t0 + k * s16, pan=-.3 if k % 2 else .3, verb=.25)
    if intro: continue
    for k in range(4):
        add(K, t0 + k * beat)
        if k in (1, 3): add(C, t0 + k * beat, verb=.2)
    for k in range(16):
        add(shaker(.12 if k % 2 else .07), t0 + k * s16, pan=.4)
    for k, ln in ((0, 3), (3, 3), (6, 2), (8, 3), (11, 3), (14, 2)):   # 트로피컬 베이스 리듬
        add(bass(root - 12 + (12 if k == 14 else 0), ln * s16 * .9), t0 + k * s16)

# 리버브(짧은 IR)
ir_n = int(SR * 1.4); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 4)
L += fftconvolve(VL, ir)[:N] * .12; R += fftconvolve(VR, ir)[:N] * .12
# 사이드체인 느낌(킥마다 살짝 덕킹)
mix = np.stack([L, R], 1)[:int(SR * DUR)]
mix = sosfilt(butter(1, 30, 'high', fs=SR, output='sos'), mix, axis=0)
mix /= np.max(np.abs(mix)) + 1e-9; mix *= .89
fo = int(SR * 1.5); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', out, DUR)
