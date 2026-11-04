# 'Noir' BGM — 심장박동+로우패스 긴장 인트로 → 붐뱁 로파이(로즈 피아노) → LIFT초부터 밝은 코드 (자체 합성, 저작권 없음)
# 사용: python3 bgm_noir.py out.wav 총초 드롭초 리프트초 [seed] [sfx 종류:초,...]  (1=도장 2=종이 3=라이저)
import sys, numpy as np, wave
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
out = sys.argv[1]; DUR = float(sys.argv[2]); DROP = float(sys.argv[3]); LIFT = float(sys.argv[4])
seed = int(sys.argv[5]) if len(sys.argv) > 5 else 7
SFX = [tuple(map(float, s.split(':'))) for s in (sys.argv[6].split(',') if len(sys.argv) > 6 and sys.argv[6] else [])]
rng = np.random.default_rng(seed)
BPM = 86.0; beat = 60 / BPM; bar = beat * 4
N = int(SR * (DUR + 3))
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
ML, MR = np.zeros(N), np.zeros(N); RL, RR = np.zeros(N), np.zeros(N)


def add(sig, t0, pan=0.0, rev=0.0):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    ML[i:i + n] += sig[:n] * l; MR[i:i + n] += sig[:n] * r
    if rev: RL[i:i + n] += sig[:n] * l * rev; RR[i:i + n] += sig[:n] * r * rev


def rhodes(m, dur, vel):   # FM 일렉 피아노
    n = int(SR * (dur + 0.6)); t = np.arange(n) / SR; f = mtof(m)
    mod = np.sin(2 * np.pi * f * t) * 1.6 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 1.4) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    e = np.minimum(1, t / 0.004) * np.where(t > dur, np.exp(-(t - dur) * 8), 1)
    return s * e * trem * vel


def chord(ms, dur, vel, spread=0.018):
    n = int(SR * (dur + 0.7)); s = np.zeros(n)
    for k, m in enumerate(ms):
        x = rhodes(m, dur, vel / len(ms) * 2.2); o = int(k * spread * SR); s[o:o + len(x)] += x[:n - o]
    return s


def bass(m, dur, vel=0.5):
    n = int(SR * (dur + .05)); t = np.arange(n) / SR; f = mtof(m)
    s = np.sin(2 * np.pi * f * t) + 0.18 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(1.3 * s) * np.minimum(1, t / .006) * np.where(t > dur, np.exp(-(t - dur) * 40), np.exp(-t * .8)) * vel


def kick(vel=1.0):
    n = int(SR * .45); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-t * 28)) / SR) * np.exp(-t * 7)
    return np.tanh(1.6 * s) * vel


def snare(vel=0.45):
    n = int(SR * .35); t = np.arange(n) / SR
    nz = sosfilt(butter(2, [900, 7000], 'band', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t * 18)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * .6
    return np.tanh(1.5 * (nz + body)) * vel


def hat(vel=0.08):
    n = int(SR * .06); t = np.arange(n) / SR
    return sosfilt(butter(2, 7500, 'high', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t * 70) * vel


def heart(vel=0.8):
    s = np.zeros(int(SR * .6))
    for o, v in ((0, 1), (.16, .7)):
        n = int(SR * .25); t = np.arange(n) / SR
        x = np.sin(2 * np.pi * np.cumsum(45 + 40 * np.exp(-t * 30)) / SR) * np.exp(-t * 16) * v
        i = int(o * SR); s[i:i + n] += x
    return np.tanh(2 * s) * vel


def riser(dur, vel=0.3):
    n = int(SR * dur); t = np.arange(n) / SR; nz = rng.standard_normal(n); o = np.zeros(n); blk = 2048
    for i in range(0, n, blk):
        o[i:i + blk] = sosfilt(butter(2, min(300 + 9000 * (i / n) ** 2, 18000), 'high', fs=SR, output='sos'), nz[i:i + blk])
    return o * (t / dur) ** 2 * vel


def impact(vel=0.85):
    n = int(SR * 1.5); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(36 + 55 * np.exp(-t * 16)) / SR) * np.exp(-t * 2.4)
    return np.tanh(1.5 * s) * vel


def thud(vel=0.85):
    n = int(SR * .5); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(70 + 120 * np.exp(-t * 40)) / SR) * np.exp(-t * 12)
    nz = sosfilt(butter(2, [300, 3000], 'band', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t * 30)
    return np.tanh(2 * (s + nz)) * vel


def swish(vel=0.25):
    n = int(SR * .28); t = np.arange(n) / SR
    nz = sosfilt(butter(2, [1500, 9000], 'band', fs=SR, output='sos'), rng.standard_normal(n))
    return nz * np.sin(np.pi * t / t[-1]) ** 2 * vel


# 인트로: 심장박동 + 저음 드론 + 먹먹한 Dm
t = 0.0
while t < DROP - 0.05:
    add(heart(.75), t); t += 0.82
n = int(SR * DROP); tt = np.arange(n) / SR
drone = (np.sin(2 * np.pi * mtof(38) * tt) + .4 * np.sin(2 * np.pi * mtof(45) * tt)) * np.minimum(1, tt / 0.8) * .16
add(drone, 0)
add(chord([62, 65, 69, 72], DROP * .8, .16), 0.1, 0, rev=.9)
add(riser(min(DROP, 2.2), .28), DROP - min(DROP, 2.2))
add(impact(), DROP, rev=.4)

# 본편: 다크 붐뱁 (Dm9 - Bbmaj7 - Gm9 - A7b9) → LIFT 이후 밝게 (Bbmaj7 - C6 - Dm9 - F/A)
dark = [(38, [62, 65, 69, 72]), (34, [58, 62, 65, 69]), (31, [58, 62, 65, 69]), (33, [61, 64, 67, 70])]
bright = [(34, [62, 65, 69, 74]), (36, [64, 67, 69, 72]), (38, [65, 69, 72, 76]), (41, [65, 69, 72, 77])]
t = DROP; k = 0; lifted = False
while t < DUR + 1:
    if not lifted and t >= LIFT - 1e-3:
        lifted = True; k = 0
    elif not lifted and t + bar > LIFT + 1e-3:   # 리프트 직전 짧은 브레이크(스네어 필) 후 박자 재시작
        root, ch = dark[k % 4]; gap = LIFT - t
        add(chord(ch, gap * .8, .18), t, -.15, rev=.7); add(kick(1.0), t); add(bass(root, gap * .7), t)
        nf = int(gap / (beat / 4))
        for j in range(max(0, nf - 6), nf): add(snare(.18 + .04 * (j - nf + 6)), t + j * beat / 4, rev=.2)
        t = LIFT; continue
    root, ch = (bright if lifted else dark)[k % 4]
    add(chord(ch, bar * .55, .2), t, -.15, rev=.7)
    add(chord(ch[1:], beat * .4, .1), t + beat * 2.5, .2, rev=.7)
    swing = beat / 2 * 0.12
    for b_ in range(4):
        bt = t + b_ * beat
        if b_ == 0: add(kick(1.0), bt)
        if b_ == 2: add(kick(.8), bt + beat / 2)
        if b_ in (1, 3): add(snare(.42), bt, rev=.25)
        for h in range(2):
            add(hat(.07 if h == 0 else .045), bt + h * (beat / 2 + swing), .3)
    for s_, ln in ((0, 1.4), (1.75, .2), (2.5, 1.2)):
        add(bass(root, beat * ln), t + s_ * beat)
    if lifted:   # 밝은 멜로디 한 줄
        for j, (m, o) in enumerate(((81, 0.5), (84, 1.5), (81, 2.25), (79, 3.0))):
            add(rhodes(m + (0 if k % 2 == 0 else -2), beat * .4, .09), t + o * beat, .25, rev=.6)
    t += bar; k += 1

# 비닐 크랙클
cr = np.zeros(N); idx = rng.integers(0, N, int(DUR * 25)); cr[idx] = rng.uniform(-.25, .25, len(idx))
cr = sosfilt(butter(2, 2000, 'high', fs=SR, output='sos'), cr) + sosfilt(butter(1, 800, 'low', fs=SR, output='sos'), rng.standard_normal(N)) * .006
ML += cr; MR += cr

for kind, at in SFX:
    {1: lambda: add(thud(), at, rev=.2), 2: lambda: add(swish(), at, .3 * np.sin(at)), 3: lambda: add(riser(.5, .18), at - .5)}[int(kind)]()

ir_n = int(SR * 1.8); ir_t = np.arange(ir_n) / SR
ir = rng.standard_normal((2, ir_n)) * np.exp(-ir_t * 3.0)
L = ML + fftconvolve(RL, ir[0])[:N] * .05
R = MR + fftconvolve(RR, ir[1])[:N] * .05
mix = np.stack([L, R])
mix = sosfilt(butter(1, 30, 'high', fs=SR, output='sos'), mix)
mix = np.tanh(mix * 1.15)
n = int(SR * DUR); mix = mix[:, :n]
mix *= 0.89 / (np.abs(mix).max() + 1e-9)
fade = int(SR * 1.5); mix[:, -fade:] *= np.linspace(1, 0, fade)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype(np.int16).tobytes())
print('bgm', out, DUR)
