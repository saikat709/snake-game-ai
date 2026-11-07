"""
Initial screen initialization animation sequence.
Presents a high-tech Cyberpunk CRT Boot sequence, Grid Matrix calibration,
laser sweep illumination, holographic title reveal, and seamless transition into gameplay.
"""

import math
import random
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ARENA_X, ARENA_Y,
    ARENA_WIDTH, ARENA_HEIGHT, CELL_SIZE, GRID_COLS, GRID_ROWS,
    COLOR_BG_DARK, COLOR_CYAN, COLOR_MAGENTA, COLOR_GOLD,
    COLOR_WHITE, COLOR_GRID_LINE, COLOR_GRID_DOT
)
from particles import GlowManager, SparkParticle

class BootAnimation:
    def __init__(self, audio_manager):
        self.audio = audio_manager
        self.timer = 0.0
        self.completed = False
        self.fast_forward = False
        
        # Audio triggers
        self.played_boot = False
        self.played_sweep = False
        self.logged_lines = 0
        
        # Diagnostics terminal log lines
        self.boot_logs = [
            ("INIT", "HYPERION DISPLAY MATRIX INITIALIZING..."),
            ("GRID", f"CALIBRATING TOPOLOGY [{GRID_COLS}x{GRID_ROWS}] ONLINE"),
            ("LINK", "SYNAPSE NEURAL LINK: ESTABLISHED (100%)"),
            ("CORE", "CYBER VIPER PROTOCOLS LOADED. READY."),
        ]
        
        # Decorative particles
        self.particles = []
        
        # Fonts
        self._init_fonts()

    def _init_fonts(self):
        try:
            self.mono_font = pygame.font.SysFont("dejavusansmono", 16, bold=True)
            self.title_font = pygame.font.SysFont("dejavusansmono", 48, bold=True)
            self.sub_font = pygame.font.SysFont("dejavusansmono", 18, bold=True)
            self.legend_font = pygame.font.SysFont("dejavusansmono", 14)
        except Exception:
            self.mono_font = pygame.font.Font(None, 20)
            self.title_font = pygame.font.Font(None, 64)
            self.sub_font = pygame.font.Font(None, 24)
            self.legend_font = pygame.font.Font(None, 18)

    def handle_event(self, event):
        """Allows skipping animation with Arrow keys, Space, or Enter."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                if self.timer < 3.2:
                    self.timer = 3.2  # Fast forward to ready screen
                    return None
                else:
                    self.completed = True
                    return (1, 0) # Default start right
            elif event.key in (pygame.K_UP, pygame.K_w):
                if self.timer < 3.2:
                    self.timer = 3.2
                    return None
                self.completed = True
                return (0, -1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if self.timer < 3.2:
                    self.timer = 3.2
                    return None
                self.completed = True
                return (0, 1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                if self.timer < 3.2:
                    self.timer = 3.2
                    return None
                self.completed = True
                return (-1, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if self.timer < 3.2:
                    self.timer = 3.2
                    return None
                self.completed = True
                return (1, 0)
        return None

    def update(self, dt):
        self.timer += dt

        # Play boot sound once at start
        if not self.played_boot:
            self.audio.play_boot()
            self.played_boot = True

        # Terminal log line beep triggers
        lines_to_show = min(len(self.boot_logs), int(self.timer / 0.32))
        if lines_to_show > self.logged_lines:
            self.audio.play_beep()
            self.logged_lines = lines_to_show

        # Particle updates
        self.particles = [p for p in self.particles if p.update(dt)]

        # Spawn bursts when logo appears at t = 2.4s
        if 2.4 <= self.timer <= 2.5 and len(self.particles) < 30:
            for _ in range(35):
                self.particles.append(SparkParticle(SCREEN_WIDTH // 2, 280, COLOR_CYAN, speed_mult=1.5))
                self.particles.append(SparkParticle(SCREEN_WIDTH // 2, 280, COLOR_MAGENTA, speed_mult=1.2))

    def draw(self, surface):
        surface.fill(COLOR_BG_DARK)

        # Stage 0: CRT Power On Flash & Expansion (0.0s - 1.2s)
        if self.timer < 1.0:
            self._draw_crt_turn_on(surface)
            return

        # Stage 1: Laser Scanlines & Grid Calibration (1.0s - 2.4s)
        self._draw_grid_sweep(surface)

        # Draw Diagnostics Terminal Log in bottom corner
        self._draw_terminal_logs(surface)

        # Stage 2: Logo reveal & Press Arrow Key prompt (2.4s+)
        if self.timer >= 2.2:
            self._draw_title_reveal(surface)

        # Draw active intro particles
        for p in self.particles:
            p.draw(surface)

        # CRT Scanline overlay effect
        self._draw_scanlines(surface)

    def _draw_crt_turn_on(self, surface):
        """Simulates vintage sci-fi CRT aperture ignite and vertical bloom."""
        t = self.timer / 1.0
        center_y = SCREEN_HEIGHT // 2
        
        if t < 0.35:
            # Horizontal bright beam firing across screen
            progress = t / 0.35
            line_w = int(SCREEN_WIDTH * progress)
            x_start = (SCREEN_WIDTH - line_w) // 2
            pygame.draw.line(surface, (255, 255, 255), (x_start, center_y), (x_start + line_w, center_y), 3)
            GlowManager.draw_glow(surface, (SCREEN_WIDTH // 2, center_y), 50, COLOR_CYAN)
        else:
            # Vertical expansion of screen brightness
            expand_prog = (t - 0.35) / 0.65
            h = int(SCREEN_HEIGHT * (expand_prog ** 2.2))
            top = max(0, center_y - h // 2)
            glow_rect = pygame.Surface((SCREEN_WIDTH, max(2, h)), pygame.SRCALPHA)
            glow_rect.fill((0, 240, 255, int(180 * (1.0 - expand_prog * 0.7))))
            surface.blit(glow_rect, (0, top), special_flags=pygame.BLEND_ADD)
            pygame.draw.line(surface, (255, 255, 255), (0, center_y - h // 2), (SCREEN_WIDTH, center_y - h // 2), 2)
            pygame.draw.line(surface, (255, 255, 255), (0, center_y + h // 2), (SCREEN_WIDTH, center_y + h // 2), 2)

    def _draw_grid_sweep(self, surface):
        """Draws arena grid being activated by laser sweep beams."""
        progress = min(1.0, (self.timer - 1.0) / 1.4)
        
        # Arena boundary border glow
        border_rect = pygame.Rect(ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT)
        pygame.draw.rect(surface, (15, 24, 45), border_rect)
        pygame.draw.rect(surface, (0, 160, 220), border_rect, 2)

        # Draw grid lines up to sweep progress
        sweep_x = ARENA_X + int(ARENA_WIDTH * progress)
        sweep_y = ARENA_Y + int(ARENA_HEIGHT * progress)

        # Vertical grid lines
        for c in range(GRID_COLS + 1):
            gx = ARENA_X + c * CELL_SIZE
            if gx <= sweep_x:
                dist_factor = max(0.2, 1.0 - abs(gx - sweep_x) / 150.0)
                col = (int(18 + 40 * dist_factor), int(25 + 100 * dist_factor), int(45 + 150 * dist_factor))
                pygame.draw.line(surface, col, (gx, ARENA_Y), (gx, ARENA_Y + ARENA_HEIGHT), 1)

        # Horizontal grid lines
        for r in range(GRID_ROWS + 1):
            gy = ARENA_Y + r * CELL_SIZE
            if gy <= sweep_y:
                dist_factor = max(0.2, 1.0 - abs(gy - sweep_y) / 150.0)
                col = (int(18 + 40 * dist_factor), int(25 + 100 * dist_factor), int(45 + 150 * dist_factor))
                pygame.draw.line(surface, col, (ARENA_X, gy), (ARENA_X + ARENA_WIDTH, gy), 1)

        # Glowing Laser sweep beams
        if progress < 1.0:
            # Vertical laser sweep line
            laser_v = pygame.Surface((6, ARENA_HEIGHT), pygame.SRCALPHA)
            laser_v.fill((0, 255, 255, 230))
            surface.blit(laser_v, (sweep_x - 3, ARENA_Y), special_flags=pygame.BLEND_ADD)
            GlowManager.draw_glow(surface, (sweep_x, ARENA_Y + ARENA_HEIGHT // 2), 60, (0, 255, 255))

            # Horizontal laser sweep line
            laser_h = pygame.Surface((ARENA_WIDTH, 6), pygame.SRCALPHA)
            laser_h.fill((255, 40, 180, 230))
            surface.blit(laser_h, (ARENA_X, sweep_y - 3), special_flags=pygame.BLEND_ADD)
            GlowManager.draw_glow(surface, (ARENA_X + ARENA_WIDTH // 2, sweep_y), 60, (255, 40, 180))

    def _draw_terminal_logs(self, surface):
        """Displays boot diagnostic messages in cyber terminal style."""
        lines_to_show = min(len(self.boot_logs), int(self.timer / 0.32))
        base_x = ARENA_X + 20
        base_y = ARENA_Y + ARENA_HEIGHT - 110

        for i in range(lines_to_show):
            tag, msg = self.boot_logs[i]
            y = base_y + i * 22
            
            # Draw tag box
            tag_surf = self.mono_font.render(f"[{tag}]", True, COLOR_CYAN)
            surface.blit(tag_surf, (base_x, y))
            
            # Draw message
            msg_surf = self.mono_font.render(f" {msg}", True, (180, 220, 255))
            surface.blit(msg_surf, (base_x + 65, y))

    def _draw_title_reveal(self, surface):
        """Draws holographic title with chromatic aberration and arrow key prompt."""
        reveal_prog = min(1.0, (self.timer - 2.2) / 0.6)
        alpha = int(255 * reveal_prog)
        
        center_x = SCREEN_WIDTH // 2
        center_y = ARENA_Y + 160

        title_text = "N E O  S N A K E"
        
        # Chromatic Aberration Layer: Red/Magenta offset
        mag_surf = self.title_font.render(title_text, True, COLOR_MAGENTA)
        mag_surf.set_alpha(int(alpha * 0.75))
        surface.blit(mag_surf, mag_surf.get_rect(center=(center_x - 3, center_y + 1)))

        # Chromatic Aberration Layer: Cyan offset
        cyan_surf = self.title_font.render(title_text, True, COLOR_CYAN)
        cyan_surf.set_alpha(int(alpha * 0.75))
        surface.blit(cyan_surf, cyan_surf.get_rect(center=(center_x + 3, center_y - 1)))

        # Core Sharp White Layer
        white_surf = self.title_font.render(title_text, True, COLOR_WHITE)
        white_surf.set_alpha(alpha)
        surface.blit(white_surf, white_surf.get_rect(center=(center_x, center_y)))

        # Outer Soft Title Glow
        GlowManager.draw_glow(surface, (center_x, center_y), 110, (0, 220, 255))

        # Subtitle
        sub_text = "CYBERNETIC ARCADIA PROTOCOL"
        sub_surf = self.sub_font.render(sub_text, True, COLOR_GOLD)
        sub_surf.set_alpha(alpha)
        surface.blit(sub_surf, sub_surf.get_rect(center=(center_x, center_y + 44)))

        # Pulsing Call-To-Action Prompt
        pulse = 0.5 + 0.5 * math.sin(self.timer * 6.0)
        prompt_alpha = int(255 * pulse)
        
        prompt_text = "► PRESS ANY ARROW KEY TO INITIALIZE ◄"
        prompt_surf = self.sub_font.render(prompt_text, True, COLOR_CYAN)
        prompt_surf.set_alpha(prompt_alpha)
        surface.blit(prompt_surf, prompt_surf.get_rect(center=(center_x, ARENA_Y + 340)))

        # Arrow Keys Graphic Guide
        self._draw_arrow_controls_guide(surface, center_x, ARENA_Y + 410, alpha)

    def _draw_arrow_controls_guide(self, surface, cx, cy, alpha):
        """Draws a stylish visual diagram of Arrow Keys."""
        btn_w, btn_h = 34, 30
        
        # Key Layout: Up above, Left Down Right below
        keys = [
            ("▲", cx, cy - 20),
            ("◄", cx - 44, cy + 18),
            ("▼", cx, cy + 18),
            ("►", cx + 44, cy + 18),
        ]

        for symbol, kx, ky in keys:
            rect = pygame.Rect(kx - btn_w // 2, ky - btn_h // 2, btn_w, btn_h)
            
            # Key background box
            box_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            box_surf.fill((16, 28, 54, alpha))
            pygame.draw.rect(box_surf, (0, 240, 255, alpha), (0, 0, btn_w, btn_h), 1, border_radius=4)
            surface.blit(box_surf, rect.topleft)

            # Key arrow icon
            arrow_surf = self.mono_font.render(symbol, True, COLOR_WHITE)
            arrow_surf.set_alpha(alpha)
            surface.blit(arrow_surf, arrow_surf.get_rect(center=(kx, ky)))

        # Small footnote
        hint_surf = self.legend_font.render("WASD ALSO SUPPORTED  •  [SPACE] SKIP INTRO", True, (130, 160, 200))
        hint_surf.set_alpha(alpha)
        surface.blit(hint_surf, hint_surf.get_rect(center=(cx, cy + 56)))

    def _draw_scanlines(self, surface):
        """Tasteful arcade CRT scanline overlay."""
        # Draw sparse horizontal scanlines every 4 pixels
        scanline_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(scanline_surf, (0, 0, 0, 32), (0, y), (SCREEN_WIDTH, y))
        surface.blit(scanline_surf, (0, 0))
