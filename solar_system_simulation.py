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


# -----------------------------------------------------------------------------
# Logic / Math Helpers
# -----------------------------------------------------------------------------
def get_time():
    return time.time()

def draw_text(x, y, text):
    # 2D Overlay Text
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glColor3f(1.0, 1.0, 1.0)
    
    glRasterPos2i(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
        
    glEnable(GL_DEPTH_TEST)
    if state.lighting_enabled:
        glEnable(GL_LIGHTING)
        
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_times_text(x, y, text, large=True):
    """Draw text using Times Roman font - elegant serif style."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    glRasterPos2i(x, y)
    font = GLUT_BITMAP_TIMES_ROMAN_24 if large else GLUT_BITMAP_TIMES_ROMAN_10
    for char in text:
        glutBitmapCharacter(font, ord(char))
    
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_large_text(x, y, text, scale=0.15):
    """Draw larger text using stroke characters."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    glTranslatef(x, y, 0)
    glScalef(scale, scale, scale)
    
    for char in text:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(char))
    
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def init_background_animation():
    """Initialize background animation elements."""
    global bg_planets, shooting_stars
    
    # Create mini orbiting planets for background
    bg_planets = []
    planet_colors = [
        (0.7, 0.7, 0.7),  # Mercury gray
        (0.9, 0.6, 0.2),  # Venus orange
        (0.2, 0.5, 1.0),  # Earth blue
        (1.0, 0.3, 0.2),  # Mars red
        (0.8, 0.6, 0.4),  # Jupiter tan
        (0.9, 0.8, 0.5),  # Saturn gold
        (0.4, 0.9, 0.9),  # Uranus cyan
        (0.2, 0.2, 0.9),  # Neptune blue
    ]
    
    for i, color in enumerate(planet_colors):
        bg_planets.append({
            'angle': random.uniform(0, 360),
            'orbit_radius': 8 + i * 3,
            'speed': 15 - i * 1.5,
            'size': 0.2 + random.uniform(0, 0.3),
            'color': color,
            'y_offset': random.uniform(-1, 1)
        })
    
    # Create initial shooting stars
    shooting_stars = []

def update_background_animation(dt):
    """Update background animation elements."""
    global bg_planets, shooting_stars, bg_animation_time
    
    bg_animation_time += dt
    
    # Update orbiting planets
    for planet in bg_planets:
        planet['angle'] += planet['speed'] * dt
        if planet['angle'] >= 360:
            planet['angle'] -= 360
    
    # Update shooting stars
    for star in shooting_stars[:]:
        star['x'] += star['vx'] * dt
        star['y'] += star['vy'] * dt
        star['life'] -= dt
        if star['life'] <= 0:
            shooting_stars.remove(star)
    
    # Spawn new shooting stars occasionally
    if random.random() < 0.02:  # 2% chance per frame
        shooting_stars.append({
            'x': random.uniform(0, WINDOW_WIDTH),
            'y': random.uniform(WINDOW_HEIGHT * 0.5, WINDOW_HEIGHT),
            'vx': random.uniform(200, 400),
            'vy': random.uniform(-150, -50),
            'life': random.uniform(0.5, 1.5),
            'max_life': random.uniform(0.5, 1.5),
            'length': random.uniform(30, 80)
        })

def draw_background_animation():
    """Draw animated background with orbiting planets and shooting stars."""
    global bg_planets, shooting_stars
    
    # Draw shooting stars (2D overlay)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    for star in shooting_stars:
        alpha = star['life'] / star['max_life']
        # Draw streak line
        glBegin(GL_LINES)
        glColor4f(1.0, 1.0, 1.0, alpha)
        glVertex2f(star['x'], star['y'])
        glColor4f(1.0, 1.0, 1.0, 0.0)
        # Trail behind
        trail_x = star['x'] - (star['vx'] / abs(star['vx'])) * star['length'] if star['vx'] != 0 else star['x']
        trail_y = star['y'] - (star['vy'] / abs(star['vy'])) * star['length'] * 0.5 if star['vy'] != 0 else star['y']
        glVertex2f(trail_x, trail_y)
        glEnd()
    
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    # Draw orbiting mini-planets (3D)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluPerspective(45, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 300.0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glTranslatef(0, 0, -40)  # Move back to see planets
    
    glDisable(GL_LIGHTING)
    
    for planet in bg_planets:
        rad = math.radians(planet['angle'])
        px = math.cos(rad) * planet['orbit_radius']
        pz = math.sin(rad) * planet['orbit_radius']
        py = planet['y_offset']
        
        glPushMatrix()
        glTranslatef(px, py, pz)
        glColor3f(*planet['color'])
        glutSolidSphere(planet['size'], 12, 12)
        glPopMatrix()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_home_screen():
    """Draw the homepage with animated title and menu."""
    global title_pulse_time, menu_starfield, bg_planets
    
    # Initialize menu starfield if needed
    if menu_starfield is None:
        menu_starfield = Starfield(800)  # More stars for better effect
    
    # Initialize background animation if needed
    if not bg_planets:
        init_background_animation()
    
    # Update animations
    title_pulse_time += 0.016  # ~60fps
    update_background_animation(0.016)
    
    # Clear screen with dark space color
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Set up perspective view for 3D elements
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluPerspective(45, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 300.0)
    glMatrixMode(GL_MODELVIEW)
    
    # Draw starfield in background
    glPushMatrix()
    glTranslatef(0, 0, -50)
    menu_starfield.update(0.016)
    menu_starfield.draw()
    glPopMatrix()
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    # Draw animated background (orbiting planets + shooting stars)
    draw_background_animation()
    
    # --- 2D Overlay Elements ---
    # Calculate pulsing effect for title
    pulse = 0.85 + 0.15 * math.sin(title_pulse_time * 2.0)
    
    # Draw main title with Times Roman font
    title = "SOLAR SYSTEM SIMULATION"
    
    # Title glow effect (offset slightly, dimmer color)
    glColor3f(0.2 * pulse, 0.3 * pulse, 0.6 * pulse)
    draw_times_text(WINDOW_WIDTH // 2 - 140 + 1, WINDOW_HEIGHT - 160 - 1, title, large=True)
    
    # Main title - bright cyan/blue
    glColor3f(0.5 * pulse, 0.85 * pulse, 1.0 * pulse)
    draw_times_text(WINDOW_WIDTH // 2 - 140, WINDOW_HEIGHT - 160, title, large=True)
    
    # Draw decorative scanline effect (subtle)
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.0, 0.0, 0.04)
    glBegin(GL_LINES)
    for scan_y in range(0, WINDOW_HEIGHT, 3):
        glVertex2f(0, scan_y)
        glVertex2f(WINDOW_WIDTH, scan_y)
    glEnd()
    glDisable(GL_BLEND)
    
    # Draw decorative line under title
    glColor3f(0.4 + 0.2 * pulse, 0.5 + 0.2 * pulse, 0.8)
    glLineWidth(1.5)
    glBegin(GL_LINES)
    glVertex2f(WINDOW_WIDTH // 2 - 130, WINDOW_HEIGHT - 190)
    glVertex2f(WINDOW_WIDTH // 2 + 130, WINDOW_HEIGHT - 190)
    glEnd()
    glLineWidth(1.0)
    
    # Draw menu items with Times Roman font
    menu_y_start = WINDOW_HEIGHT - 260
    menu_spacing = 35
    
    for i, item in enumerate(MENU_ITEMS):
        if i == menu_selection:
            # Selected item - highlighted with arrows, glowing
            sel_pulse = 0.8 + 0.2 * math.sin(title_pulse_time * 4)
            glColor3f(1.0 * sel_pulse, 0.9 * sel_pulse, 0.3)
            draw_times_text(WINDOW_WIDTH // 2 - 80, menu_y_start - i * menu_spacing, f"> {item} <", large=True)
        else:
            # Unselected items - dimmer
            glColor3f(0.6, 0.6, 0.65)
            draw_times_text(WINDOW_WIDTH // 2 - 55, menu_y_start - i * menu_spacing, item, large=True)
    
    # Draw navigation hint at bottom
    glColor3f(0.4, 0.4, 0.5)
    draw_text(WINDOW_WIDTH // 2 - 140, 70, "Use UP/DOWN arrows to navigate")
    draw_text(WINDOW_WIDTH // 2 - 100, 45, "Press ENTER to select")
    
    # Draw version/credit with subtle styling
    glColor3f(0.25, 0.25, 0.35)
    draw_text(10, 20, "Solar System Simulation - Advanced Edition")

def draw_tutorial_screen():
    """Draw the tutorial/controls screen."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Draw starfield background
    global menu_starfield
    if menu_starfield:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPerspective(45, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 300.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(0, 0, -50)
        menu_starfield.draw()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    # Title
    glColor3f(0.6, 0.8, 1.0)
    draw_large_text(WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT - 80, "CONTROLS", 0.22)
    
    # Decorative line
    glDisable(GL_LIGHTING)
    glColor3f(0.4, 0.5, 0.7)
    glBegin(GL_LINES)
    glVertex2f(100, WINDOW_HEIGHT - 110)
    glVertex2f(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 110)
    glEnd()
    
    # Control categories
    y = WINDOW_HEIGHT - 150
    spacing = 22
    
    # --- Navigation Controls ---
    glColor3f(1.0, 0.8, 0.3)
    draw_text(80, y, "=== CAMERA & NAVIGATION ===")
    y -= spacing + 5
    
    controls_nav = [
        ("C", "Cycle camera modes (Free/Top/Side/Follow/Spacecraft)"),
        ("1-8", "Focus on planets (1=Mercury ... 8=Neptune)"),
        ("0", "View Sun information"),
        ("Z / X", "Zoom in / Zoom out"),
        ("Mouse Scroll", "Zoom in / out"),
    ]
    
    glColor3f(0.9, 0.9, 0.9)
    for key, desc in controls_nav:
        draw_text(100, y, f"[{key}]")
        glColor3f(0.7, 0.7, 0.7)
        draw_text(220, y, desc)
        glColor3f(0.9, 0.9, 0.9)
        y -= spacing
    
    y -= 10
    
    # --- Spacecraft Mode ---
    glColor3f(0.3, 1.0, 0.5)
    draw_text(80, y, "=== SPACECRAFT MODE ===")
    y -= spacing + 5
    
    controls_ship = [
        ("9", "Toggle spacecraft mode ON/OFF"),
        ("W / S", "Move forward / backward"),
        ("A / D", "Turn left / right"),
        ("Q / E", "Move up / down"),
    ]
    
    glColor3f(0.9, 0.9, 0.9)
    for key, desc in controls_ship:
        draw_text(100, y, f"[{key}]")
        glColor3f(0.7, 0.7, 0.7)
        draw_text(220, y, desc)
        glColor3f(0.9, 0.9, 0.9)
        y -= spacing
    
    y -= 10
    
    # --- Simulation Controls ---
    glColor3f(0.8, 0.4, 1.0)
    draw_text(80, y, "=== SIMULATION ===")
    y -= spacing + 5
    
    controls_sim = [
        ("SPACE", "Pause / Resume simulation"),
        ("+ / -", "Speed up / slow down time"),
        ("F", "Fast forward (5x speed)"),
        ("G", "Toggle gravity ON/OFF (planets drift!)"),
        ("O", "Toggle orbit path lines"),
        ("L", "Toggle lighting effects"),
        ("H", "Hide / Show planets"),
        ("ESC", "Exit simulation"),
    ]
    
    glColor3f(0.9, 0.9, 0.9)
    for key, desc in controls_sim:
        draw_text(100, y, f"[{key}]")
        glColor3f(0.7, 0.7, 0.7)
        draw_text(220, y, desc)
        glColor3f(0.9, 0.9, 0.9)
        y -= spacing
    
    # Footer
    glColor3f(0.5, 0.5, 0.6)
    draw_text(WINDOW_WIDTH // 2 - 100, 40, "Press ESC to return to menu")

def draw_settings_screen():
    """Draw the settings screen."""
    global settings
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Draw starfield background
    global menu_starfield
    if menu_starfield:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPerspective(45, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 300.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(0, 0, -50)
        menu_starfield.draw()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    # Title
    glColor3f(0.6, 0.8, 1.0)
    draw_large_text(WINDOW_WIDTH // 2 - 110, WINDOW_HEIGHT - 80, "SETTINGS", 0.22)
    
    # Decorative line
    glDisable(GL_LIGHTING)
    glColor3f(0.4, 0.5, 0.7)
    glBegin(GL_LINES)
    glVertex2f(100, WINDOW_HEIGHT - 110)
    glVertex2f(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 110)
    glEnd()
    
    y = WINDOW_HEIGHT - 180
    spacing = 40
    
    # Settings options
    glColor3f(1.0, 0.9, 0.4)
    draw_text(150, y, "Starting Camera Mode:")
    glColor3f(0.7, 0.9, 1.0)
    draw_text(400, y, CAM_MODE_NAMES[settings["starting_camera"]])
    draw_text(600, y, "[LEFT/RIGHT to change]")
    y -= spacing
    
    glColor3f(1.0, 0.9, 0.4)
    draw_text(150, y, "Starting Speed:")
    glColor3f(0.7, 0.9, 1.0)
    draw_text(400, y, f"{settings['starting_speed']:.1f}x")
    draw_text(600, y, "[Use +/- keys]")
    y -= spacing
    
    glColor3f(1.0, 0.9, 0.4)
    draw_text(150, y, "Show Orbit Paths:")
    glColor3f(0.5, 1.0, 0.5) if settings["show_orbits_default"] else glColor3f(1.0, 0.5, 0.5)
    draw_text(400, y, "ON" if settings["show_orbits_default"] else "OFF")
    draw_text(600, y, "[O to toggle]")
    y -= spacing
    
    glColor3f(1.0, 0.9, 0.4)
    draw_text(150, y, "Lighting Effects:")
    glColor3f(0.5, 1.0, 0.5) if settings["lighting_default"] else glColor3f(1.0, 0.5, 0.5)
    draw_text(400, y, "ON" if settings["lighting_default"] else "OFF")
    draw_text(600, y, "[L to toggle]")
    
    # Info note
    y -= 80
    glColor3f(0.6, 0.6, 0.7)
    draw_text(150, y, "Note: These settings will be applied when starting the simulation.")
    
    # Footer
    glColor3f(0.5, 0.5, 0.6)
    draw_text(WINDOW_WIDTH // 2 - 100, 40, "Press ESC to return to menu")

def start_simulation():
    """Start the simulation with current settings applied."""
    global current_screen
    
    # Apply settings to simulation state
    state.camera_mode = settings["starting_camera"]
    state.speed_multiplier = settings["starting_speed"]
    state.show_orbits = settings["show_orbits_default"]
    state.lighting_enabled = settings["lighting_default"]
    
    # Apply lighting setting
    if state.lighting_enabled:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
    else:
        glDisable(GL_LIGHTING)
    
    # Switch to simulation screen
    current_screen = SCREEN_SIMULATION

def start_tour():
    """Initialize and start the guided tour."""
    global current_screen, tour_active, tour_current_stop, tour_stop_timer
    global tour_transitioning, tour_transition_progress, tour_camera_start, tour_camera_end
    
    current_screen = SCREEN_TOUR
    tour_active = True
    tour_current_stop = 0
    tour_stop_timer = 0.0
    tour_transitioning = True
    tour_transition_progress = 0.0
    
    # Start camera from a distant viewpoint
    tour_camera_start = [0, 30, 60]
    
    # Calculate first target position (Sun)
    tour_camera_end = get_tour_camera_position(0)
    
    # Ensure simulation is running
    state.paused = False
    state.speed_multiplier = 0.5  # Slow speed for tour
    state.show_orbits = True

def get_tour_camera_position(stop_index):
    """Get camera position for a tour stop."""
    stop = TOUR_STOPS[stop_index]
    dist = stop["distance"]
    
    if stop["type"] == "sun":
        # Position camera looking at sun
        return [dist, dist * 0.5, dist]
    else:
        # Get planet position and offset camera
        planet = solar_system.planets[stop["index"]]
        px, py, pz = planet.world_pos
        return [px + dist, py + dist * 0.4, pz + dist]

def get_tour_target_position(stop_index):
    """Get the look-at target for a tour stop."""
    stop = TOUR_STOPS[stop_index]
    
    if stop["type"] == "sun":
        return [0, 0, 0]
    else:
        planet = solar_system.planets[stop["index"]]
        return list(planet.world_pos)

def lerp(a, b, t):
    """Linear interpolation between two values."""
    return a + (b - a) * t

def smooth_step(t):
    """Smooth step function for easing."""
    return t * t * (3 - 2 * t)

def update_tour(dt):
    """Update the guided tour state."""
    global tour_current_stop, tour_stop_timer, tour_transitioning
    global tour_transition_progress, tour_camera_start, tour_camera_end, tour_active
    global current_screen
    
    if not tour_active:
        return
    
    if tour_transitioning:
        # Flying to next stop
        tour_transition_progress += dt / TOUR_TRANSITION_DURATION
        
        if tour_transition_progress >= 1.0:
            tour_transition_progress = 1.0
            tour_transitioning = False
            tour_stop_timer = 0.0
    else:
        # At a stop, showing narration
        stop = TOUR_STOPS[tour_current_stop]
        tour_stop_timer += dt
        
        if tour_stop_timer >= stop["duration"]:
            # Move to next stop
            tour_current_stop += 1
            
            if tour_current_stop >= len(TOUR_STOPS):
                # Tour complete
                end_tour()
                return
            
            # Start transition to next stop
            tour_transitioning = True
            tour_transition_progress = 0.0
            tour_camera_start = list(tour_camera_end)
            tour_camera_end = get_tour_camera_position(tour_current_stop)
    
    # Update camera position
    if solar_system:
        t = smooth_step(tour_transition_progress)
        
        # Interpolate camera position
        cam_x = lerp(tour_camera_start[0], tour_camera_end[0], t)
        cam_y = lerp(tour_camera_start[1], tour_camera_end[1], t)
        cam_z = lerp(tour_camera_start[2], tour_camera_end[2], t)
        
        solar_system.camera.eye = [cam_x, cam_y, cam_z]
        
        # Look at current target
        target = get_tour_target_position(tour_current_stop)
        solar_system.camera.center = target
        solar_system.camera.up = [0, 1, 0]

def end_tour():
    """End the guided tour and return to menu."""
    global tour_active, current_screen
    tour_active = False
    current_screen = SCREEN_HOME

def draw_tour_ui():
    """Draw the tour overlay UI with narration."""
    if not tour_active:
        return
    
    stop = TOUR_STOPS[tour_current_stop]
    
    # Draw semi-transparent overlay at bottom
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Background panel
    glColor4f(0.0, 0.0, 0.1, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(50, 20)
    glVertex2f(WINDOW_WIDTH - 50, 20)
    glVertex2f(WINDOW_WIDTH - 50, 140)
    glVertex2f(50, 140)
    glEnd()
    
    # Border
    glColor3f(0.4, 0.6, 0.9)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(50, 20)
    glVertex2f(WINDOW_WIDTH - 50, 20)
    glVertex2f(WINDOW_WIDTH - 50, 140)
    glVertex2f(50, 140)
    glEnd()
    glLineWidth(1.0)
    
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    
    # Planet name header
    glColor3f(1.0, 0.9, 0.4)
    draw_times_text(80, 115, stop["name"], large=True)
    
    # Progress indicator
    progress_text = f"({tour_current_stop + 1}/{len(TOUR_STOPS)})"
    glColor3f(0.6, 0.6, 0.7)
    draw_text(WINDOW_WIDTH - 150, 115, progress_text)
    
    # Narration text
    if not tour_transitioning:
        y = 85
        for line in stop["narration"]:
            glColor3f(0.9, 0.9, 0.95)
            draw_text(80, y, line)
            y -= 20
    else:
        glColor3f(0.7, 0.7, 0.8)
        draw_text(80, 70, "Flying to next destination...")
    
    # Controls hint at top
    glColor3f(0.5, 0.5, 0.6)
    draw_text(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT - 30, "Press SPACE to skip | ESC to exit tour")

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class Starfield:
    def __init__(self, count=1000):
        self.stars = []
        for _ in range(count):
            x = random.uniform(-100, 100)
            y = random.uniform(-50, 50)
            z = random.uniform(-100, 100)
            brightness = random.uniform(0.3, 1.0)  # Initial brightness
            twinkle_speed = random.uniform(0.5, 3.0)  # How fast it twinkles
            twinkle_offset = random.uniform(0, 6.28)  # Random phase offset
            self.stars.append({
                'pos': (x, y, z),
                'brightness': brightness,
                'base_brightness': brightness,
                'twinkle_speed': twinkle_speed,
                'twinkle_offset': twinkle_offset
            })
    
    def update(self, dt):
        """Update star brightness for twinkling effect."""
        current_time = get_time()
        for star in self.stars:
            # Vary brightness using sine wave
            twinkle = math.sin(current_time * star['twinkle_speed'] + star['twinkle_offset'])
            # Map -1 to 1 range to 0.5 to 1.0 of base brightness
            star['brightness'] = star['base_brightness'] * (0.7 + 0.3 * twinkle)
            
    def draw(self):
        glDisable(GL_LIGHTING)
        glBegin(GL_POINTS)
        for star in self.stars:
            b = star['brightness']
            glColor3f(b, b, b)  # White with variable brightness
            glVertex3f(*star['pos'])
        glEnd()
        if state.lighting_enabled:
            glEnable(GL_LIGHTING)


class AsteroidBelt:
    """Asteroid belt between Mars and Jupiter with individually orbiting asteroids."""
    def __init__(self, count=200, inner_radius=14.5, outer_radius=16.5):
        self.asteroids = []
        for _ in range(count):
            orbit_radius = random.uniform(inner_radius, outer_radius)
            orbit_angle = random.uniform(0, 360)
            orbit_speed = random.uniform(15.0, 22.0)  # Between Mars and Jupiter speeds
            size = random.uniform(0.05, 0.15)
            y_offset = random.uniform(-0.3, 0.3)  # Slight vertical variation
            self.asteroids.append({
                'orbit_radius': orbit_radius,
                'orbit_angle': orbit_angle,
                'orbit_speed': orbit_speed,
                'size': size,
                'y_offset': y_offset
            })
    
    def update(self, dt):
        if state.paused:
            return
        adj_dt = dt * state.speed_multiplier
        for asteroid in self.asteroids:
            asteroid['orbit_angle'] += asteroid['orbit_speed'] * adj_dt
            if asteroid['orbit_angle'] >= 360.0:
                asteroid['orbit_angle'] -= 360.0
    
    def draw(self):
        if state.planets_hidden:
            return
        glDisable(GL_LIGHTING)
        
        # Use texture if available
        use_texture = "Asteroid" in planet_textures
        if use_texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, planet_textures["Asteroid"])
            glColor3f(1.0, 1.0, 1.0)
        else:
            glColor3f(0.5, 0.45, 0.4)  # Grey-brown asteroid color
        
        for asteroid in self.asteroids:
            rad = math.radians(asteroid['orbit_angle'])
            x = math.cos(rad) * asteroid['orbit_radius']
            z = math.sin(rad) * asteroid['orbit_radius']
            y = asteroid['y_offset']
            
            glPushMatrix()
            glTranslatef(x, y, z)
            
            if use_texture:
                quadric = gluNewQuadric()
                gluQuadricTexture(quadric, GL_TRUE)
                gluSphere(quadric, asteroid['size'], 6, 6)
                gluDeleteQuadric(quadric)
            else:
                glutSolidSphere(asteroid['size'], 6, 6)
            
            glPopMatrix()
        
        if use_texture:
            glDisable(GL_TEXTURE_2D)
        
        if state.lighting_enabled:
            glEnable(GL_LIGHTING)


class Spacecraft:
    """Player-controllable spacecraft that can fly around the solar system."""
    def __init__(self):
        # Position (start near Earth's orbit)
        self.pos = [12.0, 2.0, 0.0]
        
        # Rotation (yaw = left/right, pitch = up/down)
        self.yaw = 0.0    # Degrees, 0 = facing +Z
        self.pitch = 0.0  # Degrees, 0 = level
        
        # Movement
        self.move_speed = 15.0
        self.turn_speed = 90.0  # Degrees per second
    
    def get_forward_vector(self):
        """Calculate forward direction based on yaw and pitch."""
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        
        # Forward vector considering yaw and pitch
        fx = math.sin(yaw_rad) * math.cos(pitch_rad)
        fy = math.sin(pitch_rad)
        fz = math.cos(yaw_rad) * math.cos(pitch_rad)
        
        return [fx, fy, fz]
    
    def get_right_vector(self):
        """Calculate right direction (perpendicular to forward on XZ plane)."""
        yaw_rad = math.radians(self.yaw + 90)
        return [math.sin(yaw_rad), 0.0, math.cos(yaw_rad)]
    
    def update(self, dt):
        """Update spacecraft based on pressed keys."""
        if state.paused or not state.spacecraft_mode:
            return
        
        # Get movement vectors
        forward = self.get_forward_vector()
        
        # Process held keys for smooth movement
        keys = state.keys_pressed
        
        # Forward/Backward (W/S)
        if 'w' in keys:
            self.pos[0] += forward[0] * self.move_speed * dt
            self.pos[1] += forward[1] * self.move_speed * dt
            self.pos[2] += forward[2] * self.move_speed * dt
        if 's' in keys:
            self.pos[0] -= forward[0] * self.move_speed * dt
            self.pos[1] -= forward[1] * self.move_speed * dt
            self.pos[2] -= forward[2] * self.move_speed * dt
        
        # Turn Left/Right (A/D)
        if 'a' in keys:
            self.yaw -= self.turn_speed * dt
        if 'd' in keys:
            self.yaw += self.turn_speed * dt
        
        # Up/Down (Q/E)
        if 'q' in keys:
            self.pos[1] += self.move_speed * dt
        if 'e' in keys:
            self.pos[1] -= self.move_speed * dt
        
        # Keep yaw in range
        if self.yaw > 360: self.yaw -= 360
        if self.yaw < 0: self.yaw += 360
    
    def draw(self):
        """Draw the spacecraft model."""
        if not state.spacecraft_mode and state.camera_mode != CAM_SPACECRAFT:
            # Only draw if not in spacecraft view (can't see yourself)
            self._draw_model()
        elif state.camera_mode != CAM_SPACECRAFT:
            self._draw_model()
    
    def _draw_model(self):
        """Draw a simple spacecraft: cone nose + cylinder body."""
        glDisable(GL_LIGHTING)
        
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        glRotatef(-self.yaw, 0, 1, 0)  # Rotate to face direction
        glRotatef(90, 1, 0, 0)  # Orient cone forward
        
        # Body (cylinder) - silver/grey
        glColor3f(0.7, 0.7, 0.8)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.15, 0.15, 0.6, 12, 1)
        
        # Nose (cone) - white
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(0, 0, -0.3)
        glutSolidCone(0.15, 0.3, 12, 1)
        
        # Engine glow (small sphere at back) - blue
        glTranslatef(0, 0, 0.9)
        glColor3f(0.3, 0.5, 1.0)
        glutSolidSphere(0.1, 8, 8)
        
        glPopMatrix()
        
        if state.lighting_enabled:
            glEnable(GL_LIGHTING)

class Camera:
    def __init__(self):
        self.eye = [0.0, 10.0, 30.0]
        self.center = [0.0, 0.0, 0.0]
        self.up = [0.0, 1.0, 0.0]

    def update(self, target_pos=None):
        mode = state.camera_mode
        self.up = [0.0, 1.0, 0.0] # Default Up
        zoom = state.zoom_level  # Get current zoom
        
        if mode == CAM_FREE:
            self.eye = [0.0, 20.0 * zoom, 45.0 * zoom]
            self.center = [0.0, 0.0, 0.0]
            
        elif mode == CAM_TOP:
            self.eye = [0.0, 70.0 * zoom, 0.1]
            self.center = [0.0, 0.0, 0.0]
            self.up = [0.0, 0.0, -1.0] 
            
        elif mode == CAM_SIDE:
            self.eye = [70.0 * zoom, 0.0, 0.0]
            self.center = [0.0, 0.0, 0.0]
            
        elif mode == CAM_FOLLOW:
            if target_pos:
                dist = 12.0 * zoom
                height = 6.0 * zoom
                self.eye = [target_pos[0] + dist, target_pos[1] + height, target_pos[2] + dist]
                self.center = target_pos
            else:
                self.eye = [0.0, 15.0 * zoom, 30.0 * zoom]
                self.center = [0.0, 0.0, 0.0]
        
        # Note: CAM_SPACECRAFT is handled separately in update_spacecraft_camera

    def apply(self):
        gluLookAt(
            self.eye[0], self.eye[1], self.eye[2],
            self.center[0], self.center[1], self.center[2],
            self.up[0], self.up[1], self.up[2]
        )

class Planet:
    def __init__(self, name, radius, orbit_radius, orbit_speed, rotation_speed, color,
                 has_ring=False, ring_inner=0, ring_outer=0, ring_color=(1,1,1,0.5), ring_tilt=0):
        self.name = name
        self.radius = radius
        self.orbit_radius = orbit_radius
        self.orbit_speed = orbit_speed      
        self.rotation_speed = rotation_speed 
        self.color = color
        
        # Ring properties
        self.has_ring = has_ring
        self.ring_inner = ring_inner
        self.ring_outer = ring_outer
        self.ring_color = ring_color  # RGBA for transparency
        self.ring_tilt = ring_tilt  # Tilt angle in degrees (0 = flat, 90 = vertical)
        
        self.orbit_angle = random.uniform(0, 360) # Random start pos
        self.rotation_angle = 0.0
        
        self.world_pos = [orbit_radius, 0.0, 0.0]
        self.velocity_drift = [0.0, 0.0, 0.0]
        self.drifting_pos = [0.0, 0.0, 0.0] # used when gravity off
        self.was_gravity_on = True
        
        # Orbit trail tracking
        self.trail_history = []  # List of past positions
        self.trail_max_length = 100  # Number of trail points to keep
        self.trail_update_interval = 0.05  # Seconds between trail updates
        self.trail_timer = 0.0

    def update(self, dt):
        if state.paused:
            return

        adj_dt = dt * state.speed_multiplier
        
        # Self Rotation (always happens)
        self.rotation_angle += self.rotation_speed * adj_dt
        if self.rotation_angle >= 360.0: self.rotation_angle -= 360.0
        
        if state.gravity_enabled:
            # Check if we just switched ON
            if not self.was_gravity_on:
                # Restoration logic: Just snap back to orbit calculations
                pass 
            self.was_gravity_on = True
            
            # Normal Orbit
            self.orbit_angle += self.orbit_speed * adj_dt
            if self.orbit_angle >= 360.0: self.orbit_angle -= 360.0
            elif self.orbit_angle < 0.0: self.orbit_angle += 360.0
            
            rad = math.radians(self.orbit_angle)
            self.world_pos[0] = math.cos(rad) * self.orbit_radius
            self.world_pos[1] = 0.0
            self.world_pos[2] = math.sin(rad) * self.orbit_radius
            
        else:
            # Gravity OFF - Drift
            if self.was_gravity_on:
                # First frame of drift: Calculate tangent velocity
                # Velocity magnitude = orbit circumference / period? 
                # Simplification: relative to orbit radius and angular speed
                # v = r * omega (radians/sec)
                omega = math.radians(self.orbit_speed)
                angle_rad = math.radians(self.orbit_angle)
                
                # Tangent vector (-sin, cos)
                vx = -math.sin(angle_rad) * self.orbit_radius * omega
                vz = math.cos(angle_rad) * self.orbit_radius * omega
                
                self.velocity_drift = [vx, 0.0, vz]
                self.drifting_pos = list(self.world_pos)
                self.was_gravity_on = False
            
            # Update Position linearly
            self.drifting_pos[0] += self.velocity_drift[0] * adj_dt 
            self.drifting_pos[1] += self.velocity_drift[1] * adj_dt
            self.drifting_pos[2] += self.velocity_drift[2] * adj_dt
            
            self.world_pos = list(self.drifting_pos)
        
        # Update orbit trail
        self.trail_timer += adj_dt
        if self.trail_timer >= self.trail_update_interval:
            self.trail_timer = 0.0
            self.trail_history.append(list(self.world_pos))
            if len(self.trail_history) > self.trail_max_length:
                self.trail_history.pop(0)

    def draw_orbit(self):
        if not state.show_orbits: return
            
        glDisable(GL_LIGHTING)
        glColor3f(0.15, 0.15, 0.15)
        glBegin(GL_LINE_LOOP)
        segments = 64
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            x = self.orbit_radius * math.cos(theta)
            z = self.orbit_radius * math.sin(theta)
            glVertex3f(x, 0.0, z)
        glEnd()
        if state.lighting_enabled: glEnable(GL_LIGHTING)

    def draw_ring(self):
        """Draw planetary ring with transparency and tilt."""
        if not self.has_ring:
            return
        
        glPushMatrix()
        
        # Apply ring tilt (e.g., Uranus has ~90 degree tilt)
        if self.ring_tilt != 0:
            glRotatef(self.ring_tilt, 1.0, 0.0, 0.0)  # Tilt around X axis
        
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Draw ring as triangle strip
        segments = 64
        glBegin(GL_TRIANGLE_STRIP)
        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)
            
            # Outer edge
            glColor4f(*self.ring_color)
            glVertex3f(cos_t * self.ring_outer, 0.0, sin_t * self.ring_outer)
            
            # Inner edge (slightly more transparent)
            inner_color = (self.ring_color[0], self.ring_color[1], self.ring_color[2], self.ring_color[3] * 0.7)
            glColor4f(*inner_color)
            glVertex3f(cos_t * self.ring_inner, 0.0, sin_t * self.ring_inner)
        glEnd()
        
        glDisable(GL_BLEND)
        if state.lighting_enabled:
            glEnable(GL_LIGHTING)
        
        glPopMatrix()

    def draw(self, is_selected):
        if state.planets_hidden: return

        # Draw Orbit Path only if gravity is ON (otherwise it's confusing)
        if state.gravity_enabled:
            self.draw_orbit()
        
        glPushMatrix()
        glTranslatef(self.world_pos[0], self.world_pos[1], self.world_pos[2])
        
        # Highlight
        if is_selected:
            glDisable(GL_LIGHTING)
            glColor3f(1.0, 1.0, 1.0)
            glutWireSphere(self.radius * 1.3, 8, 8)
            if state.lighting_enabled: glEnable(GL_LIGHTING)
        
        # Draw Ring BEFORE rotation (rings stay flat in orbital plane)
        self.draw_ring()
        
        # Rotate for planet texture/surface
        glRotatef(self.rotation_angle, 0.0, 1.0, 0.0)
        
        # Draw Planet with texture
        if self.name in planet_textures:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, planet_textures[self.name])
            glColor3f(1.0, 1.0, 1.0)  # Full brightness for textured surface
            
            quadric = gluNewQuadric()
            gluQuadricTexture(quadric, GL_TRUE)
            gluQuadricNormals(quadric, GLU_SMOOTH)
            gluSphere(quadric, self.radius, 32, 32)
            gluDeleteQuadric(quadric)
            
            glDisable(GL_TEXTURE_2D)
        else:
            # Fallback to solid color
            glColor3f(*self.color)
            gluSphere(gluNewQuadric(), self.radius, 32, 32)
        
        glPopMatrix()
        
        # Draw trail after planet (not affected by planet's matrix)
        self.draw_trail()
        
        # Draw label above planet
        self.draw_label()
    
    def draw_trail(self):
        """Draw fading orbit trail behind planet."""
        if len(self.trail_history) < 2:
            return
        
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glBegin(GL_LINE_STRIP)
        for i, pos in enumerate(self.trail_history):
            # Fade from transparent (old) to planet color (new)
            alpha = i / len(self.trail_history)  # 0.0 (old) to 1.0 (new)
            glColor4f(self.color[0], self.color[1], self.color[2], alpha * 0.7)
            glVertex3f(pos[0], pos[1], pos[2])
        # Connect to current position
        glColor4f(self.color[0], self.color[1], self.color[2], 0.7)
        glVertex3f(self.world_pos[0], self.world_pos[1], self.world_pos[2])
        glEnd()
        
        glDisable(GL_BLEND)
        if state.lighting_enabled:
            glEnable(GL_LIGHTING)
    
    def draw_label(self):
        """Draw planet name label above the planet."""
        # Project 3D position to get label position
        label_y_offset = self.radius + 0.5  # Above planet
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)  # Labels always visible
        glColor3f(1.0, 1.0, 1.0)
        
        glPushMatrix()
        glTranslatef(self.world_pos[0], self.world_pos[1] + label_y_offset, self.world_pos[2])
        
        # Billboard - face the camera
        # Get modelview matrix and extract rotation to cancel it
        modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
        # Reset rotation part (first 3x3) to identity but keep translation
        for i in range(3):
            for j in range(3):
                if i == j:
                    modelview[i][j] = 1.0
                else:
                    modelview[i][j] = 0.0
        glLoadMatrixf(modelview)
        
        # Scale text
        glScalef(0.004, 0.004, 0.004)
        
        # Draw each character
        for char in self.name:
            glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(char))
        
        glPopMatrix()
        
        glEnable(GL_DEPTH_TEST)
        if state.lighting_enabled:
            glEnable(GL_LIGHTING)

class SolarSystem:
    def __init__(self):
        self.planets = []
        self.camera = Camera()
        self.stars = Starfield()
        self.asteroid_belt = AsteroidBelt()  # Asteroid belt between Mars and Jupiter
        self.spacecraft = Spacecraft()  # Player spacecraft
        self.last_time = get_time()
        self._init_bodies()

    def _init_bodies(self):
        # Planet data: name, radius, orbit_radius, orbit_speed, rotation_speed, color,
        #              has_ring, ring_inner, ring_outer, ring_color (RGBA)
        data = [
            ("Mercury", 0.4,  4.0,  45.0, 100.0, (0.7, 0.7, 0.7)),
            ("Venus",   0.6,  7.0,  35.0,  80.0, (0.9, 0.6, 0.2)),
            ("Earth",   0.6, 10.0,  29.0, 150.0, (0.2, 0.4, 1.0)),
            ("Mars",    0.5, 13.0,  24.0, 140.0, (1.0, 0.2, 0.2)),
            ("Jupiter", 1.4, 18.0,  13.0, 300.0, (0.8, 0.6, 0.4)),
            # Saturn with golden rings
            ("Saturn",  1.2, 23.0,   9.0, 280.0, (0.9, 0.8, 0.5),
             True, 1.5, 2.5, (0.85, 0.75, 0.55, 0.6)),
            # Uranus with cyan-tinted rings (90° tilt - famous for spinning on its side!)
            ("Uranus",  1.0, 28.0,   6.0, 200.0, (0.4, 0.9, 0.9),
             True, 1.3, 1.8, (0.5, 0.8, 0.85, 0.4), 90),
            ("Neptune", 1.0, 32.0,   5.0, 190.0, (0.1, 0.1, 0.8)),
        ]
        
        for p in data:
            self.planets.append(Planet(*p))

    def update(self):
        current_time = get_time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        for p in self.planets:
            p.update(dt)
        
        # Update asteroid belt
        self.asteroid_belt.update(dt)
        
        # Update spacecraft
        self.spacecraft.update(dt)
        
        # Update twinkling stars
        self.stars.update(dt)
            
        target_pos = None
        if state.selected_planet_index != -1:
            target_pos = self.planets[state.selected_planet_index].world_pos
        
        # Update camera (handle spacecraft mode specially)
        if state.camera_mode == CAM_SPACECRAFT:
            self._update_spacecraft_camera()
        else:
            self.camera.update(target_pos)

    def draw(self):
        # Draw Starfield
        self.stars.draw()

        # Draw Sun with texture
        glPushMatrix()
        glDisable(GL_LIGHTING)
        
        if "Sun" in planet_textures:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, planet_textures["Sun"])
            glColor3f(1.0, 1.0, 1.0)
            
            quadric = gluNewQuadric()
            gluQuadricTexture(quadric, GL_TRUE)
            gluQuadricNormals(quadric, GLU_SMOOTH)
            gluSphere(quadric, 2.0, 32, 32)
            gluDeleteQuadric(quadric)
            
            glDisable(GL_TEXTURE_2D)
        else:
            glColor3f(1.0, 1.0, 0.0)
            gluSphere(gluNewQuadric(), 2.0, 32, 32)
        
        if state.lighting_enabled: glEnable(GL_LIGHTING)
        glPopMatrix()
        
        # Draw Sun label
        self._draw_sun_label()
        
        # Draw Asteroid Belt
        self.asteroid_belt.draw()
        
        # Draw Spacecraft (only visible from non-spacecraft cameras)
        if state.camera_mode != CAM_SPACECRAFT:
            self.spacecraft.draw()
        
        # Draw Planets
        for i, p in enumerate(self.planets):
            p.draw(i == state.selected_planet_index)
    
    def _draw_sun_label(self):
        """Draw 'Sun' label above the sun."""
        label_y_offset = 3.0  # Above sun (radius is 2.0)
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glColor3f(1.0, 1.0, 0.7)  # Slightly yellow-white
        
        glPushMatrix()
        glTranslatef(0.0, label_y_offset, 0.0)
        
        # Billboard - face the camera
        modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
        for i in range(3):
            for j in range(3):
                if i == j:
                    modelview[i][j] = 1.0
                else:
                    modelview[i][j] = 0.0
        glLoadMatrixf(modelview)
        
        # Scale text
        glScalef(0.005, 0.005, 0.005)
        
        # Draw "Sun"
        for char in "Sun":
            glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(char))
        
        glPopMatrix()
        
        glEnable(GL_DEPTH_TEST)
        if state.lighting_enabled:
            glEnable(GL_LIGHTING)
    
    def _update_spacecraft_camera(self):
        """Position camera behind spacecraft looking in its direction."""
        ship = self.spacecraft
        forward = ship.get_forward_vector()
        
        # Camera position: behind and above spacecraft
        cam_dist = 5.0
        cam_height = 2.0
        
        self.camera.eye = [
            ship.pos[0] - forward[0] * cam_dist,
            ship.pos[1] + cam_height,
            ship.pos[2] - forward[2] * cam_dist
        ]
        
        # Look at point ahead of spacecraft
        look_dist = 10.0
        self.camera.center = [
            ship.pos[0] + forward[0] * look_dist,
            ship.pos[1] + forward[1] * look_dist,
            ship.pos[2] + forward[2] * look_dist
        ]
        
        self.camera.up = [0.0, 1.0, 0.0]

    def draw_ui(self):
        # Top-left info
        info = [f"Mode: {CAM_MODE_NAMES[state.camera_mode]}",
                f"Speed: {state.speed_multiplier:.1f}x {'(PAUSED)' if state.paused else ''}",
                f"Gravity: {'ON' if state.gravity_enabled else 'OFF'}",
                f"Lighting: {'ON' if state.lighting_enabled else 'OFF'}"]
        
        y = WINDOW_HEIGHT - 20
        for line in info:
            draw_text(10, y, line)
            y -= 20
        
        # Controls hint at bottom left
        draw_text(10, 100, "Keys: 0=Sun, 1-8=Planets, C=Camera, 9=Spacecraft")
        draw_text(10, 80, "Spacecraft: WASD=Move, QE=Up/Down")
        draw_text(10, 60, "Zoom: Z=In, X=Out (or Mouse Scroll)")
        draw_text(10, 40, "Space=Pause, +/-=Speed, ESC=Exit")
            
        # Selected Celestial Body Info Panel (right side)
        selected_name = None
        if state.selected_planet_index == -1:
            # Check if Sun is selected (index -2 means Sun)
            if hasattr(state, 'sun_selected') and state.sun_selected:
                selected_name = "Sun"
        else:
            selected_name = self.planets[state.selected_planet_index].name
        
        if selected_name and selected_name in CELESTIAL_INFO:
            info_data = CELESTIAL_INFO[selected_name]
            
            # Panel position (right side)
            panel_x = WINDOW_WIDTH - 320
            panel_y = WINDOW_HEIGHT - 30
            
            # Title
            draw_text(panel_x, panel_y, f"== {selected_name} ==")
            panel_y -= 25
            
            # Type
            draw_text(panel_x, panel_y, f"Type: {info_data['type']}")
            panel_y -= 18
            
            # Diameter
            draw_text(panel_x, panel_y, f"Diameter: {info_data['diameter']}")
            panel_y -= 18
            
            # Sun-specific or Planet-specific info
            if selected_name == "Sun":
                draw_text(panel_x, panel_y, f"Mass: {info_data['mass']}")
                panel_y -= 18
                draw_text(panel_x, panel_y, f"Surface: {info_data['surface_temp']}")
                panel_y -= 18
            else:
                draw_text(panel_x, panel_y, f"Orbit: {info_data['orbit_period']}")
                panel_y -= 18
                draw_text(panel_x, panel_y, f"Distance: {info_data['distance']}")
                panel_y -= 18
                
                # Current simulation distance
                p = self.planets[state.selected_planet_index]
                dist = math.sqrt(p.world_pos[0]**2 + p.world_pos[1]**2 + p.world_pos[2]**2)
                draw_text(panel_x, panel_y, f"Sim Dist: {dist:.1f} units")
                panel_y -= 18
            
            # Fun Facts
            panel_y -= 10  # Extra spacing
            draw_text(panel_x, panel_y, "--- Fun Facts ---")
            panel_y -= 20
            
            for fact in info_data['facts']:
                draw_text(panel_x, panel_y, f"* {fact}")
                panel_y -= 16

# -----------------------------------------------------------------------------
# Global State
# -----------------------------------------------------------------------------
solar_system = None

# -----------------------------------------------------------------------------
# GLUT Callbacks
# -----------------------------------------------------------------------------
def display():
    global current_screen
    
    # Draw the appropriate screen
    if current_screen == SCREEN_HOME:
        draw_home_screen()
    elif current_screen == SCREEN_TUTORIAL:
        draw_tutorial_screen()
    elif current_screen == SCREEN_SETTINGS:
        draw_settings_screen()
    elif current_screen == SCREEN_SIMULATION:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        if solar_system:
            # Set Light Position (At Sun)
            glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 0, 1])
            
            solar_system.camera.apply()
            solar_system.draw()
            solar_system.draw_ui()
    elif current_screen == SCREEN_TOUR:
        # Tour mode - render simulation with tour UI overlay
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        if solar_system:
            glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 0, 1])
            solar_system.camera.apply()
            solar_system.draw()
            
            # Draw tour narration overlay
            draw_tour_ui()
    
    glutSwapBuffers()

def timer(value):
    global menu_starfield
    
    # Only update simulation when in simulation screen
    if current_screen == SCREEN_SIMULATION and solar_system:
        solar_system.update()
    elif current_screen == SCREEN_TOUR and solar_system:
        # Update simulation and tour during tour mode
        solar_system.update()
        update_tour(0.016)
    elif menu_starfield:
        # Keep starfield twinkling on menu screens
        menu_starfield.update(0.016)
    
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)

def reshape(w, h):
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h, 0.1, 300.0)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global current_screen, menu_selection, settings
    
    try: k = key.decode("utf-8").lower()
    except: return
    
    # --- HOME SCREEN CONTROLS ---
    if current_screen == SCREEN_HOME:
        if k == '\r':  # Enter key
            if menu_selection == 0:  # Start Simulation
                start_simulation()
            elif menu_selection == 1:  # Guided Tour
                start_tour()
            elif menu_selection == 2:  # Tutorial
                current_screen = SCREEN_TUTORIAL
            elif menu_selection == 3:  # Settings
                current_screen = SCREEN_SETTINGS
            elif menu_selection == 4:  # Exit
                glutDestroyWindow(glutGetWindow())
                sys.exit(0)
        return  # Don't process other keys on home screen
    
    # --- TUTORIAL SCREEN CONTROLS ---
    elif current_screen == SCREEN_TUTORIAL:
        if k == '\x1b':  # ESC key
            current_screen = SCREEN_HOME
        return
    
    # --- SETTINGS SCREEN CONTROLS ---
    elif current_screen == SCREEN_SETTINGS:
        if k == '\x1b':  # ESC key
            current_screen = SCREEN_HOME
        elif k == 'o':  # Toggle orbits
            settings["show_orbits_default"] = not settings["show_orbits_default"]
        elif k == 'l':  # Toggle lighting
            settings["lighting_default"] = not settings["lighting_default"]
        elif k in ['+', '=']:  # Increase speed
            settings["starting_speed"] = min(10.0, settings["starting_speed"] + 0.5)
        elif k in ['-', '_']:  # Decrease speed
            settings["starting_speed"] = max(0.5, settings["starting_speed"] - 0.5)
        return
    
    # --- TOUR SCREEN CONTROLS ---
    elif current_screen == SCREEN_TOUR:
        if k == '\x1b':  # ESC key - exit tour
            end_tour()
        elif k == ' ':  # SPACE - skip to next stop
            global tour_current_stop, tour_transitioning, tour_transition_progress
            global tour_camera_start, tour_camera_end
            tour_current_stop += 1
            if tour_current_stop >= len(TOUR_STOPS):
                end_tour()
            else:
                tour_transitioning = True
                tour_transition_progress = 0.0
                tour_camera_start = list(solar_system.camera.eye)
                tour_camera_end = get_tour_camera_position(tour_current_stop)
        return
    
    # --- SIMULATION SCREEN CONTROLS ---
    if k == '\x1b':  # ESC - return to menu
        current_screen = SCREEN_HOME
        state.paused = True  # Pause simulation when in menu
    elif k == ' ': state.toggle_pause()
    elif k in ['+', '=']: state.adjust_speed(0.5)
    elif k in ['-', '_']: state.adjust_speed(-0.5)
    elif k == 'c': state.cycle_camera()
    elif k == 'o': state.toggle_orbits()
    elif k == 'l': state.toggle_lighting()
    elif k == 'g': state.toggle_gravity()
    elif k == 'h': state.toggle_hide()
    elif k == 'f': state.fast_forward()
    elif k in '12345678': state.select_planet(int(k) - 1)
    elif k == '0': state.select_sun()  # Select Sun to show its info
    elif k == '9': state.toggle_spacecraft_mode()  # Toggle spacecraft
    elif k == 'z': state.adjust_zoom(-0.1)  # Zoom in
    elif k == 'x': state.adjust_zoom(0.1)   # Zoom out
    
    # Track keys for spacecraft movement (WASD + QE)
    if k in 'wasdeq':
        state.keys_pressed.add(k)

def keyboard_up(key, x, y):
    """Handle key release for smooth spacecraft movement."""
    try: k = key.decode("utf-8").lower()
    except: return
    
    # Remove key from pressed set
    if k in state.keys_pressed:
        state.keys_pressed.remove(k)

def mouse_scroll(button, dir, x, y):
    """Handle mouse scroll wheel for zoom."""
    if button == 3:  # Scroll up
        state.adjust_zoom(-0.1)  # Zoom in
    elif button == 4:  # Scroll down
        state.adjust_zoom(0.1)   # Zoom out

def special_keyboard(key, x, y):
    """Handle special keys (arrow keys) for menu navigation."""
    global menu_selection, settings
    
    # --- HOME SCREEN ---
    if current_screen == SCREEN_HOME:
        if key == GLUT_KEY_UP:
            menu_selection = (menu_selection - 1) % len(MENU_ITEMS)
        elif key == GLUT_KEY_DOWN:
            menu_selection = (menu_selection + 1) % len(MENU_ITEMS)
    
    # --- SETTINGS SCREEN ---
    elif current_screen == SCREEN_SETTINGS:
        if key == GLUT_KEY_LEFT:
            # Cycle camera mode backwards
            current_cam = settings["starting_camera"]
            settings["starting_camera"] = (current_cam - 1) % 5
        elif key == GLUT_KEY_RIGHT:
            # Cycle camera mode forwards
            current_cam = settings["starting_camera"]
            settings["starting_camera"] = (current_cam + 1) % 5

def init():
    glClearColor(0.05, 0.05, 0.05, 1.0) # Very Dark Grey (Space)
    glEnable(GL_DEPTH_TEST)
    
    # Lighting Setup
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE) # Important for scaling
    
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    
    # Light Components
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.1, 0.1, 0.1, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    global solar_system
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(WINDOW_TITLE)
    init()
    
    # Show loading screen before texture generation
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glColor3f(0.6, 0.8, 1.0)
    glRasterPos2i(WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2)
    for char in "Loading...":
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
    glutSwapBuffers()
    
    init_planet_textures()  # Generate procedural textures
    solar_system = SolarSystem()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)  # For spacecraft smooth movement
    glutSpecialFunc(special_keyboard)  # For arrow keys (menu navigation)
    glutMouseFunc(mouse_scroll)  # For zoom with scroll wheel
    glutTimerFunc(0, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()

