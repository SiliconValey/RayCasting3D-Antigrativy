import settings

# Mapa del juego (0 = vacío, 1-6 = diferentes texturas de paredes, 7 = puerta)
WORLD_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 1],
    [1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 0, 1],
    [1, 0, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 5, 5, 7, 5, 5, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# Dimensiones del mapa
MAP_WIDTH = len(WORLD_MAP[0])
MAP_HEIGHT = len(WORLD_MAP)

# Posiciones de puertas (x, y)
# Habitación cerrada con una sola puerta en (7, 10)
DOOR_POSITIONS = [
    (7, 10),  # Entrada a la habitación secreta
]

# Posiciones de sprites (x, y, tipo)
# tipo: 'barrel', 'pillar', 'greenlight'
SPRITE_POSITIONS = [
    (3.5, 3.5, 'barrel'),
    (2.5, 2.5, 'pillar'),
    (10.5, 3.5, 'barrel'),
    (12.5, 5.5, 'pillar'),
    (4.5, 2.5, 'greenlight'),
    # Nuevos sprites
    (1.5, 1.5, 'greenlight'),
    (14.5, 1.5, 'barrel'),
    (1.5, 14.5, 'barrel'),
    (14.5, 14.5, 'greenlight'),
    (5.5, 5.5, 'pillar'),
    # Sprites dentro de la habitación secreta
    (7.5, 12.5, 'greenlight'),  # Luz verde en el centro de la habitación
    (6.5, 11.5, 'barrel'),      # Barril izquierdo
    (8.5, 11.5, 'barrel'),      # Barril derecho
    (7.5, 13.5, 'pillar'),      # Columna al fondo
]

# Posiciones de enemigos (x, y, tipo)
ENEMY_POSITIONS = [
    (10.5, 10.5, 'guard'), # Hallway guard
    (7.5, 8.5, 'guard'),  # Near door
    (5.5, 4.5, 'guard'),  # Room guard
    (13.5, 13.5, 'guard') # Back room guard
]


def is_wall(x, y, doors=None):
    """Verifica si una posición contiene una pared"""
    if x < 0 or x >= MAP_WIDTH or y < 0 or y >= MAP_HEIGHT:
        return True
    
    wall_type = WORLD_MAP[int(y)][int(x)]
    
    # Si es una puerta (7), verificar si está abierta
    if wall_type == 7 and doors:
        door = get_door_at_position(int(x), int(y), doors)
        if door and door.is_passable():
            return False
    
    return wall_type != 0


def get_wall_type(x, y):
    """Obtiene el tipo de pared en una posición"""
    if x < 0 or x >= MAP_WIDTH or y < 0 or y >= MAP_HEIGHT:
        return 1
    return WORLD_MAP[int(y)][int(x)]


def is_door(x, y):
    """Verifica si una posición contiene una puerta"""
    if x < 0 or x >= MAP_WIDTH or y < 0 or y >= MAP_HEIGHT:
        return False
    return WORLD_MAP[int(y)][int(x)] == 7


def get_door_at_position(x, y, doors):
    """Obtiene la puerta en una posición específica"""
    for door in doors:
        if door.x == int(x) and door.y == int(y):
            return door
    return None
