"""Tiny procedural sound effects (no audio files or numpy needed)."""
import array
import math
import pygame

# grade -> (start frequency Hz, length ms, pitch drop 0..1)
GRADE_TONES = {
    "PERFECT": (1320, 130, 0.0),
    "GREAT":   (990, 120, 0.0),
    "OK":      (660, 110, 0.0),
}


def _make_tone(freq, ms, drop=0.0, volume=0.35):
    init = pygame.mixer.get_init()
    if not init:
        return None
    rate, fmt, channels = init
    if fmt != -16:                       # only 16-bit signed output is generated
        return None
    n = int(rate * ms / 1000)
    buf = array.array("h")
    phase = 0.0
    for i in range(n):
        t = i / n
        phase += 2 * math.pi * freq * (1 - drop * t) / rate
        sample = int(32767 * volume * (1 - t) ** 2 * math.sin(phase))  # decaying envelope
        for _ in range(channels):
            buf.append(sample)
    return pygame.mixer.Sound(buffer=buf.tobytes())


class SoundBank:
    """Loads a beep per grade. If audio is unavailable the game just stays silent."""

    def __init__(self):
        self.sounds = {}
        try:
            for grade, (freq, ms, drop) in GRADE_TONES.items():
                snd = _make_tone(freq, ms, drop)
                if snd:
                    self.sounds[grade] = snd
        except pygame.error:
            self.sounds = {}

    def play(self, grade):
        snd = self.sounds.get(grade)
        if snd:
            snd.play()
