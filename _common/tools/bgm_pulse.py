# 'Pulse' BGM — 긴장감 인트로(마이너 펄스) → 3.6초 드롭 → 밝은 플럭 그루브 (자체 합성, 저작권 없음)
# 사용: python3 bgm_pulse.py out.wav 초 드롭초 [seed]
import sys, numpy as np, wave
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
out = sys.argv[1]; DUR = float(sys.argv[2]); DROP = float(sys.argv[3]); seed = int(sys.argv[4]) if len(sys.argv) > 4 else 11
SFX = [tuple(map(float, s.split(':'))) for s in (sys.argv[5].split(',') if len(sys.argv) > 5 else [])]  # 종류:초
rng = np.random.default_rng(seed)
BPM = 100.0; beat = 60 / BPM; bar = beat * 4
N = int(SR * (DUR + 3))
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
ML, MR = np.zeros(N), np.zeros(N); RL, RR = np.zeros(N), np.zeros(N)   # 드라이 / 리버브 보낼 버스


def add(sig, t0, pan=0.0, rev=0.0):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    ML[i:i + n] += sig[:n] * l; MR[i:i + n] += sig[:n] * r
    if rev: RL[i:i + n] += sig[:n] * l * rev; RR[i:i + n] += sig[:n] * r * rev


def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t * d)


def pluck(m, vel, dec=5.0):
    n = int(SR * 1.2); t = np.arange(n) / SR; f = mtof(m)
    s = np.zeros(n)
    for k, a in ((1, 1), (2, .5), (3, .3), (4, .18), (5, .1)):
        s += a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * dec * (1 + 0.6 * k))
    return s * np.minimum(1, t / 0.003) * vel


def stab(m_list, dur, vel, bright=1.0):
    n = int(SR * (dur + .3)); t = np.arange(n) / SR; s = np.zeros(n)
    for m in m_list:
        for d in (-0.08, 0.08):
            f = mtof(m) * 2 ** (d / 12)
            ph = 2 * np.pi * f * t
            s += sum((1 / k) * np.sin(k * ph) * (bright ** (k - 1)) for k in range(1, 7))
    e = np.minimum(1, t / 0.01) * np.where(t > dur, np.exp(-(t - dur) * 14), np.exp(-t * 1.2))
    return s * e * vel / (len(m_list) * 3)


def bass(m, dur, vel=0.42):
    n = int(SR * (dur + .05)); t = np.arange(n) / SR; f = mtof(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) + 0.1 * np.sin(2 * np.pi * 3 * f * t)
    return np.tanh(1.6 * s) * np.minimum(1, t / .005) * np.where(t > dur, np.exp(-(t - dur) * 60), 1) * vel


def kick(vel=1.0):
    n = int(SR * .5); t = np.arange(n) / SR
    f = 46 + 110 * np.exp(-t * 32); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    return np.tanh(1.4 * s) * vel


def clap(vel=0.5):
    n = int(SR * .3); t = np.arange(n) / SR
    nz = sosfilt(butter(2, [1000, 6000], 'band', fs=SR, output='sos'), rng.standard_normal(n))
    e = sum(np.exp(-np.maximum(0, t - o) * 60) * (t >= o) for o in (0, .011, .022)) / 3 + np.exp(-t * 16) * (t > .022)
    return nz * e * vel


def hat(vel=0.1, op=False):
    n = int(SR * (.22 if op else .05)); t = np.arange(n) / SR
    nz = sosfilt(butter(2, 8000, 'high', fs=SR, output='sos'), rng.standard_normal(n))
    return nz * np.exp(-t * (16 if op else 80)) * vel


def noise_riser(dur, vel=0.35):
    n = int(SR * dur); t = np.arange(n) / SR
    nz = rng.standard_normal(n); out_ = np.zeros(n); blk = 2048
    for i in range(0, n, blk):
        fc = 400 + 9000 * (i / n) ** 2
        out_[i:i + blk] = sosfilt(butter(2, min(fc, 18000), 'high', fs=SR, output='sos'), nz[i:i + blk])
    return out_ * (t / dur) ** 2 * vel


def impact(vel=0.9):
    n = int(SR * 1.6); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t * 18)) / SR) * np.exp(-t * 2.5)
    nz = sosfilt(butter(2, 2500, 'low', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t * 6) * .5
    return np.tanh(1.5 * (s + nz)) * vel


def thud(vel=0.8):   # 도장 '쾅'
    n = int(SR * .5); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(70 + 120 * np.exp(-t * 40)) / SR) * np.exp(-t * 12)
    nz = sosfilt(butter(2, [300, 3000], 'band', fs=SR, output='sos'), rng.standard_normal(n)) * np.exp(-t * 30)
    return np.tanh(2 * (s + nz)) * vel


def swish(vel=0.25):  # 종이 넘기는 소리
    n = int(SR * .28); t = np.arange(n) / SR
    nz = sosfilt(butter(2, [1500, 9000], 'band', fs=SR, output='sos'), rng.standard_normal(n))
    return nz * np.sin(np.pi * t / t[-1]) ** 2 * vel


# ---------- 인트로(긴장): A minor 펄스 ----------
t = 0.0
while t < DROP - 1e-3:
    for j in range(8):
        tt = t + j * beat / 2
        if tt >= DROP: break
        add(bass(33, beat * .4, .3), tt)                          # A1 8분 펄스
        add(hat(.06 + .03 * (j % 2)), tt + beat / 4, .3)
    add(stab([57, 60, 64], beat * .3, .22, .7), t, -.2, rev=.5)   # Am 스탭
    add(stab([57, 60, 65], beat * .3, .18, .7), t + beat * 2.5, .2, rev=.5)
    for j, m in enumerate([76, 72, 69, 72]):
        add(pluck(m, .07, 9), t + (j * 0.5 + 1) * beat, .4 - .25 * j, rev=.6)
    t += bar
add(noise_riser(DROP), 0.0)
add(impact(), DROP, rev=.4)

# ---------- 드롭 이후: 밝은 그루브 ----------
prog = [(41, [65, 69, 72, 76]), (43, [67, 71, 74, 77]), (40, [64, 67, 71, 74]), (45, [69, 72, 76, 79])]   # F - G - Em - Am
arp_pat = [0, 2, 1, 3, 2, 1, 3, 2]
t = DROP; k = 0
while t < DUR + 1:
    root, ch = prog[k % 4]
    add(stab(ch[:3], bar * .9, .10, .5), t, 0, rev=.8)               # 패드성 코드
    for b_ in range(4):
        add(kick(.95 if b_ in (0, 2) else .55), t + b_ * beat)
        if b_ in (1, 3): add(clap(.42), t + b_ * beat, rev=.25)
        for h in range(4):
            add(hat(.05 + .03 * (h == 2), op=(h == 2 and b_ == 3)), t + b_ * beat + h * beat / 4 + rng.normal(0, .003), .25)
    for s_, ln in ((0, .7), (.75, .2), (1.5, .45), (2, .7), (2.75, .2), (3.5, .45)):
        add(bass(root - 12 if s_ != 2.75 else root, beat * ln), t + s_ * beat)
    for j in range(8):                                               # 8분 플럭 아르페지오
        m = ch[arp_pat[j]] + 12
        add(pluck(m, .10 + .03 * (j % 4 == 0), 5.5), t + j * beat / 2, .35 * np.sin(j * 1.3), rev=.45)
    if k % 2 == 1:                                                   # 2마디마다 짧은 훅 리프
        for j, (m, o) in enumerate(((84, 2.5), (83, 3.0), (81, 3.25), (79, 3.5))):
            add(pluck(m, .09, 4), t + o * beat, -.2, rev=.6)
    t += bar; k += 1

for kind, at in SFX:
    {1: lambda: add(thud(), at, rev=.2), 2: lambda: add(swish(), at, .3 * np.sin(at)), 3: lambda: add(noise_riser(.5, .18), at - .5)}[int(kind)]()

# ---------- 믹스 ----------
ir_n = int(SR * 1.8); ir_t = np.arange(ir_n) / SR
ir = rng.standard_normal((2, ir_n)) * np.exp(-ir_t * 3.2)
L = ML + fftconvolve(RL, ir[0])[:N] * .05
R = MR + fftconvolve(RR, ir[1])[:N] * .05
mix = np.stack([L, R])
mix = sosfilt(butter(1, 30, 'high', fs=SR, output='sos'), mix)
mix = np.tanh(mix * 1.1)
n = int(SR * DUR); mix = mix[:, :n]
mix *= 0.89 / (np.abs(mix).max() + 1e-9)
fade = int(SR * 1.5); mix[:, -fade:] *= np.linspace(1, 0, fade)
pcm = (mix.T * 32767).astype(np.int16)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('bgm', out, DUR)
