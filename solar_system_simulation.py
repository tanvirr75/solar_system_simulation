import sys
import time
import math
import random
import ctypes
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Global texture storage
planet_textures = {}

# -----------------------------------------------------------------------------
# Constants & Configuration
# -----------------------------------------------------------------------------
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
WINDOW_TITLE = b"Solar System Simulation - Advanced"

# Camera Modes
CAM_FREE = 0
CAM_TOP = 1
CAM_SIDE = 2
CAM_FOLLOW = 3
CAM_SPACECRAFT = 4
CAM_MODE_NAMES = {
    CAM_FREE: "Free View",
    CAM_TOP: "Top Down",
    CAM_SIDE: "Side View",
    CAM_FOLLOW: "Planet Follow",
    CAM_SPACECRAFT: "Spacecraft"
}

# Screen States
SCREEN_HOME = 0
SCREEN_SIMULATION = 1
SCREEN_TUTORIAL = 2
SCREEN_SETTINGS = 3
SCREEN_TOUR = 4  # Guided tour mode

# Menu Configuration
MENU_ITEMS = ["Start Simulation", "Guided Tour", "Tutorial", "Settings", "Exit"]
current_screen = SCREEN_HOME
menu_selection = 0
menu_starfield = None  # Will be initialized later
title_pulse_time = 0.0

# Settings defaults (can be modified in settings screen)
settings = {
    "starting_camera": CAM_FREE,
    "starting_speed": 1.0,
    "show_orbits_default": True,
    "lighting_default": True
}

# Guided Tour Configuration
TOUR_STOPS = [
    {"name": "Sun", "type": "sun", "duration": 6.0, "distance": 8.0,
     "narration": ["Welcome to the Solar System!", "Our journey begins at the Sun,", "the heart of our solar system."]},
    {"name": "Mercury", "type": "planet", "index": 0, "duration": 5.0, "distance": 5.0,
     "narration": ["Mercury - the smallest planet.", "Closest to the Sun with extreme", "temperature swings."]},
    {"name": "Venus", "type": "planet", "index": 1, "duration": 5.0, "distance": 5.0,
     "narration": ["Venus - Earth's twin in size.", "The hottest planet due to", "its thick atmosphere."]},
    {"name": "Earth", "type": "planet", "index": 2, "duration": 6.0, "distance": 5.0,
     "narration": ["Earth - our home planet.", "The only known world", "with liquid water and life."]},
    {"name": "Mars", "type": "planet", "index": 3, "duration": 5.0, "distance": 5.0,
     "narration": ["Mars - the Red Planet.", "Future target for human", "exploration and colonization."]},
    {"name": "Jupiter", "type": "planet", "index": 4, "duration": 6.0, "distance": 7.0,
     "narration": ["Jupiter - the giant!", "This massive planet could fit", "1,300 Earths inside it."]},
    {"name": "Saturn", "type": "planet", "index": 5, "duration": 6.0, "distance": 7.0,
     "narration": ["Saturn - the ringed beauty.", "Its iconic rings are made", "mostly of ice and rock."]},
    {"name": "Uranus", "type": "planet", "index": 6, "duration": 5.0, "distance": 6.0,
     "narration": ["Uranus - the sideways planet.", "It rotates on its side", "with a 98-degree tilt!"]},
    {"name": "Neptune", "type": "planet", "index": 7, "duration": 5.0, "distance": 6.0,
     "narration": ["Neptune - the windy world.", "Fastest winds in the solar system", "reaching 2,100 km/h!"]},
]

# Tour state
tour_active = False
tour_current_stop = 0
tour_stop_timer = 0.0
tour_transition_progress = 0.0
tour_transitioning = True
tour_camera_start = [0, 0, 0]
tour_camera_end = [0, 0, 0]
TOUR_TRANSITION_DURATION = 3.0  # Seconds to fly between stops

# Background Animation State
bg_planets = []  # Mini orbiting planets for homepage
shooting_stars = []  # Shooting star effects
bg_animation_time = 0.0

# Celestial Body Information (accurate scientific data + fun facts)
CELESTIAL_INFO = {
    "Sun": {
        "type": "Star",
        "diameter": "1,392,700 km",
        "mass": "1.989 x 10^30 kg",
        "surface_temp": "5,500°C",
        "facts": [
            "Contains 99.86% of solar system mass",
            "Light takes 8 min to reach Earth",
            "4.6 billion years old"
        ]
    },
    "Mercury": {
        "type": "Terrestrial Planet",
        "diameter": "4,879 km",
        "orbit_period": "88 Earth days",
        "distance": "57.9 million km",
        "facts": [
            "Smallest planet in our solar system",
            "No atmosphere - extreme temps!",
            "Day: 430°C, Night: -180°C"
        ]
    },
    "Venus": {
        "type": "Terrestrial Planet",
        "diameter": "12,104 km",
        "orbit_period": "225 Earth days",
        "distance": "108.2 million km",
        "facts": [
            "Hottest planet (465°C avg)",
            "Spins backwards (retrograde)",
            "Day longer than its year!"
        ]
    },
    "Earth": {
        "type": "Terrestrial Planet",
        "diameter": "12,742 km",
        "orbit_period": "365.25 days",
        "distance": "149.6 million km",
        "facts": [
            "Only planet with liquid water",
            "71% covered by oceans",
            "Home to 8.7 million species"
        ]
    },
    "Mars": {
        "type": "Terrestrial Planet",
        "diameter": "6,779 km",
        "orbit_period": "687 Earth days",
        "distance": "227.9 million km",
        "facts": [
            "Called the Red Planet (iron oxide)",
            "Has the largest volcano: Olympus Mons",
            "Two moons: Phobos and Deimos"
        ]
    },
    "Jupiter": {
        "type": "Gas Giant",
        "diameter": "139,820 km",
        "orbit_period": "11.86 Earth years",
        "distance": "778.5 million km",
        "facts": [
            "Largest planet (1,300 Earths fit!)",
            "Great Red Spot is a 400yr storm",
            "Has 95 known moons"
        ]
    },
    "Saturn": {
        "type": "Gas Giant",
        "diameter": "116,460 km",
        "orbit_period": "29.46 Earth years",
        "distance": "1.43 billion km",
        "facts": [
            "Famous rings are mostly ice",
            "Least dense planet (would float!)",
            "Has 146 known moons"
        ]
    },
    "Uranus": {
        "type": "Ice Giant",
        "diameter": "50,724 km",
        "orbit_period": "84 Earth years",
        "distance": "2.87 billion km",
        "facts": [
            "Rotates on its side (98° tilt!)",
            "Coldest atmosphere: -224°C",
            "Has 28 known moons"
        ]
    },
    "Neptune": {
        "type": "Ice Giant",
        "diameter": "49,244 km",
        "orbit_period": "165 Earth years",
        "distance": "4.5 billion km",
        "facts": [
            "Strongest winds: 2,100 km/h",
            "Has 16 known moons",
            "Discovered by math prediction!"
        ]
    }
}

# -----------------------------------------------------------------------------
# State Management
# -----------------------------------------------------------------------------
class SimulationState:
    def __init__(self):
        self.speed_multiplier = 1.0
        self.paused = False
        self.show_orbits = True
        self.camera_mode = CAM_FREE
        self.selected_planet_index = -1
        self.sun_selected = False  # For Sun info panel
        
        # Advanced Features
        self.lighting_enabled = True
        self.gravity_enabled = True
        self.planets_hidden = False
        
        # Spacecraft controls
        self.spacecraft_mode = False  # Toggle with '9'
        self.keys_pressed = set()  # Track held keys for smooth movement
        
        # Zoom control
        self.zoom_level = 1.0  # 1.0 = default, < 1 = closer, > 1 = farther
        self.zoom_min = 0.3
        self.zoom_max = 3.0
        
    def toggle_pause(self):
        self.paused = not self.paused

    def adjust_speed(self, delta):
        self.speed_multiplier += delta
        print(f"Speed: {self.speed_multiplier:.2f}x")

    def toggle_orbits(self):
        self.show_orbits = not self.show_orbits

    def cycle_camera(self):
        self.camera_mode = (self.camera_mode + 1) % 5  # Includes spacecraft mode
    
    def toggle_spacecraft_mode(self):
        self.spacecraft_mode = not self.spacecraft_mode
        if self.spacecraft_mode:
            self.camera_mode = CAM_SPACECRAFT
            print("Spacecraft Mode: ON (WASD to move, QE up/down)")
        else:
            self.camera_mode = CAM_FREE
            print("Spacecraft Mode: OFF")

    def select_planet(self, index):
        self.sun_selected = False  # Deselect Sun when selecting planet
        self.selected_planet_index = index if (0 <= index < 8) else -1
    
    def select_sun(self):
        self.selected_planet_index = -1  # Deselect any planet
        self.sun_selected = True
        
    def toggle_lighting(self):
        self.lighting_enabled = not self.lighting_enabled
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
        else:
            glDisable(GL_LIGHTING)
            
    def toggle_gravity(self):
        self.gravity_enabled = not self.gravity_enabled
        print(f"Gravity: {'ON' if self.gravity_enabled else 'OFF'}")
        
    def toggle_hide(self):
        self.planets_hidden = not self.planets_hidden
        
    def fast_forward(self):
        self.speed_multiplier = 5.0
        print("Fast Forward Activated (5.0x)")
    
    def adjust_zoom(self, delta):
        """Adjust zoom level (positive = zoom out, negative = zoom in)."""
        self.zoom_level += delta
        self.zoom_level = max(self.zoom_min, min(self.zoom_max, self.zoom_level))

state = SimulationState()

# -----------------------------------------------------------------------------
# Procedural Texture Generation
# -----------------------------------------------------------------------------
def noise2d(x, y, seed=0):
    """Simple pseudo-random noise function."""
    n = int(x * 374761393 + y * 668265263 + seed * 1013904223)
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 0x7fffffff) / 0x7fffffff

def fractal_noise(x, y, octaves=4, persistence=0.5, seed=0):
    """Multi-octave fractal noise."""
    total = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0
    
    for _ in range(octaves):
        total += noise2d(x * frequency, y * frequency, seed) * amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= 2.0
    
    return total / max_value

def create_texture(width, height, data):
    """Create an OpenGL texture from RGB data."""
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # Convert to bytes
    pixels = bytes(data)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, 
                 GL_RGB, GL_UNSIGNED_BYTE, pixels)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    
    return texture_id

def generate_sun_texture(size=128):
    """Generate fiery sun texture."""
    data = []
    for y in range(size):
        for x in range(size):
            u = x / size
            v = y / size
            
            # Multiple noise layers for turbulence
            n1 = fractal_noise(u * 8, v * 8, 4, 0.6, 1)
            n2 = fractal_noise(u * 16, v * 16, 3, 0.5, 2)
            
            # Hot spots
            intensity = 0.7 + n1 * 0.3 + n2 * 0.15
            
            r = min(255, int(255 * intensity))
            g = min(255, int(200 * intensity * (0.8 + n1 * 0.2)))
            b = min(255, int(50 * n2))
            
            data.extend([r, g, b])
    
    return create_texture(size, size, data)

def generate_planet_texture(name, base_color, size=128):
    """Generate procedural texture for a planet."""
    data = []
    
    # Different patterns for different planets
    for y in range(size):
        for x in range(size):
            u = x / size
            v = y / size
            
            if name == "Mercury":
                # Gray with craters
                n = fractal_noise(u * 20, v * 20, 4, 0.6, 10)
                crater = noise2d(u * 30, v * 30, 20)
                gray = 0.5 + n * 0.3 - (crater > 0.85) * 0.2
                r = g = b = int(gray * 200)
                
            elif name == "Venus":
                # Yellowish with swirly clouds
                n = fractal_noise(u * 6 + v * 2, v * 4, 5, 0.5, 30)
                r = int(220 * (0.8 + n * 0.2))
                g = int(180 * (0.7 + n * 0.3))
                b = int(100 * (0.5 + n * 0.3))
                
            elif name == "Earth":
                # Blue oceans with green/brown continents
                continent = fractal_noise(u * 8, v * 8, 5, 0.55, 50)
                is_land = continent > 0.45
                
                if is_land:
                    # Land - green to brown
                    height = (continent - 0.45) / 0.55
                    r = int(80 + height * 100)
                    g = int(120 + height * 40)
                    b = int(40 + height * 30)
                else:
                    # Ocean - blue
                    depth = 0.45 - continent
                    r = int(30 + depth * 40)
                    g = int(80 + depth * 60)
                    b = int(180 + depth * 50)
                    
            elif name == "Mars":
                # Red/orange with darker regions
                n1 = fractal_noise(u * 10, v * 10, 4, 0.5, 70)
                n2 = fractal_noise(u * 20, v * 20, 3, 0.4, 71)
                
                r = int(200 * (0.7 + n1 * 0.3))
                g = int(100 * (0.5 + n1 * 0.3 + n2 * 0.2))
                b = int(60 * (0.4 + n2 * 0.3))
                
            elif name == "Jupiter":
                # Banded with Great Red Spot feel
                band = math.sin(v * math.pi * 12) * 0.5 + 0.5
                n = fractal_noise(u * 15, v * 3, 4, 0.5, 90)
                turbulence = fractal_noise(u * 8, v * 8, 3, 0.6, 91)
                
                mix = band * 0.6 + n * 0.3 + turbulence * 0.1
                r = int(210 * (0.7 + mix * 0.3))
                g = int(160 * (0.6 + mix * 0.3))
                b = int(100 * (0.4 + mix * 0.4))
                
            elif name == "Saturn":
                # Golden banded
                band = math.sin(v * math.pi * 10) * 0.5 + 0.5
                n = fractal_noise(u * 12, v * 2, 3, 0.5, 110)
                
                mix = band * 0.7 + n * 0.3
                r = int(230 * (0.75 + mix * 0.25))
                g = int(200 * (0.7 + mix * 0.25))
                b = int(130 * (0.5 + mix * 0.3))
                
            elif name == "Uranus":
                # Pale cyan, mostly uniform
                n = fractal_noise(u * 8, v * 8, 3, 0.3, 130)
                
                r = int(150 * (0.85 + n * 0.15))
                g = int(220 * (0.9 + n * 0.1))
                b = int(230 * (0.9 + n * 0.1))
                
            elif name == "Neptune":
                # Deep blue with subtle bands
                band = math.sin(v * math.pi * 6) * 0.3 + 0.7
                n = fractal_noise(u * 10, v * 10, 3, 0.4, 150)
                
                r = int(60 * (0.6 + n * 0.3))
                g = int(100 * (0.7 + n * 0.2 + band * 0.1))
                b = int(220 * (0.85 + n * 0.15))
                
            else:
                # Fallback - use base color
                r = int(base_color[0] * 255)
                g = int(base_color[1] * 255)
                b = int(base_color[2] * 255)
            
            # Clamp values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            data.extend([r, g, b])
    
    return create_texture(size, size, data)

def generate_asteroid_texture(size=32):
    """Generate rocky asteroid texture."""
    data = []
    for y in range(size):
        for x in range(size):
            u = x / size
            v = y / size
            
            n = fractal_noise(u * 10, v * 10, 3, 0.6, 200)
            gray = int(80 + n * 80)
            
            data.extend([gray, int(gray * 0.9), int(gray * 0.85)])
    
    return create_texture(size, size, data)

def init_planet_textures():
    """Initialize all planet textures."""
    global planet_textures
    
    print("Generating procedural textures...")
    
    planet_textures["Sun"] = generate_sun_texture(128)
    planet_textures["Mercury"] = generate_planet_texture("Mercury", (0.7, 0.7, 0.7), 128)
    planet_textures["Venus"] = generate_planet_texture("Venus", (0.9, 0.6, 0.2), 128)
    planet_textures["Earth"] = generate_planet_texture("Earth", (0.2, 0.4, 1.0), 128)
    planet_textures["Mars"] = generate_planet_texture("Mars", (1.0, 0.2, 0.2), 128)
    planet_textures["Jupiter"] = generate_planet_texture("Jupiter", (0.8, 0.6, 0.4), 128)
    planet_textures["Saturn"] = generate_planet_texture("Saturn", (0.9, 0.8, 0.5), 128)
    planet_textures["Uranus"] = generate_planet_texture("Uranus", (0.4, 0.9, 0.9), 128)
    planet_textures["Neptune"] = generate_planet_texture("Neptune", (0.1, 0.1, 0.8), 128)
    planet_textures["Asteroid"] = generate_asteroid_texture(32)
    
    print("Textures generated!")
