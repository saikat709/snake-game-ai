"""
Cyberpunk User Interface (HUD), Scoreboards, High Score persistence,
Combos, Game Over cards, and Post-Processing overlays.
"""

import json
import os
import math
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ARENA_X, ARENA_Y,
    ARENA_WIDTH, ARENA_HEIGHT, CELL_SIZE, GRID_COLS, GRID_ROWS,
    COLOR_BG_DARK, COLOR_BG_LIGHT, COLOR_GRID_LINE, COLOR_GRID_DOT,
    COLOR_ARENA_BORDER, COLOR_ARENA_BORDER_GLOW,
    COLOR_CYAN, COLOR_GOLD, COLOR_MAGENTA, COLOR_WHITE,
    COLOR_TEXT_DIM, COLOR_PANEL_BG, COLOR_PANEL_BORDER
)
from particles import GlowManager

HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "highscore.json")

class UIManager:
    def __init__(self):
        self.displayed_score = 0
        self.high_score = self._load_high_score()
        self.is_new_record = False
        self.pulse_timer = 0.0
        self._init_fonts()
        self.vignette_surf = self._create_vignette()

    def _init_fonts(self):
        try:
            self.font_large = pygame.font.SysFont("dejavusansmono", 32, bold=True)
            self.font_mid = pygame.font.SysFont("dejavusansmono", 18, bold=True)
            self.font_small = pygame.font.SysFont("dejavusansmono", 13, bold=True)
            self.font_tiny = pygame.font.SysFont("dejavusansmono", 11)
            self.font_title = pygame.font.SysFont("dejavusansmono", 44, bold=True)
        except Exception:
            self.font_large = pygame.font.Font(None, 44)
            self.font_mid = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
            self.font_tiny = pygame.font.Font(None, 14)
            self.font_title = pygame.font.Font(None, 56)

    def _create_vignette(self):
        """Pre-renders an ambient dark vignette around the screen perimeter."""
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Vignette border strips
        for i in range(40):
            alpha = int(210 * ((40 - i) / 40.0) ** 1.8)
            col = (4, 6, 12, alpha)
            # Top, bottom, left, right strips
            pygame.draw.rect(surf, col, (0, i, SCREEN_WIDTH, 1))
            pygame.draw.rect(surf, col, (0, SCREEN_HEIGHT - 1 - i, SCREEN_WIDTH, 1))
            pygame.draw.rect(surf, col, (i, 0, 1, SCREEN_HEIGHT))
            pygame.draw.rect(surf, col, (SCREEN_WIDTH - 1 - i, 0, 1, SCREEN_HEIGHT))
        return surf

    def _load_high_score(self):
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r") as f:
                    data = json.load(f)
                    return int(data.get("high_score", 0))
            except Exception:
                pass
        return 0

    def save_high_score(self, score):
        if score > self.high_score:
            self.high_score = score
            self.is_new_record = True
            try:
                with open(HIGHSCORE_FILE, "w") as f:
                    json.dump({"high_score": self.high_score}, f)
            except Exception as e:
                print(f"[UI] Could not save highscore: {e}")

    def update(self, dt, target_score):
        self.pulse_timer += dt
        # Smoothly tick up displayed score
        if self.displayed_score < target_score:
            diff = target_score - self.displayed_score
            step = max(1, int(diff * 12 * dt))
            self.displayed_score = min(target_score, self.displayed_score + step)
        elif self.displayed_score > target_score:
            self.displayed_score = target_score

    def draw_arena_background(self, surface):
        """Draws the arena floor with cybernetic grid lines and glowing intersections."""
        # Arena Floor
        arena_rect = pygame.Rect(ARENA_X, ARENA_Y, ARENA_WIDTH, ARENA_HEIGHT)
        pygame.draw.rect(surface, (10, 14, 24), arena_rect)

        # Subtle Grid Lines
        for c in range(GRID_COLS + 1):
            gx = ARENA_X + c * CELL_SIZE
            pygame.draw.line(surface, COLOR_GRID_LINE, (gx, ARENA_Y), (gx, ARENA_Y + ARENA_HEIGHT), 1)

        for r in range(GRID_ROWS + 1):
            gy = ARENA_Y + r * CELL_SIZE
            pygame.draw.line(surface, COLOR_GRID_LINE, (ARENA_X, gy), (ARENA_X + ARENA_WIDTH, gy), 1)

        # Glowing Intersection Nodes
        for c in range(0, GRID_COLS + 1, 2):
            for r in range(0, GRID_ROWS + 1, 2):
                gx = ARENA_X + c * CELL_SIZE
                gy = ARENA_Y + r * CELL_SIZE
                pygame.draw.circle(surface, COLOR_GRID_DOT, (gx, gy), 2)

        # Outer Arena Cyber Border & Corner Brackets
        pygame.draw.rect(surface, (0, 180, 240), arena_rect, 2)
        
        # Corner aesthetic brackets
        bracket_len = 16
        corners = [
            (ARENA_X, ARENA_Y),                                     # Top-Left
            (ARENA_X + ARENA_WIDTH, ARENA_Y),                       # Top-Right
            (ARENA_X, ARENA_Y + ARENA_HEIGHT),                      # Bottom-Left
            (ARENA_X + ARENA_WIDTH, ARENA_Y + ARENA_HEIGHT)         # Bottom-Right
        ]
        
        # TL
        pygame.draw.lines(surface, COLOR_CYAN, False, [(ARENA_X, ARENA_Y + bracket_len), (ARENA_X, ARENA_Y), (ARENA_X + bracket_len, ARENA_Y)], 3)
        # TR
        pygame.draw.lines(surface, COLOR_CYAN, False, [(ARENA_X + ARENA_WIDTH - bracket_len, ARENA_Y), (ARENA_X + ARENA_WIDTH, ARENA_Y), (ARENA_X + ARENA_WIDTH, ARENA_Y + bracket_len)], 3)
        # BL
        pygame.draw.lines(surface, COLOR_CYAN, False, [(ARENA_X, ARENA_Y + ARENA_HEIGHT - bracket_len), (ARENA_X, ARENA_Y + ARENA_HEIGHT), (ARENA_X + bracket_len, ARENA_Y + ARENA_HEIGHT)], 3)
        # BR
        pygame.draw.lines(surface, COLOR_CYAN, False, [(ARENA_X + ARENA_WIDTH - bracket_len, ARENA_Y + ARENA_HEIGHT), (ARENA_X + ARENA_WIDTH, ARENA_Y + ARENA_HEIGHT), (ARENA_X + ARENA_WIDTH, ARENA_Y + ARENA_HEIGHT - bracket_len)], 3)

    def draw_hud(self, surface, score, combo, combo_timer, max_combo_timer, apples_eaten, is_muted):
        """Renders the top sci-fi HUD panel with Score, High Score, Combo gauge, and stats."""
        hud_x = ARENA_X
        hud_y = 18
        hud_w = ARENA_WIDTH
        hud_h = 76

        # HUD Panel Background
        panel_surf = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        panel_surf.fill((12, 17, 30, 235))
        pygame.draw.rect(panel_surf, (30, 48, 80), (0, 0, hud_w, hud_h), 1, border_radius=6)
        surface.blit(panel_surf, (hud_x, hud_y))

        # Bottom Neon Accent Line on HUD
        pygame.draw.line(surface, COLOR_CYAN, (hud_x + 10, hud_y + hud_h - 2), (hud_x + hud_w - 10, hud_y + hud_h - 2), 2)

        # 1. SCORE SECTION (Left)
        score_lbl = self.font_tiny.render("SCORE MATRIX", True, COLOR_TEXT_DIM)
        surface.blit(score_lbl, (hud_x + 18, hud_y + 12))
        score_val = self.font_large.render(f"{self.displayed_score:05d}", True, COLOR_CYAN)
        surface.blit(score_val, (hud_x + 16, hud_y + 28))

        # 2. HIGH SCORE SECTION
        hs_x = hud_x + 180
        hs_lbl = self.font_tiny.render("HIGH RECORD ★", True, COLOR_TEXT_DIM)
        surface.blit(hs_lbl, (hs_x, hud_y + 12))
        display_hs = max(self.high_score, score)
        hs_val = self.font_large.render(f"{display_hs:05d}", True, COLOR_GOLD)
        surface.blit(hs_val, (hs_x, hud_y + 28))

        # 3. COMBO MULTIPLIER & BAR (Center)
        combo_x = hud_x + 360
        combo_lbl = self.font_tiny.render("NEURAL MULTIPLIER", True, COLOR_TEXT_DIM)
        surface.blit(combo_lbl, (combo_x, hud_y + 12))

        combo_col = COLOR_GOLD if combo >= 3 else (COLOR_MAGENTA if combo >= 2 else COLOR_WHITE)
        combo_str = f"x{combo}" if combo > 1 else "x1"
        combo_val = self.font_large.render(combo_str, True, combo_col)
        surface.blit(combo_val, (combo_x, hud_y + 28))

        # Combo Drain Meter Bar
        meter_x = combo_x + 64
        meter_y = hud_y + 36
        meter_w = 95
        meter_h = 14
        pygame.draw.rect(surface, (20, 26, 45), (meter_x, meter_y, meter_w, meter_h), border_radius=3)
        pygame.draw.rect(surface, (45, 65, 110), (meter_x, meter_y, meter_w, meter_h), 1, border_radius=3)
        if combo > 1 and max_combo_timer > 0:
            fill_ratio = max(0.0, min(1.0, combo_timer / max_combo_timer))
            fill_w = int((meter_w - 4) * fill_ratio)
            if fill_w > 0:
                pygame.draw.rect(surface, combo_col, (meter_x + 2, meter_y + 2, fill_w, meter_h - 4), border_radius=2)

        # 4. APPLES / LENGTH (Right)
        app_x = hud_x + 550
        app_lbl = self.font_tiny.render("CORES HARVESTED", True, COLOR_TEXT_DIM)
        surface.blit(app_lbl, (app_x, hud_y + 12))
        app_val = self.font_mid.render(f"{apples_eaten:03d} UNITS", True, (0, 255, 180))
        surface.blit(app_val, (app_x, hud_y + 34))

        # 5. AUDIO & CONTROLS FOOTNOTE (Far Right)
        status_x = hud_x + hud_w - 14
        audio_text = "MUTED [M]" if is_muted else "AUDIO ON [M]"
        audio_col = (255, 90, 90) if is_muted else (130, 220, 130)
        audio_surf = self.font_tiny.render(audio_text, True, audio_col)
        surface.blit(audio_surf, audio_surf.get_rect(topright=(status_x, hud_y + 14)))

        pause_surf = self.font_tiny.render("[P] PAUSE  [R] RESTART", True, COLOR_TEXT_DIM)
        surface.blit(pause_surf, pause_surf.get_rect(topright=(status_x, hud_y + 40)))

    def draw_pause_screen(self, surface):
        """Draws frosted pause menu overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 9, 18, 195))
        surface.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        card_w, card_h = 360, 220
        card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((14, 20, 36, 245))
        pygame.draw.rect(card_surf, COLOR_CYAN, (0, 0, card_w, card_h), 2, border_radius=8)
        surface.blit(card_surf, card_rect.topleft)

        # Title
        pause_txt = self.font_large.render("SYSTEM PAUSED", True, COLOR_WHITE)
        surface.blit(pause_txt, pause_txt.get_rect(center=(cx, cy - 50)))

        # Menu options
        lines = [
            ("PRESS [P] OR [ESC] TO RESUME", COLOR_CYAN),
            ("PRESS [R] TO RESTART", COLOR_GOLD),
            ("PRESS [M] TO TOGGLE AUDIO", COLOR_WHITE),
        ]
        for idx, (text, col) in enumerate(lines):
            surf_t = self.font_small.render(text, True, col)
            surface.blit(surf_t, surf_t.get_rect(center=(cx, cy + 5 + idx * 30)))

    def draw_game_over(self, surface, final_score, apples_eaten, max_combo, elapsed_time):
        """Draws dramatic cyberpunk Game Over statistics terminal."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((12, 4, 10, 215))
        surface.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        card_w, card_h = 480, 420
        card_rect = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((16, 12, 24, 250))
        pygame.draw.rect(card_surf, (255, 45, 85), (0, 0, card_w, card_h), 2, border_radius=8)
        surface.blit(card_surf, card_rect.topleft)

        # Game Over Header
        title_surf = self.font_title.render("SYSTEM TERMINATED", True, (255, 45, 85))
        surface.blit(title_surf, title_surf.get_rect(center=(cx, cy - 155)))
        GlowManager.draw_glow(surface, (cx, cy - 155), 70, (255, 30, 80))

        sub_surf = self.font_tiny.render("NEURAL LINK COLLAPSED - CRITICAL COLLISION DETECTED", True, COLOR_TEXT_DIM)
        surface.blit(sub_surf, sub_surf.get_rect(center=(cx, cy - 118)))

        # Divider line
        pygame.draw.line(surface, (70, 30, 50), (cx - 180, cy - 100), (cx + 180, cy - 100), 1)

        # Stats Table
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        stats = [
            ("FINAL RUN SCORE", f"{final_score:05d}", COLOR_CYAN),
            ("RECORD HIGH SCORE", f"{self.high_score:05d}", COLOR_GOLD),
            ("CORES HARVESTED", f"{apples_eaten}", (0, 255, 180)),
            ("PEAK COMBO MULTIPLIER", f"x{max_combo}", COLOR_MAGENTA),
            ("ACTIVE SURVIVAL TIME", time_str, COLOR_WHITE),
        ]

        start_y = cy - 75
        for idx, (label, val, col) in enumerate(stats):
            row_y = start_y + idx * 32
            lbl_surf = self.font_mid.render(label, True, (150, 170, 200))
            surface.blit(lbl_surf, (cx - 180, row_y))

            val_surf = self.font_mid.render(val, True, col)
            surface.blit(val_surf, val_surf.get_rect(topright=(cx + 180, row_y)))

        # New High Record notification badge
        if self.is_new_record:
            badge_surf = self.font_small.render("★ NEW RECORD ACHIEVED ★", True, COLOR_GOLD)
            surface.blit(badge_surf, badge_surf.get_rect(center=(cx, cy + 98)))

        # Pulsing Restart Prompt
        pulse = 0.5 + 0.5 * math.sin(self.pulse_timer * 6.0)
        prompt_surf = self.font_mid.render("► PRESS ANY ARROW KEY TO REBOOT ◄", True, COLOR_CYAN)
        prompt_surf.set_alpha(int(255 * pulse))
        surface.blit(prompt_surf, prompt_surf.get_rect(center=(cx, cy + 145)))

        sub_prompt = self.font_tiny.render("OR PRESS [SPACE] / [R] TO RESTART", True, COLOR_TEXT_DIM)
        surface.blit(sub_prompt, sub_prompt.get_rect(center=(cx, cy + 175)))

    def draw_vignette(self, surface):
        surface.blit(self.vignette_surf, (0, 0))
