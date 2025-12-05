import math

# Configuración de la pantalla
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Configuración del raycasting
FOV = math.pi / 3  # 60 grados
HALF_FOV = FOV / 2
NUM_RAYS = SCREEN_WIDTH // 2  # Número de rayos a lanzar
MAX_DEPTH = 20  # Profundidad máxima de rayos
DELTA_ANGLE = FOV / NUM_RAYS

# Configuración del jugador
PLAYER_SPEED = 0.05  # Velocidad de movimiento
PLAYER_ROT_SPEED = 0.03  # Velocidad de rotación

# Tamaño del mapa
TILE_SIZE = 1.0

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Colores del juego
FLOOR_COLOR = (50, 50, 50)
CEILING_COLOR = (100, 100, 100)

# Configuración del minimap
MINIMAP_SCALE = 5
MINIMAP_TILE_SIZE = 10
MINIMAP_OFFSET_X = 10
MINIMAP_OFFSET_Y = 10

# Escala de distancia para renderizado
SCALE = SCREEN_WIDTH // NUM_RAYS

# Configuración de sonido
SOUND_ENABLED = True
