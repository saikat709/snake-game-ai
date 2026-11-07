"""
Procedural audio synthesizer for Cyber Snake.
Generates retro-futuristic sound effects dynamically using pygame.mixer.
Zero external audio files required.
"""

import math
import struct
import pygame

class AudioManager:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.sounds = {}
        
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.enabled = True
            self._generate_sounds()
        except Exception as e:
            # Fallback if audio device is unavailable
            self.enabled = False
            print(f"[Audio] Audio device not available: {e}. Running in silent mode.")

    def _create_sound_from_samples(self, samples, sample_rate=44100):
        """Convert a list of floating-point audio samples (-1.0 to 1.0) into a pygame Sound."""
        buf = bytearray()
        for s in samples:
            clamped = max(-32767, min(32767, int(s * 32767.0)))
            buf += struct.pack('<hh', clamped, clamped)
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_sounds(self):
        """Synthesize all custom retro-futuristic sound effects."""
        sample_rate = 44100

        # 1. Boot Power Surge / Chord (0.9s)
        n = int(sample_rate * 0.9)
        boot_samples = []
        for i in range(n):
            t = i / sample_rate
            env = min(1.0, t * 4.0) * max(0.0, 1.0 - (t / 0.9) ** 2)
            freq1 = 110 + 220 * (t / 0.9)
            freq2 = 165 + 330 * (t / 0.9)
            freq3 = 220 + 440 * (t / 0.9)
            val = 0.15 * math.sin(2 * math.pi * freq1 * t) + \
                  0.15 * math.sin(2 * math.pi * freq2 * t) + \
                  0.12 * math.sin(2 * math.pi * freq3 * t)
            boot_samples.append(val * env)
        self.sounds['boot'] = self._create_sound_from_samples(boot_samples)

        # 2. Terminal Beep / Keystroke (0.04s)
        n = int(sample_rate * 0.04)
        beep_samples = []
        for i in range(n):
            t = i / sample_rate
            env = 1.0 - (t / 0.04)
            val = 0.22 * math.sin(2 * math.pi * 1400 * t)
            beep_samples.append(val * env)
        self.sounds['beep'] = self._create_sound_from_samples(beep_samples)

        # 3. Soft Turn / Arrow Key Whoosh-Click (0.05s)
        n = int(sample_rate * 0.05)
        turn_samples = []
        for i in range(n):
            t = i / sample_rate
            env = (1.0 - t / 0.05) ** 2
            val = 0.18 * math.sin(2 * math.pi * (300 + 400 * (1.0 - t / 0.05)) * t)
            turn_samples.append(val * env)
        self.sounds['turn'] = self._create_sound_from_samples(turn_samples)

        # 4. Normal Eat Chimes (dynamically pitched for combos x1 through x5)
        base_freqs = [523.25, 659.25, 783.99, 1046.50, 1318.51] # C5, E5, G5, C6, E6
        for idx, base_f in enumerate(base_freqs, start=1):
            n = int(sample_rate * 0.14)
            eat_samples = []
            for i in range(n):
                t = i / sample_rate
                env = (1.0 - t / 0.14) ** 1.5
                f = base_f + 120 * (1.0 - t / 0.14)
                # Primary sine + harmonic sparkle
                val = 0.28 * math.sin(2 * math.pi * f * t) + 0.12 * math.sin(4 * math.pi * f * t)
                eat_samples.append(val * env)
            self.sounds[f'eat_{idx}'] = self._create_sound_from_samples(eat_samples)

        # 5. Bonus Food Spawn Alarm (0.3s)
        n = int(sample_rate * 0.3)
        spawn_samples = []
        for i in range(n):
            t = i / sample_rate
            env = (1.0 - t / 0.3)
            # Pulsing dual frequency
            mod = 1.0 + 0.3 * math.sin(2 * math.pi * 25 * t)
            val = 0.25 * math.sin(2 * math.pi * 880 * mod * t)
            spawn_samples.append(val * env)
        self.sounds['bonus_spawn'] = self._create_sound_from_samples(spawn_samples)

        # 6. Bonus Food Collect (0.35s Major Arpeggio Fanfare)
        n = int(sample_rate * 0.35)
        bonus_eat_samples = []
        for i in range(n):
            t = i / sample_rate
            env = (1.0 - t / 0.35) ** 1.2
            # Arpeggio sequence
            step = int(t / 0.08)
            freqs = [659.25, 830.61, 987.77, 1318.51] # E, G#, B, E
            f = freqs[min(step, len(freqs)-1)]
            val = 0.3 * math.sin(2 * math.pi * f * t) + 0.1 * math.sin(4 * math.pi * f * t)
            bonus_eat_samples.append(val * env)
        self.sounds['bonus_eat'] = self._create_sound_from_samples(bonus_eat_samples)

        # 7. Game Over Explosion / Cyber Meltdown (0.55s)
        n = int(sample_rate * 0.55)
        import random
        rng = random.Random(42)
        over_samples = []
        for i in range(n):
            t = i / sample_rate
            env = (1.0 - t / 0.55) ** 1.8
            # Bass plunge
            bass_f = 140 * (1.0 - t / 0.6) + 30
            saw = (2.0 * ((bass_f * t) % 1.0) - 1.0)
            noise = rng.uniform(-1.0, 1.0) * 0.4
            val = 0.35 * saw + noise
            over_samples.append(val * env)
        self.sounds['game_over'] = self._create_sound_from_samples(over_samples)

    def play(self, sound_name):
        if not self.enabled or self.muted:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            snd.play()

    def play_boot(self):
        self.play('boot')

    def play_beep(self):
        self.play('beep')

    def play_turn(self):
        self.play('turn')

    def play_eat(self, combo=1):
        tier = max(1, min(5, combo))
        self.play(f'eat_{tier}')

    def play_bonus_spawn(self):
        self.play('bonus_spawn')

    def play_bonus_eat(self):
        self.play('bonus_eat')

    def play_game_over(self):
        self.play('game_over')

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted
