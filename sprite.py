import math


class Sprite:
    def __init__(self, x, y, sprite_type, texture):
        self.x = x
        self.y = y
        self.sprite_type = sprite_type
        self.texture = texture
        self.distance = 0
        self.screen_x = 0
        self.screen_y = 0
        self.sprite_height = 0
        self.sprite_width = 0
        self.v_shift = 0.0 # Desplazamiento vertical (proporcional a la altura)
    
    def calculate_distance(self, player_x, player_y):
        """Calcula la distancia al jugador"""
        dx = self.x - player_x
        dy = self.y - player_y
        self.distance = math.sqrt(dx * dx + dy * dy)
        return self.distance
    
    def get_sprite_projection(self, player_x, player_y, player_angle, screen_width, screen_height):
        """Calcula la proyección del sprite en la pantalla usando corrección de tangente"""
        # Vector del jugador al sprite
        dx = self.x - player_x
        dy = self.y - player_y
        
        # Distancia euclidiana
        dist = math.sqrt(dx*dx + dy*dy)
        self.distance = dist
        
        # Ángulo del sprite
        sprite_angle = math.atan2(dy, dx)
        
        # Diferencia de ángulo
        delta = sprite_angle - player_angle
        
        # Normalizar delta a [-PI, PI]
        while delta > math.pi: delta -= 2 * math.pi
        while delta < -math.pi: delta += 2 * math.pi
        
        # Verificar si está en el campo de visión (con un margen)
        # FOV es PI/3 (60 grados), mitad es PI/6
        HALF_FOV = math.pi / 3 / 2
        
        # Si el ángulo es demasiado grande, no dibujar
        # Agregamos un margen generoso para que no desaparezcan en los bordes
        if abs(delta) > HALF_FOV + 0.5:
            return None
            
        # Proyección en pantalla usando Tangente para evitar el efecto de deslizamiento
        # screen_x = center + (tan(delta) / tan(half_fov)) * center
        # Esto proyecta correctamente el ángulo en un plano recto
        
        screen_dist = (screen_width / 2) / math.tan(HALF_FOV)
        proj_x = math.tan(delta) * screen_dist
        
        self.screen_x = int(screen_width / 2 + proj_x)
        
        # Calcular distancia perpendicular para evitar ojo de pez en el escalado
        perp_dist = dist * math.cos(delta)
        
        # Evitar división por cero o distancias muy pequeñas
        if perp_dist < 0.2:
            return None
            
        # Altura del sprite
        proj_height = int(screen_height / perp_dist)
        
        # Limitar altura máxima
        if proj_height > screen_height * 5:
            proj_height = screen_height * 5
            
        self.sprite_height = proj_height
        self.sprite_width = proj_height
        
        # Calcular shift vertical
        v_shift_px = int(proj_height * self.v_shift)
        self.screen_y = int(screen_height / 2 - proj_height / 2) + v_shift_px
        
        return {
            'x': self.screen_x,
            'y': self.screen_y,
            'width': self.sprite_width,
            'height': self.sprite_height,
            'distance': perp_dist  # Usar distancia perpendicular para z-buffer
        }
