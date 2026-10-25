# 피아노 재즈 BGM 합성기 (저작권 없는 자체 작곡). 사용: python3 bgm_jazz.py out.wav 초 [seed]
import sys, numpy as np, wave
SR = 44100
out = sys.argv[1]; DUR = float(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7
rng = np.random.default_rng(seed)
BPM = float(sys.argv[4]) if len(sys.argv) > 4 else 92; beat = 60 / BPM
N = int(SR * (DUR + 2)); L = np.zeros(N); R = np.zeros(N)

def mtof(m): return 440 * 2 ** ((m - 69) / 12)

def piano(m, dur, vel=0.5):
    n = int(SR * (dur + 1.2)); t = np.arange(n) / SR; f = mtof(m)
    s = np.zeros(n)
    for k, a in enumerate([1, .55, .32, .18, .1, .06], 1):
        inh = f * k * (1 + 0.0004 * k * k)
        s += a * np.sin(2 * np.pi * inh * t + rng.uniform(0, 6.28)) * np.exp(-t * (1.3 + 0.9 * k) * (1 + f / 1500))
    att = np.minimum(1, t / 0.004)
    rel = np.where(t > dur, np.exp(-(t - dur) * 6), 1)
    return s * att * rel * vel * 0.18

def bass(m, dur, vel=0.6):
    n = int(SR * (dur + .3)); t = np.arange(n) / SR; f = mtof(m)
    s = np.sin(2*np.pi*f*t) + .35*np.sin(4*np.pi*f*t) + .12*np.sin(6*np.pi*f*t)
    env = np.minimum(1, t/0.01) * np.exp(-t*2.2) * np.where(t > dur, np.exp(-(t-dur)*12), 1)
    return s * env * vel * 0.22

def ride(vel=0.12):
    n = int(SR*0.5); t = np.arange(n)/SR
    nz = rng.standard_normal(n); nz = np.diff(np.concatenate([[0], nz]))  # 고역 강조
    ping = sum(np.sin(2*np.pi*f*t) for f in (5200, 6900, 8300)) * 0.15
    return (nz*0.5 + ping) * np.exp(-t*9) * vel * 0.25

def brush(vel=0.08):
    n = int(SR*0.18); t = np.arange(n)/SR
    return rng.standard_normal(n) * np.exp(-t*25) * vel * 0.2

def add(x, at, pan=0.0):
    i = int(at*SR); j = min(N, i+len(x)); x = x[:j-i]
    L[i:j] += x * (1-pan) ; R[i:j] += x * (1+pan)

# 진행: ii-V-I-VI (F장조) 루프. (근음, 보이싱)
prog = [(50, [53, 57, 60, 64]),   # Dm9  (D F A C E)
        (43, [53, 57, 59, 64]),   # G13  (F A B E)
        (48, [52, 55, 59, 62]),   # Cmaj9(E G B D)
        (45, [49, 55, 58, 61])]   # A7b9 (C# G Bb C#)
prog = [(r+5, [n+5 for n in v]) for r, v in prog]  # F조로 이동
scale = [65, 67, 69, 70, 72, 74, 76, 77, 79]
sw = 0.62  # 스윙 비율
t = 0.0; bar = 0
while t < DUR:
    root, voic = prog[bar % 4]
    # 피아노 컴핑: 2·4박 엇박에 짧게
    for b, d in ([(0.0, .4), (1.0+sw, .3), (2.0+sw, .3), (3.0+sw, .3)] if BPM > 110 else ([(1.0+sw, .35), (3.0+sw, .35)] if bar % 2 else [(0.0, 1.6), (2.0+sw, .45)])):
        for k, n in enumerate(voic):
            add(piano(n, d*beat, 0.42 + rng.uniform(-.05, .05)), t + b*beat + k*0.006, pan=-0.15)
    # 워킹 베이스 4분음표
    walk = [root-12, root-12+rng.choice([3, 4]), root-12+7, root-12+rng.choice([10, 9, -1])]
    for b, m in enumerate(walk):
        add(bass(m, beat*0.9), t + b*beat, pan=0.05)
    # 라이드 스윙 + 브러시 2·4
    for b in range(4):
        add(ride(0.10 if b % 2 == 0 else 0.13), t + b*beat, pan=0.3)
        if b % 2 == 1:
            add(ride(0.06), t + (b+sw)*beat, pan=0.3); add(brush(0.09), t + b*beat, pan=-0.2)
    # 멜로디: 짝수 마디마다 짧은 프레이즈
    if bar % 2 == 0 and bar > 0:
        pos = 0.0; note = int(rng.integers(2, 6))
        for _ in range(int(rng.integers(3, 6))):
            note = int(np.clip(note + rng.choice([-2, -1, 1, 2]), 0, len(scale)-1))
            d = rng.choice([0.5, 1.0, 1.5])
            add(piano(scale[note], d*beat*0.9, 0.55), t + (pos + (sw-0.5 if pos % 1 else 0))*beat, pan=0.1)
            pos += d
            if pos >= 3.5: break
    t += 4*beat; bar += 1

# 간단한 리버브(다중 지연) + 마스터
def verb(x):
    y = x.copy()
    for d, g in [(0.029, .35), (0.041, .3), (0.053, .25), (0.071, .2), (0.097, .15), (0.131, .1)]:
        k = int(d*SR); y[k:] += x[:-k]*g
    return y
L, R = verb(L), verb(R)
n = int(SR*DUR); L, R = L[:n], R[:n]
fade = int(SR*1.5); env = np.ones(n); env[:int(SR*.3)] = np.linspace(0, 1, int(SR*.3)); env[-fade:] = np.linspace(1, 0, fade)
L *= env; R *= env
pk = max(np.abs(L).max(), np.abs(R).max()); L, R = L/pk*0.6, R/pk*0.6
pcm = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', out, DUR)
