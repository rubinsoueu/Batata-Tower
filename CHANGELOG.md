# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Basic Pygame window initialization and rendering loop.
- Simple grassy background with a zig-zag brown path.
- `Banana` enemy class with basic pathfinding, health bar, funny walking animation, and a dizzy death animation.
- `PotatoTower` class representing defense towers with an aiming mechanic (eyes looking at target).
- `Bullet` class for projectiles that seek targets and deal damage.
- Basic economy system (starting with $80, earning $6 per Banana kill).
- Wave system that speeds up enemy spawning over time.
- Placement mechanic (clicking to cost $40 and spawn a PotatoTower).
- Pixel Art procedural rendering engine (No external image assets needed).
- 3 Tower Types: Normal (Balanced), Frita (Fast/Short Range), Doce Sniper (Slow/High Damage/Long Range).
- 3 Enemy Types: Normal (Yellow), Green (Fast/Low HP), Plantain (Slow/High HP).
- Tower Upgrades: Click an existing tower to level it up (increases stats, adds piercing or AoE).
- Active Abilities: "Purê Lento" (Q) to slow enemies globally, "Bomba de Ketchup" (W) to deal massive AoE damage.
- Multiple Levels: Level 1 (Grass) and Level 2 (Desert) with diverging paths and difficulties.
- Main Menu System: Campaign Mode, Arcade Level Select, and Settings Options.
- Professional SFX and Looping Background Music via downloaded `.wav` and `.ogg` assets.

### Changed
- Project officially renamed from "Barata Tower" to "Batata Tower".
- Refactored geometry drawing to memory-based pixel art surfaces.
- Improved game loop to support state machine (MAIN_MENU, LEVEL_SELECT, SETTINGS, LEVEL_TRANSITION, PLAYING, GAMEOVER).
