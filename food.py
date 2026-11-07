"""
Food entities: Neon Apple and Quantum Golden Core.
Visualized with glowing cores, orbiting rings, and smooth pulsing animations.
"""

import math
import random
import pygame
from config import (
    CELL_SIZE, ARENA_X, ARENA_Y, GRID_COLS, GRID_ROWS,
    COLOR_FOOD_NORMAL, COLOR_FOOD_NORMAL_GLOW,
    COLOR_FOOD_BONUS, COLOR_FOOD_BONUS_GLOW
)
from particles import GlowManager

class Food:
    def __init__(self):
        self.grid_x = 0
        self.grid_y = 0
        self.anim_timer = 0.0
        
        # Bonus food properties
        self.bonus_active = False
        self.bonus_x = 0
        self.bonus_y = 0
        self.bonus_duration = 7.5
        self.bonus_timer = 0.0
        self.bonus_rot_angle = 0.0

    def spawn(self, snake_positions):
        """Randomly pick an unoccupied cell on the grid."""
        occupied = set(snake_positions)
        if self.bonus_active:
            occupied.add((self.bonus_x, self.bonus_y))
            
        free_cells = [
            (x, y) for x in range(GRID_COLS) for y in range(GRID_ROWS)
            if (x, y) not in occupied
        ]
        if free_cells:
            self.grid_x, self.grid_y = random.choice(free_cells)

    def spawn_bonus(self, snake_positions):
        """Spawn the rare Quantum Golden Core."""
        occupied = set(snake_positions)
        occupied.add((self.grid_x, self.grid_y))
        
        free_cells = [
            (x, y) for x in range(GRID_COLS) for y in range(GRID_ROWS)
            if (x, y) not in occupied
        ]
        if free_cells:
            self.bonus_x, self.bonus_y = random.choice(free_cells)
            self.bonus_active = True
            self.bonus_timer = self.bonus_duration
            return True
        return False

    def get_pixel_pos(self, gx, gy):
        px = ARENA_X + gx * CELL_SIZE + CELL_SIZE // 2
        py = ARENA_Y + gy * CELL_SIZE + CELL_SIZE // 2
        return px, py

    def update(self, dt):
        self.anim_timer += dt
        self.bonus_rot_angle += dt * 3.5
        
        if self.bonus_active:
            self.bonus_timer -= dt
            if self.bonus_timer <= 0:
                self.bonus_active = False
                return "bonus_expired"
        return None

    def draw(self, surface):
        px, py = self.get_pixel_pos(self.grid_x, self.grid_y)
        
        # Bobbing floating motion
        bob = math.sin(self.anim_timer * 4.0) * 2.5
        draw_y = py + bob

        # 1. Pulsing Outer Glow
        pulse = 0.75 + 0.25 * math.sin(self.anim_timer * 6.0)
        glow_radius = int(24 * pulse)
        GlowManager.draw_glow(surface, (px, draw_y), glow_radius, COLOR_FOOD_NORMAL_GLOW)

        # 2. Main Apple Orb Body
        core_radius = int((CELL_SIZE * 0.36) * (0.95 + 0.05 * pulse))
        pygame.draw.circle(surface, COLOR_FOOD_NORMAL, (int(px), int(draw_y)), core_radius)

        # 3. Inner Glossy Highlight
        high_r = max(2, int(core_radius * 0.4))
        high_x = int(px - core_radius * 0.32)
        high_y = int(draw_y - core_radius * 0.32)
        pygame.draw.circle(surface, (255, 200, 220), (high_x, high_y), high_r)

        # 4. Digital Leaf / Stem
        leaf_x = int(px)
        leaf_y = int(draw_y - core_radius - 2)
        pygame.draw.line(surface, (0, 255, 180), (leaf_x, leaf_y + 2), (leaf_x + 3, leaf_y - 3), 2)
        pygame.draw.circle(surface, (0, 255, 180), (leaf_x + 3, leaf_y - 3), 2)

        # 5. Orbiting energy sparks
        orbit_r = core_radius + 6
        for i in range(2):
            ang = self.anim_timer * 3.0 + i * math.pi
            ox = px + math.cos(ang) * orbit_r
            oy = draw_y + math.sin(ang) * (orbit_r * 0.6)
            pygame.draw.circle(surface, (255, 240, 240), (int(ox), int(oy)), 2)

        # Draw Bonus Food if active
        if self.bonus_active:
            self._draw_bonus(surface)

    def _draw_bonus(self, surface):
        bpx, bpy = self.get_pixel_pos(self.bonus_x, self.bonus_y)
        bob = math.sin(self.anim_timer * 6.0) * 3.0
        draw_y = bpy + bob

        # Glowing golden aura
        pulse = 0.8 + 0.2 * math.sin(self.anim_timer * 10.0)
        GlowManager.draw_glow(surface, (bpx, draw_y), int(34 * pulse), COLOR_FOOD_BONUS_GLOW)

        # Spinning gyroscope orbital rings
        ring_rad = int(CELL_SIZE * 0.48)
        ang1 = self.bonus_rot_angle
        ang2 = -self.bonus_rot_angle * 1.3

        # Draw rotating ring 1
        ring_pts1 = []
        for i in range(16):
            theta = (i / 16.0) * 2 * math.pi
            rx = math.cos(theta) * ring_rad
            ry = math.sin(theta) * (ring_rad * 0.45)
            # Rotate by ang1
            rx_rot = rx * math.cos(ang1) - ry * math.sin(ang1)
            ry_rot = rx * math.sin(ang1) + ry * math.cos(ang1)
            ring_pts1.append((int(bpx + rx_rot), int(draw_y + ry_rot)))
        if len(ring_pts1) > 2:
            pygame.draw.lines(surface, (255, 240, 150), True, ring_pts1, 2)

        # Draw rotating ring 2
        ring_pts2 = []
        for i in range(16):
            theta = (i / 16.0) * 2 * math.pi
            rx = math.cos(theta) * (ring_rad * 0.8)
            ry = math.sin(theta) * (ring_rad * 0.4)
            rx_rot = rx * math.cos(ang2) - ry * math.sin(ang2)
            ry_rot = rx * math.sin(ang2) + ry * math.cos(ang2)
            ring_pts2.append((int(bpx + rx_rot), int(draw_y + ry_rot)))
        if len(ring_pts2) > 2:
            pygame.draw.lines(surface, (255, 215, 0), True, ring_pts2, 2)

        # Golden Core Orb
        core_r = int(CELL_SIZE * 0.28)
        pygame.draw.circle(surface, (255, 255, 230), (int(bpx), int(draw_y)), core_r)
        pygame.draw.circle(surface, COLOR_FOOD_BONUS, (int(bpx), int(draw_y)), int(core_r * 0.75))

        # Circular countdown gauge
        time_ratio = max(0.0, self.bonus_timer / self.bonus_duration)
        gauge_radius = int(CELL_SIZE * 0.58)
        gauge_rect = pygame.Rect(bpx - gauge_radius, draw_y - gauge_radius, gauge_radius * 2, gauge_radius * 2)
        start_angle = math.pi / 2
        end_angle = start_angle + (2 * math.pi * time_ratio)
        if time_ratio > 0.05:
            pygame.draw.arc(surface, (255, 220, 50), gauge_rect, start_angle, end_angle, 2)
