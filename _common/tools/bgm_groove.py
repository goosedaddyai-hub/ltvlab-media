# 'Groove' BGM — 똑딱 시계+필터 인트로 → 누디스코 펑크(포온더플로어·슬랩 베이스·브라스 스탭) (자체 합성, 저작권 없음)
# 사용: python3 bgm_groove.py out.wav 총초 드롭초 [seed] [sfx 종류:초,...]  (1=도장 2=종이 3=라이저 4=팝 5=딩)
import sys, numpy as np, wave
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
out = sys.argv[1]; DUR = float(sys.argv[2]); DROP = float(sys.argv[3])
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 21
SFX = [tuple(map(float, s.split(':'))) for s in (sys.argv[5].split(',') if len(sys.argv) > 5 and sys.argv[5] else [])]
rng = np.random.default_rng(seed)
BPM = 116.0; beat = 60 / BPM; bar = beat * 4
N = int(SR * (DUR + 3))
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
ML, MR = np.zeros(N), np.zeros(N); RL, RR = np.zeros(N), np.zeros(N)


def add(sig, t0, pan=0.0, rev=0.0):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    ML[i:i + n] += sig[:n] * l; MR[i:i + n] += sig[:n] * r
    if rev: RL[i:i + n] += sig[:n] * l * rev; RR[i:i + n] += sig[:n] * r * rev


def saw(f, t):
    return 2 * ((f * t) % 1.0) - 1


def brass(ms, dur, vel):   # 디튠 톱니 + 필터 스윕 브라스 스탭
    n = int(SR * (dur + .15)); t = np.arange(n) / SR; s = np.zeros(n)
    for m in ms:
        f = mtof(m)
        s += saw(f * 1.004, t) + saw(f * .996, t + .01)
    cut = 900 + 3500 * np.exp(-t * 9)
    o = np.zeros(n); blk = 1024
    for i in range(0, n, blk):
        o[i:i + blk] = sosfilt(butter(2, min(cut[i], 16000), 'low', fs=SR, output='sos'), s[i:i + blk])
    e = np.minimum(1, t / .012) * np.where(t > dur, np.exp(-(t - dur) * 30), 1) * np.exp(-t * 1.5)
    return np.tanh(o * .5) * e * vel / len(ms) * 2


def keys(ms, dur, vel):    # 밝은 일렉 피아노 패드
    n = int(SR * (dur + .5)); t = np.arange(n) / SR; s = np.zeros(n)
    for k, m in enumerate(ms):
        f = mtof(m); mod = np.sin(2 * np.pi * f * 2 * t) * .8 * np.exp(-t * 5)
        x = np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 1.2)
        o = int(k * .012 * SR); s[o:] += x[:n - o]
    e = np.minimum(1, t / .005) * np.where(t > dur, np.exp(-(t - dur) * 6), 1)
    return s * e * vel / len(ms) * 2


def bass(m, dur, vel=.55, slap=False):
    n = int(SR * (dur + .04)); t = np.arange(n) / SR; f = mtof(m)
    s = np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * (6 if slap else 14))
    if slap: s += .4 * sosfilt(butter(2, [1500, 5000], 'band', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t * 60)
    e = np.minimum(1, t / .003) * np.where(t > dur, np.exp(-(t - dur) * 50), np.exp(-t * 2.5))
    return np.tanh(1.8 * s) * e * vel


def kick(vel=1.0):
    n = int(SR * .35); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(48 + 110 * np.exp(-t * 35)) / SR) * np.exp(-t * 9)
    return np.tanh(1.8 * s) * vel


def clap(vel=.4):
    n = int(SR * .25); t = np.arange(n) / SR; nz = rng.standard_normal(n)
    env = sum(np.exp(-np.maximum(0, t - o) * 60) * (t >= o) for o in (0, .011, .022)) * np.exp(-t * 14)
    return sosfilt(butter(2, [900, 6000], 'band', fs=SR, output='sos'), nz) * env * vel


def hat(vel=.07, op=False):
    n = int(SR * (.18 if op else .05)); t = np.arange(n) / SR
    return sosfilt(butter(2, 8000, 'high', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t * (18 if op else 80)) * vel


def tick(vel=.18, hi=True):
    n = int(SR * .04); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (3200 if hi else 2400) * t) * np.exp(-t * 160) * vel


def riser(dur, vel=.3):
    n = int(SR * dur); t = np.arange(n) / SR; nz = rng.standard_normal(n); o = np.zeros(n); blk = 2048
    for i in range(0, n, blk):
        o[i:i + blk] = sosfilt(butter(2, min(300 + 9000 * (i / n) ** 2, 18000), 'high', fs=SR, output='sos'), nz[i:i + blk])
    return o * (t / dur) ** 2 * vel


def impact(vel=.8):
    n = int(SR * 1.4); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t * 16)) / SR) * np.exp(-t * 2.6)
    return np.tanh(1.5 * s) * vel


def thud(vel=.85):
    n = int(SR * .5); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(70 + 120 * np.exp(-t * 40)) / SR) * np.exp(-t * 12)
    nz = sosfilt(butter(2, [300, 3000], 'band', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t * 30)
    return np.tanh(2 * (s + nz)) * vel


def swish(vel=.22):
    n = int(SR * .28); t = np.arange(n) / SR
    nz = sosfilt(butter(2, [1500, 9000], 'band', fs=SR, output='sos'), rng.standard_normal(n))
    return nz * np.sin(np.pi * t / t[-1]) ** 2 * vel


def pop(vel=.35):
    n = int(SR * .12); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(500 + 900 * np.exp(-t * 50)) / SR) * np.exp(-t * 40) * vel


def ding(vel=.3):
    n = int(SR * 1.0); t = np.arange(n) / SR; s = np.zeros(n)
    for f, a in ((1568, 1), (2093, .6)):
        s += np.sin(2 * np.pi * f * t) * np.exp(-t * 5) * a
    s[int(.09 * SR):] += (np.sin(2 * np.pi * 2637 * t) * np.exp(-t * 5))[:n - int(.09 * SR)] * .7
    return s * vel


# 인트로: 똑딱 시계 + 로우패스 코드 + 라이저 → 드롭
t = 0.0; k = 0
while t < DROP - .05:
    add(tick(.16, k % 2 == 0), t, .2 * (1 if k % 2 else -1)); t += beat / 2; k += 1
add(keys([60, 64, 67, 71], DROP * .85, .12), .05, 0, rev=.9)
add(riser(min(DROP, 2.4), .26), DROP - min(DROP, 2.4))
add(impact(), DROP, rev=.4)

# 본편: Cmaj9 - Am9 - Dm9 - G13 펑크 그루브
prog = [(36, [64, 67, 71, 74]), (33, [60, 64, 67, 71]), (38, [60, 65, 69, 72]), (31, [59, 64, 65, 69])]
bpat = [(0, .4, 0, True), (.75, .2, 12, False), (1.5, .3, 0, False), (2.0, .2, 12, True), (2.5, .4, 0, False), (3.25, .2, 7, False), (3.5, .3, 10, False)]
t = DROP; k = 0
while t < DUR + 1:
    root, ch = prog[k % 4]
    for b_ in range(4):
        bt = t + b_ * beat
        add(kick(1.0), bt)
        if b_ in (1, 3): add(clap(.38), bt, rev=.25)
        add(hat(.06), bt, -.3); add(hat(.09, True), bt + beat / 2, .3)
        add(hat(.035), bt + beat * .75, -.2)
    for o, ln, iv, sl in bpat:
        add(bass(root + iv, beat * ln, .5, sl), t + o * beat)
    # 스탭: 2&, 4 (오프비트)
    add(brass(ch, beat * .35, .16), t + beat * 1.5, -.25, rev=.5)
    add(brass(ch, beat * .25, .12), t + beat * 3.0, .25, rev=.5)
    add(keys(ch, bar * .9, .07), t, .1, rev=.8)
    if k % 2 == 1:   # 2마디마다 짧은 멜로디 훅
        for m, o in ((79, 0), (81, .5), (84, 1.0), (81, 1.75)):
            add(keys([m], beat * .3, .09), t + o * beat + beat * 2, .3, rev=.6)
    t += bar; k += 1

for kind, at in SFX:
    {1: lambda: add(thud(), at, rev=.2), 2: lambda: add(swish(), at, .3 * np.sin(at)), 3: lambda: add(riser(.5, .18), at - .5),
     4: lambda: add(pop(), at, .2), 5: lambda: add(ding(), at, 0, rev=.4)}[int(kind)]()

ir_n = int(SR * 1.6); ir_t = np.arange(ir_n) / SR
ir = rng.standard_normal((2, ir_n)) * np.exp(-ir_t * 3.2)
L = ML + fftconvolve(RL, ir[0])[:N] * .05
R = MR + fftconvolve(RR, ir[1])[:N] * .05
mix = np.stack([L, R])
mix = sosfilt(butter(1, 30, 'high', fs=SR, output='sos'), mix)
mix = np.tanh(mix * 1.1)
n = int(SR * DUR); mix = mix[:, :n]
mix *= 0.89 / (np.abs(mix).max() + 1e-9)
fade = int(SR * 1.5); mix[:, -fade:] *= np.linspace(1, 0, fade)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype(np.int16).tobytes())
print('bgm', out, DUR)
