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

