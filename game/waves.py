"""

You're welcome! This level system is fully customizable.

Wave configuration file for Wild Defense
Each wave is a list of enemy spawns
Format for each spawn: (enemy_type, delay_ms)
- enemy_type: "poacher", "deforester", or "invasive"
- delay_ms: milliseconds to wait before spawning next enemy

Example wave:
[
    ("poacher", 0),     # First enemy spawns immediately
    ("poacher", 1000),  # Second enemy spawns 1 second later
    ("deforester", 2000)  # Third enemy spawns 2 seconds later
]
"""

WAVES = [
    # Wave 1 - Simple wave with poachers
    [
        ("poacher", 0),
        ("poacher", 2000),
        ("poacher", 4000),
        ("poacher", 6000),
        ("poacher", 8000),
    ],
    
    # Wave 2 - Mix of poachers and deforesters
    [
        ("poacher", 0),
        ("deforester", 1000),
        ("poacher", 2000),
        ("deforester", 3000),
        ("poacher", 4000),
        ("deforester", 5000),
    ],
    
    # Wave 3 - Introducing invasive species
    [
        ("poacher", 0),
        ("deforester", 1500),
        ("invasive", 3000),
        ("poacher", 4000),
        ("deforester", 5500),
        ("invasive", 7000),
    ],
    
    # Wave 4 - Harder wave with more enemies
    [
        ("poacher", 0),
        ("poacher", 1000),
        ("deforester", 2000),
        ("invasive", 2500),
        ("deforester", 3000),
        ("invasive", 3500),
        ("poacher", 4000),
        ("deforester", 4500),
    ],
    
    # Wave 5 - Boss wave
    [
        ("invasive", 0),
        ("deforester", 500),
        ("deforester", 1000),
        ("invasive", 2000),
        ("poacher", 2100),
        ("poacher", 2200),
        ("poacher", 2300),
        ("invasive", 4000),
        ("deforester", 4100),
        ("deforester", 4200),
    ],
]

# Enemy stats
ENEMY_STATS = {
    "poacher": {
        "health": 50,
        "speed": 2,
        "damage": 5,
        "reward": 10
    },
    "deforester": {
        "health": 100,
        "speed": 1,
        "damage": 10,
        "reward": 15
    },
    "invasive": {
        "health": 75,
        "speed": 3,
        "damage": 15,
        "reward": 20
    }
}
