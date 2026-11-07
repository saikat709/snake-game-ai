# Neo Snake // Cyber Viper

A sleek, modern Cyberpunk-themed Snake game built with **Pygame**. Features responsive controls, an initial CRT screen initialization boot animation, smooth 60 FPS motion interpolation, dynamic neon visual effects, procedural sound synthesis, and combo multipliers.

---

## Features

- **Initial Screen Initialization Animation**:
  - Retro-futuristic CRT power-surge boot sequence.
  - Interactive terminal diagnostics with real-time audio beeps.
  - Sweeping laser scanlines and sector matrix activation.
  - Holographic title reveal with chromatic aberration.
  - Seamless launch into gameplay upon pressing any arrow key (or press Space to skip directly).

- **High-End Visuals & Modern Aesthetics**:
  - **Dynamic Multi-stop Gradient Snake**: Smooth color transition from Electric Cyan head, through Neon Emerald, to Cyber Violet tail.
  - **Fluid 60 FPS Motion Interpolation**: Mathematical sub-tick interpolation for silky-smooth movement without losing grid precision.
  - **Directional Cybernetic Head**: Reactive optic sensors (eyes) that gaze toward movement direction with animated blinks.
  - **Particle Explosions & Shockwaves**: Radial shockwaves, sparks, floating score text popups, and dynamic trauma-based screen shake.
  - **Quantum Food Cores**: Standard glowing neon apples plus rare rotating **Quantum Golden Cores** with countdown gauge and bonus overdrive score.
  - **Arcade Terminal Atmosphere**: Subtle CRT scanlines, glowing intersection nodes, and ambient vignette.

- **Procedural Audio Synthesizer**:
  - 100% self-contained synthesized retro sound effects using `pygame.mixer` buffers.
  - Zero external MP3/WAV file dependencies.
  - Progressive eat chimes that scale in pitch with your combo streak.

- **Input Buffering**:
  - Two-direction input queue prevents self-collision when cornering rapidly with arrow keys.

---

## Controls

| Key | Action |
| :--- | :--- |
| **Arrow Keys** (`↑` `↓` `←` `→`) | Move Snake / Skip Intro / Restart |
| **WASD** (`W` `A` `S` `D`) | Alternative movement controls |
| **P** or **ESC** | Pause / Resume |
| **R** | Instant Restart |
| **M** | Toggle Audio (Mute / Unmute) |
| **SPACE** / **ENTER** | Fast-forward Intro / Launch / Restart |

---

## How to Play

### Quick Start:
```bash
./run.sh
```

Or using the virtual environment:
```bash
.venv/bin/python main.py
```

---

## Project Structure

```
├── main.py        # Main game loop, states, input handling, and rendering
├── boot_anim.py   # Screen initialization boot animation sequence
├── snake.py       # Snake logic, input queue, smooth interpolation, gradient rendering
├── food.py        # Neon apples and golden quantum core food items
├── particles.py   # Particle system, glow engine, screen shake, and floating text
├── audio.py       # Procedural audio synthesizer
├── ui.py          # Cyberpunk HUD, combo gauge, high score save/load, overlays
├── config.py      # Color palettes, arena dimensions, and tuning constants
└── run.sh         # Convenient executable launcher script
```
