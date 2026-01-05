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

