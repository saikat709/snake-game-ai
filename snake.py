"""
Snake representation with smooth movement interpolation, gradient body rendering,
cybernetic head with directional optical sensors, and responsive input buffering.
"""

import math
from collections import deque
import pygame
from config import (
    CELL_SIZE, ARENA_X, ARENA_Y, GRID_COLS, GRID_ROWS,
    COLOR_SNAKE_HEAD, COLOR_SNAKE_BODY_START,
    COLOR_SNAKE_BODY_MID, COLOR_SNAKE_BODY_END,
    COLOR_SNAKE_EYE, COLOR_SNAKE_PUPIL
)
from particles import GlowManager

# Direction Constants
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

OPPOSITE = {
    DIR_UP: DIR_DOWN,
    DIR_DOWN: DIR_UP,
    DIR_LEFT: DIR_RIGHT,
    DIR_RIGHT: DIR_LEFT,
}

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        # Initial 4-segment snake centered in the arena
        mid_x = GRID_COLS // 2
        mid_y = GRID_ROWS // 2
        self.positions = [
            (mid_x, mid_y),
            (mid_x - 1, mid_y),
            (mid_x - 2, mid_y),
            (mid_x - 3, mid_y)
        ]
        self.prev_positions = list(self.positions)
        self.direction = DIR_RIGHT
        self.input_queue = deque()
        self.grow_pending = 0
        self.alive = True
        self.eye_blink_timer = 0.0

    def handle_input(self, new_dir):
        """Buffer direction input to ensure silky-smooth responsive cornering."""
        if not new_dir:
            return
        # Compare with the last queued direction or current direction
        last_dir = self.input_queue[-1] if self.input_queue else self.direction
        if new_dir != last_dir and new_dir != OPPOSITE.get(last_dir):
            if len(self.input_queue) < 2:
                self.input_queue.append(new_dir)

    def update_tick(self):
        """Execute one logic step on the grid."""
        if not self.alive:
            return None

        # Store previous positions for smooth visual interpolation
        self.prev_positions = list(self.positions)

        # Apply queued direction if available
        if self.input_queue:
            self.direction = self.input_queue.popleft()

        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Wall collision check
        if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
            self.alive = False
            return "collision_wall"

        # Self collision check (ignoring the tail if not growing)
        body_to_check = self.positions[:-1] if self.grow_pending == 0 else self.positions
        if new_head in body_to_check:
            self.alive = False
            return "collision_self"

        # Advance snake
        self.positions.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
            # Adjust prev_positions to match new length
            self.prev_positions.append(self.prev_positions[-1])
        else:
            self.positions.pop()

        return "moved"

    def grow(self, count=1):
        self.grow_pending += count

    def get_interpolated_pixels(self, alpha):
        """Calculate smooth interpolated (x, y) coordinates for all segments."""
        alpha = max(0.0, min(1.0, alpha))
        pixel_positions = []
        
        # Ensure prev_positions matches positions length
        while len(self.prev_positions) < len(self.positions):
            self.prev_positions.append(self.positions[-1])

        for curr, prev in zip(self.positions, self.prev_positions):
            # Check for wrap-around distance if any, but since we have walls it's direct
            interp_x = prev[0] + (curr[0] - prev[0]) * alpha
            interp_y = prev[1] + (curr[1] - prev[1]) * alpha
            px = ARENA_X + interp_x * CELL_SIZE + CELL_SIZE / 2.0
            py = ARENA_Y + interp_y * CELL_SIZE + CELL_SIZE / 2.0
            pixel_positions.append((px, py))
            
        return pixel_positions

    def _interpolate_color(self, c1, c2, factor):
        factor = max(0.0, min(1.0, factor))
        return (
            int(c1[0] + (c2[0] - c1[0]) * factor),
            int(c1[1] + (c2[1] - c1[1]) * factor),
            int(c1[2] + (c2[2] - c1[2]) * factor)
        )

    def get_segment_color(self, index, total):
        """Returns a multi-stop vibrant neon gradient from Head to Tail."""
        if total <= 1:
            return COLOR_SNAKE_HEAD
        ratio = index / (total - 1)
        if ratio < 0.45:
            # Head Cyan -> Mid Emerald
            return self._interpolate_color(COLOR_SNAKE_BODY_START, COLOR_SNAKE_BODY_MID, ratio / 0.45)
        else:
            # Mid Emerald -> Tail Violet
            return self._interpolate_color(COLOR_SNAKE_BODY_MID, COLOR_SNAKE_BODY_END, (ratio - 0.45) / 0.55)

    def draw(self, surface, alpha, dt=0.016):
        pixel_positions = self.get_interpolated_pixels(alpha)
        total = len(pixel_positions)
        if total == 0:
            return

        self.eye_blink_timer += dt

        # 1. Glow for Head and Upper Body
        head_px, head_py = pixel_positions[0]
        GlowManager.draw_glow(surface, (head_px, head_py), int(CELL_SIZE * 1.5), COLOR_SNAKE_HEAD)

        # 2. Draw Connected Cybernetic Body Segments
        # Draw connections between adjacent segments first
        for i in range(total - 1, 0, -1):
            p1 = pixel_positions[i]
            p2 = pixel_positions[i - 1]
            seg_col = self.get_segment_color(i, total)
            radius = max(4.0, (CELL_SIZE * 0.42) * (1.0 - (i / total) * 0.35))
            pygame.draw.line(surface, seg_col, p1, p2, int(radius * 2))

        # Draw glowing inner spinal line along the whole body
        if total >= 2:
            spine_pts = [(int(p[0]), int(p[1])) for p in pixel_positions]
            pygame.draw.lines(surface, (230, 255, 255), False, spine_pts, 3)

        # Draw rounded capsules for each segment
        for i in range(total - 1, -1, -1):
            px, py = pixel_positions[i]
            seg_col = self.get_segment_color(i, total)
            radius = max(4.0, (CELL_SIZE * 0.44) * (1.0 - (i / total) * 0.35))
            
            # Base segment
            pygame.draw.circle(surface, seg_col, (int(px), int(py)), int(radius))
            
            # Subtle core highlight
            inner_r = max(2, int(radius * 0.45))
            pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), inner_r)

        # 3. Draw Cybernetic Head & Directional Optics (Eyes)
        self._draw_head_details(surface, head_px, head_py, total)

    def _draw_head_details(self, surface, hx, hy, total):
        # Calculate angle of travel based on current direction
        dx, dy = self.direction
        angle = math.atan2(dy, dx)

        head_radius = CELL_SIZE * 0.46

        # Draw directional visor / head armor
        armor_front_x = hx + math.cos(angle) * (head_radius * 0.6)
        armor_front_y = hy + math.sin(angle) * (head_radius * 0.6)
        pygame.draw.circle(surface, (255, 255, 255), (int(armor_front_x), int(armor_front_y)), 3)

        # Eye offset perpendicular to travel direction
        perp_angle = angle + math.pi / 2
        eye_dist = head_radius * 0.58
        eye_forward = head_radius * 0.35

        eye1_x = hx + math.cos(angle) * eye_forward + math.cos(perp_angle) * eye_dist
        eye1_y = hy + math.sin(angle) * eye_forward + math.sin(perp_angle) * eye_dist

        eye2_x = hx + math.cos(angle) * eye_forward - math.cos(perp_angle) * eye_dist
        eye2_y = hy + math.sin(angle) * eye_forward - math.sin(perp_angle) * eye_dist

        # Blinking logic (blink every 4 seconds for 0.15s)
        is_blinking = (self.eye_blink_timer % 4.0) > 3.85

        for ex, ey in [(eye1_x, eye1_y), (eye2_x, eye2_y)]:
            if is_blinking:
                # Eyelid slit
                pygame.draw.line(surface, COLOR_SNAKE_EYE, (int(ex - 3), int(ey)), (int(ex + 3), int(ey)), 2)
            else:
                # Glowing Cyber Optic Lens
                pygame.draw.circle(surface, COLOR_SNAKE_EYE, (int(ex), int(ey)), 4)
                # Pupil oriented towards travel direction
                px = ex + math.cos(angle) * 1.5
                py = ey + math.sin(angle) * 1.5
                pygame.draw.circle(surface, COLOR_SNAKE_PUPIL, (int(px), int(py)), 2)
