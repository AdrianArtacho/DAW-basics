#!/usr/bin/env python3
"""Create the original 3-second teaching sound; no external samples or dependencies."""
from pathlib import Path
import math
import random
import struct
import wave

ROOT = Path(__file__).resolve().parents[1]
RATE = 48000
rng = random.Random(21)
samples = []
previous_noise = 0.0
for n in range(RATE * 3):
    t = n / RATE
    noise = rng.uniform(-1, 1)
    high_noise = noise - previous_noise
    previous_noise = noise
    value = 0.0
    for start, strength in [(0.06, 1.0), (0.78, 0.65), (1.46, 0.85)]:
        u = t - start
        if u >= 0:
            attack = min(1, u / .002)
            body = math.sin(2 * math.pi * (112 * u + 11 * (1 - math.exp(-10 * u)))) * math.exp(-6.5 * u)
            ring = (.32 * math.sin(2 * math.pi * 437 * u) + .21 * math.sin(2 * math.pi * 691 * u)) * math.exp(-3.2 * u)
            grain = .26 * high_noise * math.exp(-24 * u) + .045 * noise * math.exp(-2.6 * u)
            value += strength * attack * (body + ring + grain)
    value *= min(1, t / .005, (3 - t) / .05)
    samples.append(value)
scale = 0.5 / max(abs(x) for x in samples)
out = ROOT / 'assets/audio/3-sekunden.wav'
out.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out), 'wb') as wav:
    wav.setparams((1, 2, RATE, len(samples), 'NONE', 'not compressed'))
    wav.writeframes(b''.join(struct.pack('<h', round(v * scale * 32767)) for v in samples))
print(f'Created {out.relative_to(ROOT)}: 3.000 s, mono, 48 kHz, 16-bit PCM, peak about -6 dBFS')
