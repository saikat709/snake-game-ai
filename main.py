"""
Neo Snake - Cyberpunk Edition
A modern, polished snake game built with Pygame featuring:
- Dramatic screen initialization boot sequence
- Smooth 60 FPS motion interpolation and glow effects
- Full arrow-key responsiveness with queued inputs
- Dynamic combo multiplier and rare quantum food
- Procedural audio synthesizer (no external audio assets required)
- CRT scanlines, screen shake, and particle explosions
"""

import sys
import time
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS,
    INITIAL_SNAKE_SPEED, MAX_SNAKE_SPEED, SPEED_INCREMENT,
    COMBO_TIMEOUT, COLOR_BG_DARK, COLOR_CYAN, COLOR_GOLD,
    COLOR_FOOD_NORMAL, COLOR_FOOD_BONUS,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)
from audio import AudioManager
from particles import ParticleSystem
from food import Food
from snake import Snake
from boot_anim import BootAnimation
from ui import UIManager

# Game States
STATE_BOOT = "BOOT"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_GAME_OVER = "GAME_OVER"

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("NEO SNAKE // CYBER VIPER")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.render_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Audio & Systems
        self.audio = AudioManager()
        self.ui = UIManager()
        self.arena_rect = pygame.Rect(148, 110, 728, 572)
        self.particles = ParticleSystem(self.arena_rect)
        self.snake = Snake()
        self.food = Food()
        self.boot_anim = BootAnimation(self.audio)

        # State Variables
        self.state = STATE_BOOT
        self.score = 0
        self.apples_eaten = 0
        self.combo = 1
        self.max_combo = 1
        self.combo_timer = 0.0
        self.game_time = 0.0
        
        # Speed & Timing
        self.snake_speed = INITIAL_SNAKE_SPEED
        self.tick_duration = 1.0 / self.snake_speed
        self.time_since_tick = 0.0

        # Ready state
        self.food.spawn(self.snake.positions)

    def reset_game(self, initial_dir=DIR_RIGHT):
        """Reset game variables for a fresh run."""
        self.snake.reset()
        if initial_dir:
            self.snake.direction = initial_dir
        self.food = Food()
        self.food.spawn(self.snake.positions)
        self.score = 0
        self.apples_eaten = 0
        self.combo = 1
        self.max_combo = 1
        self.combo_timer = 0.0
        self.game_time = 0.0
        self.snake_speed = INITIAL_SNAKE_SPEED
        self.tick_duration = 1.0 / self.snake_speed
        self.time_since_tick = 0.0
        self.ui.is_new_record = False
        self.state = STATE_PLAYING

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Toggle audio with 'M' at any state
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.audio.toggle_mute()
                continue

            # State-specific event handling
            if self.state == STATE_BOOT:
                chosen_dir = self.boot_anim.handle_event(event)
                if self.boot_anim.completed:
                    self.reset_game(initial_dir=chosen_dir or DIR_RIGHT)

            elif self.state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.snake.handle_input(DIR_UP)
                        self.audio.play_turn()
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.handle_input(DIR_DOWN)
                        self.audio.play_turn()
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.handle_input(DIR_LEFT)
                        self.audio.play_turn()
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.handle_input(DIR_RIGHT)
                        self.audio.play_turn()
                    elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.state = STATE_PAUSED
                    elif event.key == pygame.K_r:
                        self.reset_game()

            elif self.state == STATE_PAUSED:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.state = STATE_PLAYING
                    elif event.key == pygame.K_r:
                        self.reset_game()

            elif self.state == STATE_GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_r, pygame.K_RETURN):
                        self.reset_game(DIR_RIGHT)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.reset_game(DIR_UP)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.reset_game(DIR_DOWN)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.reset_game(DIR_LEFT)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.reset_game(DIR_RIGHT)

        return True

    def update(self, dt):
        if self.state == STATE_BOOT:
            self.boot_anim.update(dt)

        elif self.state == STATE_PLAYING:
            self.game_time += dt
            self.ui.update(dt, self.score)
            self.particles.update(dt)

            # Update Combo timer
            if self.combo > 1:
                self.combo_timer -= dt
                if self.combo_timer <= 0:
                    self.combo = 1

            # Update Food animation & check bonus expiration
            food_event = self.food.update(dt)
            if food_event == "bonus_expired":
                bpx, bpy = self.food.get_pixel_pos(self.food.bonus_x, self.food.bonus_y)
                self.particles.spawn_eat_burst(bpx, bpy, (180, 160, 100), count=10)

            # Accumulate time for discrete snake ticks
            self.time_since_tick += dt
            self.tick_duration = 1.0 / self.snake_speed

            while self.time_since_tick >= self.tick_duration:
                self.time_since_tick -= self.tick_duration
                result = self.snake.update_tick()

                if result in ("collision_wall", "collision_self"):
                    self.trigger_game_over()
                    return

                # Check Food Collision
                head_pos = self.snake.positions[0]

                # 1. Normal Food
                if head_pos == (self.food.grid_x, self.food.grid_y):
                    self.on_eat_normal_food()

                # 2. Quantum Bonus Food
                if self.food.bonus_active and head_pos == (self.food.bonus_x, self.food.bonus_y):
                    self.on_eat_bonus_food()

        elif self.state == STATE_GAME_OVER:
            self.ui.update(dt, self.score)
            self.particles.update(dt)

    def on_eat_normal_food(self):
        """Handles eating regular neon apple."""
        self.apples_eaten += 1
        
        # Combo logic
        if self.combo_timer > 0:
            self.combo = min(5, self.combo + 1)
        else:
            self.combo = 1
        self.max_combo = max(self.max_combo, self.combo)
        self.combo_timer = COMBO_TIMEOUT

        # Score & Speed
        points = 10 * self.combo
        self.score += points
        self.snake_speed = min(MAX_SNAKE_SPEED, self.snake_speed + SPEED_INCREMENT)
        self.snake.grow(1)

        # Audio & FX
        self.audio.play_eat(self.combo)
        px, py = self.food.get_pixel_pos(self.food.grid_x, self.food.grid_y)
        self.particles.spawn_eat_burst(px, py, COLOR_FOOD_NORMAL)
        
        # Floating score text popup
        combo_str = f" x{self.combo}" if self.combo > 1 else ""
        self.particles.spawn_text(px, py - 10, f"+{points}{combo_str}", COLOR_CYAN, self.ui.font_mid)

        # Spawn next apple
        self.food.spawn(self.snake.positions)

        # Chance to spawn Quantum Bonus food every 6 apples
        if not self.food.bonus_active and (self.apples_eaten % 6 == 0):
            if self.food.spawn_bonus(self.snake.positions):
                self.audio.play_bonus_spawn()
                bpx, bpy = self.food.get_pixel_pos(self.food.bonus_x, self.food.bonus_y)
                self.particles.spawn_text(bpx, bpy - 20, "QUANTUM CORE DETECTED!", COLOR_GOLD, self.ui.font_mid)

    def on_eat_bonus_food(self):
        """Handles collecting the rare golden quantum core."""
        bonus_points = 50 * self.combo
        self.score += bonus_points
        self.food.bonus_active = False
        self.combo = min(5, self.combo + 1)
        self.max_combo = max(self.max_combo, self.combo)
        self.combo_timer = COMBO_TIMEOUT + 1.5
        self.snake.grow(2)

        # Audio & FX
        self.audio.play_bonus_eat()
        bpx, bpy = self.food.get_pixel_pos(self.food.bonus_x, self.food.bonus_y)
        self.particles.spawn_bonus_burst(bpx, bpy, COLOR_FOOD_BONUS)
        self.particles.spawn_text(bpx, bpy - 15, f"+{bonus_points} OVERDRIVE!", COLOR_GOLD, self.ui.font_mid)

    def trigger_game_over(self):
        """Triggers death sequence, explosion, audio, and high score check."""
        self.state = STATE_GAME_OVER
        self.audio.play_game_over()
        self.ui.save_high_score(self.score)

        # Explode snake segments into neon sparks
        seg_pixels = []
        for i, pos in enumerate(self.snake.positions):
            px = 148 + pos[0] * 26 + 13
            py = 110 + pos[1] * 26 + 13
            col = self.snake.get_segment_color(i, len(self.snake.positions))
            seg_pixels.append((px, py, col))
        self.particles.spawn_death_burst(seg_pixels)

    def draw(self):
        # 1. Boot animation screen
        if self.state == STATE_BOOT:
            self.boot_anim.draw(self.render_surf)
            self.screen.blit(self.render_surf, (0, 0))
            pygame.display.flip()
            return

        # 2. Main Gameplay / Over / Pause Drawing
        self.render_surf.fill(COLOR_BG_DARK)

        # Draw Arena and subtle Grid
        self.ui.draw_arena_background(self.render_surf)

        # Ambient floating cyber dust
        self.particles.draw_ambient(self.render_surf)

        # Draw Food
        self.food.draw(self.render_surf)

        # Draw Snake (with smooth 60fps interpolation if alive)
        if self.snake.alive:
            alpha = self.time_since_tick / self.tick_duration
            self.snake.draw(self.render_surf, alpha, dt=0.016)

        # Draw Particle Shockwaves, Sparks & Floating Texts
        self.particles.draw_effects(self.render_surf)

        # Draw Top HUD
        self.ui.draw_hud(
            self.render_surf,
            score=self.score,
            combo=self.combo,
            combo_timer=self.combo_timer,
            max_combo_timer=COMBO_TIMEOUT,
            apples_eaten=self.apples_eaten,
            is_muted=self.audio.muted
        )

        # State overlays
        if self.state == STATE_PAUSED:
            self.ui.draw_pause_screen(self.render_surf)
        elif self.state == STATE_GAME_OVER:
            self.ui.draw_game_over(
                self.render_surf,
                final_score=self.score,
                apples_eaten=self.apples_eaten,
                max_combo=self.max_combo,
                elapsed_time=self.game_time
            )

        # Vignette & arcade CRT edge darkening
        self.ui.draw_vignette(self.render_surf)

        # Apply screen shake offset and flip display
        shake_x, shake_y = self.particles.shake.get_offset()
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.render_surf, (shake_x, shake_y))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0
            dt = min(dt, 0.05) # Prevent huge delta spikes on window focus loss

            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
