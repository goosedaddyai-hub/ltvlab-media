# 'Tension→Lift' BGM — 마이너 펄스 긴장감 → 후반 밝게 전환 (자체 합성, 저작권 없음)
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
SR = 44100
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)

def make(DUR, LIFT, seed=93, BPM=96.0):
    rng = np.random.default_rng(seed)
    beat = 60 / BPM; N = int(SR * (DUR + 2))
    L_, R_ = np.zeros(N), np.zeros(N); RV = np.zeros(N)
    def add(sig, t0, pan=0.0, rev=0.0):
        i = int(t0 * SR); n = min(len(sig), N - i)
        if n <= 0: return
        l, r = np.sqrt(.5 * (1 - pan)), np.sqrt(.5 * (1 + pan))
        L_[i:i+n] += sig[:n] * l; R_[i:i+n] += sig[:n] * r
        if rev: RV[i:i+n] += sig[:n] * rev
    def kick(v=1):
        t = np.arange(int(SR*.45))/SR; f = 45 + 120*np.exp(-t*30)
        return np.tanh(1.5*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*7))*v
    def tick(v=.18, hi=True):
        n = int(SR*.06); t = np.arange(n)/SR; s = rng.standard_normal(n)
        s = sosfilt(butter(4, 7000 if hi else 3000, 'hp', fs=SR, output='sos'), s)
        return s*np.exp(-t*(70 if hi else 40))*v
    def clap(v=.35):
        n = int(SR*.25); t = np.arange(n)/SR; s = rng.standard_normal(n)
        s = sosfilt(butter(2, [900, 5000], 'bp', fs=SR, output='sos'), s)
        e = np.exp(-t*18) + .6*np.exp(-np.maximum(0, t-.012)*30)*(t > .012)
        return s*e*v
    def bass(m, d, v=.38):
        n = int(SR*(d+.04)); t = np.arange(n)/SR; f = mtof(m)
        s = np.sin(2*np.pi*f*t) + .3*np.sin(4*np.pi*f*t)
        return np.tanh(1.8*s)*np.minimum(1, t/.004)*np.where(t > d, np.exp(-(t-d)*50), np.exp(-t*1.5))*v
    def keys(m, v=.16, dec=3.0):
        n = int(SR*1.6); t = np.arange(n)/SR; f = mtof(m); s = np.zeros(n)
        for k, a in ((1, 1), (2, .45), (3, .2), (4, .1)): s += a*np.sin(2*np.pi*f*k*t)*np.exp(-t*dec*(1+.4*k))
        return s*np.minimum(1, t/.003)*v
    def pad(ms, d, v=.05):
        n = int(SR*d); t = np.arange(n)/SR; s = np.zeros(n)
        for m in ms:
            for dt in (-.1, .1):
                ph = 2*np.pi*mtof(m)*2**(dt/12)*t; s += sum(np.sin(k*ph)/k for k in range(1, 6))
        e = np.minimum(1, t/.6)*np.minimum(1, (d-t)/.6)
        return sosfilt(butter(2, 2200, 'lp', fs=SR, output='sos'), s*e)*v/len(ms)
    dark = [(50, [62, 65, 69]), (46, [58, 62, 65]), (43, [55, 58, 62]), (45, [57, 61, 64])]   # Dm Bb Gm A
    bright = [(41, [65, 69, 72]), (48, [64, 67, 72]), (50, [62, 65, 69]), (46, [62, 65, 70])]  # F C Dm Bb
    bar = beat*4; nb = int(DUR/bar)+2
    for b in range(nb):
        t0 = b*bar; lift = t0 >= LIFT - 1e-6
        root, ch = (bright if lift else dark)[b % 4]
        add(pad([m-12 for m in ch]+ch, bar+.6, .06 if lift else .05), t0, rev=.3)
        for s8 in range(8):
            ts = t0 + s8*beat/2
            add(bass(root-12 + (12 if (lift and s8 % 4 == 3) else 0), beat/2*.8, .34), ts)
            add(tick(.12 if s8 % 2 else .2), ts + (0.02*rng.random()), pan=.3)
        for q in (0, 2): add(kick(.9), t0+q*beat)
        if lift:
            add(kick(.6), t0+3.5*beat)
            for q in (1, 3): add(clap(.32), t0+q*beat, rev=.4)
        else:
            add(kick(.5), t0+2.75*beat)
        arp = ch + [ch[1]+12]
        pat = [0, 2, 1, 3, 2, 1, 0, 2] if not lift else [0, 1, 2, 3, 2, 3, 1, 2]
        for s8, ix in enumerate(pat):
            add(keys(arp[ix]+12, .11 if not lift else .13), t0+s8*beat/2, pan=-.25 + .5*(s8 % 2), rev=.35)
    # 간단 리버브
    ir = np.random.default_rng(1).standard_normal(int(SR*1.4))*np.exp(-np.arange(int(SR*1.4))/SR*3.2)*.02
    rv = fftconvolve(RV, ir)[:N]
    L_ += rv; R_ += rv*0.97
    st = np.stack([L_, R_], 1)[:int(SR*DUR)]
    fo = int(SR*1.6); st[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return st / (np.abs(st).max()+1e-9) * 0.8
