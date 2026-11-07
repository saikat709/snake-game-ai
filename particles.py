"""
Particle system, glow effects, floating text popups, and screen shake.
"""

import math
import random
import pygame

class GlowManager:
    """Caches pre-rendered soft glow textures for fast additive blitting."""
    _cache = {}

    @classmethod
    def get_glow_surf(cls, radius, color):
        key = (radius, color[:3])
        if key in cls._cache:
            return cls._cache[key]

        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        r, g, b = color[:3]

        # Draw concentric soft circles
        steps = max(8, min(24, radius // 2))
        for i in range(steps, 0, -1):
            ratio = i / steps
            current_r = int(radius * ratio)
            alpha = int(255 * (1.0 - ratio) ** 1.8 * 0.45)
            pygame.draw.circle(surf, (r, g, b, alpha), (radius, radius), current_r)

        cls._cache[key] = surf
        return surf

    @classmethod
    def draw_glow(cls, surface, center, radius, color):
        glow_surf = cls.get_glow_surf(radius, color)
        top_left = (int(center[0] - radius), int(center[1] - radius))
        surface.blit(glow_surf, top_left, special_flags=pygame.BLEND_ADD)


class SparkParticle:
    """High-velocity glowing spark with physics decay and color shift."""
    def __init__(self, x, y, color, speed_mult=1.0):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(60, 220) * speed_mult
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.radius = random.uniform(2.5, 5.0)
        self.lifespan = random.uniform(0.35, 0.75)
        self.life = self.lifespan
        self.friction = 0.92

    def update(self, dt):
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= (self.friction ** (dt * 60))
        self.vy *= (self.friction ** (dt * 60))
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        ratio = max(0.0, self.life / self.lifespan)
        current_r = max(1, int(self.radius * ratio))
        alpha = int(255 * ratio)
        
        # Draw particle core
        r, g, b = self.color[:3]
        core_surf = pygame.Surface((current_r * 2 + 2, current_r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(core_surf, (r, g, b, alpha), (current_r + 1, current_r + 1), current_r)
        surface.blit(core_surf, (int(self.x - current_r - 1), int(self.y - current_r - 1)), special_flags=pygame.BLEND_ADD)


class RingShockwave:
    """Expanding neon shockwave ring."""
    def __init__(self, x, y, max_radius, color, duration=0.45):
        self.x = float(x)
        self.y = float(y)
        self.max_radius = max_radius
        self.color = color
        self.duration = duration
        self.elapsed = 0.0

    def update(self, dt):
        self.elapsed += dt
        return self.elapsed < self.duration

    def draw(self, surface):
        progress = self.elapsed / self.duration
        if progress >= 1.0:
            return
        current_r = int(self.max_radius * math.sqrt(progress))
        if current_r < 2:
            return
        
        alpha = int(255 * (1.0 - progress) ** 1.5)
        thickness = max(1, int(4 * (1.0 - progress)))
        
        size = current_r * 2 + 6
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        r, g, b = self.color[:3]
        pygame.draw.circle(surf, (r, g, b, alpha), (size // 2, size // 2), current_r, thickness)
        surface.blit(surf, (int(self.x - size // 2), int(self.y - size // 2)), special_flags=pygame.BLEND_ADD)


class FloatingText:
    """Dynamic floating score and combo announcement popup."""
    def __init__(self, x, y, text, color, font, duration=0.85):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.font = font
        self.duration = duration
        self.elapsed = 0.0

    def update(self, dt):
        self.elapsed += dt
        self.y -= 45 * dt # Floats smoothly upward
        return self.elapsed < self.duration

    def draw(self, surface):
        progress = self.elapsed / self.duration
        if progress >= 1.0:
            return
        
        alpha = int(255 * (1.0 - (progress ** 1.8)))
        txt_surf = self.font.render(self.text, True, self.color)
        txt_surf.set_alpha(alpha)
        
        # Slight pop scale in beginning
        rect = txt_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt_surf, rect)


class AmbientDust:
    """Drifting subtle digital motes in the background arena."""
    def __init__(self, bounds_rect):
        self.bounds = bounds_rect
        self.x = random.uniform(bounds_rect.left, bounds_rect.right)
        self.y = random.uniform(bounds_rect.top, bounds_rect.bottom)
        self.vx = random.uniform(-10, 10)
        self.vy = random.uniform(-15, -5)
        self.radius = random.uniform(1.0, 2.2)
        self.alpha = random.randint(40, 120)
        self.pulse = random.uniform(0, 2 * math.pi)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.pulse += dt * 2.0
        
        # Wrap around bounds
        if self.x < self.bounds.left:
            self.x = self.bounds.right
        elif self.x > self.bounds.right:
            self.x = self.bounds.left
        if self.y < self.bounds.top:
            self.y = self.bounds.bottom
        elif self.y > self.bounds.bottom:
            self.y = self.bounds.top

    def draw(self, surface):
        pulsed_alpha = int(self.alpha * (0.7 + 0.3 * math.sin(self.pulse)))
        s = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(s, (80, 180, 255, pulsed_alpha), (3, 3), int(self.radius))
        surface.blit(s, (int(self.x - 3), int(self.y - 3)), special_flags=pygame.BLEND_ADD)


class ScreenShake:
    """Trauma-based screen shake implementation."""
    def __init__(self):
        self.trauma = 0.0
        self.max_offset = 14.0
        self.decay = 2.5

    def add_trauma(self, amount):
        self.trauma = min(1.0, self.trauma + amount)

    def update(self, dt):
        if self.trauma > 0:
            self.trauma = max(0.0, self.trauma - self.decay * dt)

    def get_offset(self):
        if self.trauma <= 0.001:
            return (0, 0)
        shake = self.trauma * self.trauma
        dx = random.uniform(-1.0, 1.0) * self.max_offset * shake
        dy = random.uniform(-1.0, 1.0) * self.max_offset * shake
        return (int(dx), int(dy))


class ParticleSystem:
    """Central particle and FX manager."""
    def __init__(self, arena_rect):
        self.arena_rect = arena_rect
        self.sparks = []
        self.shockwaves = []
        self.floating_texts = []
        self.dust_particles = [AmbientDust(arena_rect) for _ in range(35)]
        self.shake = ScreenShake()

    def spawn_eat_burst(self, x, y, color, count=22):
        for _ in range(count):
            self.sparks.append(SparkParticle(x, y, color))
        self.shockwaves.append(RingShockwave(x, y, max_radius=42, color=color, duration=0.35))
        self.shake.add_trauma(0.22)

    def spawn_bonus_burst(self, x, y, color):
        for _ in range(40):
            self.sparks.append(SparkParticle(x, y, color, speed_mult=1.4))
        self.shockwaves.append(RingShockwave(x, y, max_radius=75, color=color, duration=0.5))
        self.shake.add_trauma(0.4)

    def spawn_death_burst(self, segments_pixels):
        """Massive explosion when snake crashes."""
        for x, y, col in segments_pixels:
            for _ in range(8):
                self.sparks.append(SparkParticle(x, y, col, speed_mult=1.2))
        self.shake.add_trauma(0.85)

    def spawn_text(self, x, y, text, color, font):
        self.floating_texts.append(FloatingText(x, y, text, color, font))

    def update(self, dt):
        self.sparks = [p for p in self.sparks if p.update(dt)]
        self.shockwaves = [w for w in self.shockwaves if w.update(dt)]
        self.floating_texts = [t for t in self.floating_texts if t.update(dt)]
        for dust in self.dust_particles:
            dust.update(dt)
        self.shake.update(dt)

    def draw_ambient(self, surface):
        for dust in self.dust_particles:
            dust.draw(surface)

    def draw_effects(self, surface):
        for shockwave in self.shockwaves:
            shockwave.draw(surface)
        for spark in self.sparks:
            spark.draw(surface)
        for text in self.floating_texts:
            text.draw(surface)
