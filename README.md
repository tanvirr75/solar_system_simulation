# SOLAR SYSTEM SIMULATION: Fun Tour Around Our Solar System

An interactive 3D simulation of the solar system built with Python and OpenGL. This project offers a visually engaging and educational experience, featuring procedural textures, accurate celestial data, and multiple viewing modes.

## Description

This simulation recreates the solar system with a focus on both visual appeal and educational value. It uses PyOpenGL to render a 3D environment where users can explore the planets, learn facts about them, and even fly a spacecraft. The application includes a guided tour, a tutorial, and customizable settings.

## Features

- **3D Solar System Model**: Realistic representation of the Sun and 8 planets (Mercury to Neptune) with an asteroid belt.
- **Procedural Textures**: Unique, generated textures for the Sun and planets (e.g., fiery Sun, clouds on Earth, rings of Saturn).
- **Multiple Camera Modes**:
    - **Free View**: freely move the camera.
    - **Top Down**: overhead view of the system.
    - **Side View**: see the orbital planes.
    - **Planet Follow**: lock camera on a specific planet.
    - **Spacecraft**: fly around using a spaceship control scheme.
- **Educational Info**: Click or select planets to view scientific data (mass, diameter, orbit) and fun facts.
- **Guided Tour**: A narrated-style tour visiting each celestial body.
- **Interactive Controls**: Control simulation speed, toggle orbits, lighting, and gravity.

## Requirements

- Python 3.x
- **PyOpenGL**: `pip install PyOpenGL PyOpenGL_accelerate`

*(Note: Depending on your OS, you might need to install GLUT binaries separately if they are not included with PyOpenGL)*

## Installation

1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install PyOpenGL PyOpenGL_accelerate
   ```
3. Run the simulation:
   ```bash
   python "solar_system_simulation.py"
   ```

## Controls

### General
- **ESC**: Return to Home Screen / Exit
- **Enter**: Select Menu Item

### Simulation View
- **Space**: Pause / Resume
- **+ / -**: Increase / Decrease Speed
- **Mouse Scroll / Z / X**: Zoom In / Out
- **C**: Cycle Camera Modes (Free, Top, Side, Follow, Spacecraft)
- **0 - 8**: Select Celestial Body (0=Sun, 1=Mercury... 8=Neptune)
- **9**: Toggle Spacecraft Mode
- **O**: Toggle Orbits
- **L**: Toggle Lighting
- **G**: Toggle Gravity Visualization
- **F**: Fast Forward

### Spacecraft Mode
- **W / A / S / D**: Move Forward/Left/Back/Right
- **Q / E**: Move Up / Down

## Usage

- **Home Screen**: Navigate using Arrow Keys and Enter.
- **Settings**: Customize starting camera, speed, and defaults.
- **Guided Tour**: Sit back and watch a flyby of the solar system.

## License

This project is open for educational use and modification.
