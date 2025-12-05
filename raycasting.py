import math
import settings
from map import is_wall, get_wall_type


class RayCaster:
    def __init__(self):
        self.rays = []
        self.doors = None
    
    def has_line_of_sight(self, x1, y1, x2, y2):
        """Verifica si hay línea de visión directa entre dos puntos (sin paredes)"""
        # Distancia total
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx*dx + dy*dy)
        
        # Pasos para el rayo
        steps = int(dist * 2)  # Verificar cada 0.5 unidades aprox
        if steps < 1: steps = 1
        
        step_x = dx / steps
        step_y = dy / steps
        
        # Verificar cada paso
        cx, cy = x1, y1
        for _ in range(steps):
            cx += step_x
            cy += step_y
            
            # Si chocamos con una pared, no hay LOS
            # Verificación simple, se puede mejorar con DDA si es necesario
            if is_wall(int(cx), int(cy), self.doors):
                return False
                
        return True
        
    def set_doors(self, doors):
        """Asigna las puertas al raycaster"""
        self.doors = doors
        
    def cast_rays(self, player_x, player_y, player_angle):
        """Lanza rayos desde la posición del jugador"""
        self.rays = []
        
        # Ángulo inicial (izquierda del FOV)
        ray_angle = player_angle - settings.HALF_FOV
        
        # Local import to avoid circular dependency
        from map import get_door_at_position, MAP_WIDTH, MAP_HEIGHT
        
        for ray in range(settings.NUM_RAYS):
            # Lanzar un rayo en esta dirección usando DDA avanzado
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)
            
            # Prevenir división por cero
            if cos_a == 0: cos_a = 0.000001
            if sin_a == 0: sin_a = 0.000001
            
            # Configuración inicial DDA
            map_x = int(player_x)
            map_y = int(player_y)
            
            delta_dist_x = abs(1 / cos_a)
            delta_dist_y = abs(1 / sin_a)
            
            if cos_a < 0:
                step_x = -1
                side_dist_x = (player_x - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - player_x) * delta_dist_x
                
            if sin_a < 0:
                step_y = -1
                side_dist_y = (player_y - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1.0 - player_y) * delta_dist_y
                
            # Variables de resultado
            hit_side = 'vertical'  # 'horizontal' or 'vertical'
            wall_type = 0
            wall_x = 0.0  # Posición exacta del golpe (0.0 a 1.0)
            door_offset = 0.0 # Para ajuste de textura en puertas
            
            # Bucle DDA
            for _ in range(settings.MAX_DEPTH):
                # Avanzar al siguiente cuadro
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    hit_side = 'vertical'
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    hit_side = 'horizontal'
                
                # Verificar si está fuera del mapa
                if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
                    wall_type = 1
                    break
                    
                # Verificar pared usando map.py (pero optimizado)
                # Intencionalmente no usamos is_wall aquí para manejar manualmente la lógica de puertas
                if is_wall(map_x, map_y, None): # Check geometry only first
                    current_wall_type = get_wall_type(map_x, map_y)
                    
                    if current_wall_type == 7 and self.doors: # Es una puerta
                        door = get_door_at_position(map_x, map_y, self.doors)
                        if door and door.is_open:
                            # Calcular punto de impacto exacto para ver si pasamos por el hueco
                            if hit_side == 'vertical':
                                perp_wall_dist = (map_x - player_x + (1 - step_x) / 2) / cos_a
                                exact_y = player_y + perp_wall_dist * sin_a
                                hit_offset = exact_y - int(exact_y)
                            else:
                                perp_wall_dist = (map_y - player_y + (1 - step_y) / 2) / sin_a
                                exact_x = player_x + perp_wall_dist * cos_a
                                hit_offset = exact_x - int(exact_x)
                                
                            # Corregir offset si el rayo viene del lado negativo
                            # (Alineación de texturas)
                            # Simple check: if offset < open_amount, it's a gap
                            if hit_offset < door.open_amount:
                                continue # Pasar a través (hueco)
                            else:
                                # Golpeamos la parte sólida de la puerta
                                wall_type = current_wall_type
                                door_offset = door.open_amount # Guardar para ajustar textura
                                break
                        else:
                            # Puerta cerrada o no encontrada (sólida)
                            wall_type = current_wall_type
                            break
                    else:
                        # Pared normal sólida
                        wall_type = current_wall_type
                        break
            
            # Calcular distancia final proyectada
            if hit_side == 'vertical':
                depth = (map_x - player_x + (1 - step_x) / 2) / cos_a
            else:
                depth = (map_y - player_y + (1 - step_y) / 2) / sin_a
                
            # Calcular wall_x para texturizado
            if hit_side == 'vertical':
                wall_x = player_y + depth * sin_a
            else:
                wall_x = player_x + depth * cos_a
            wall_x -= math.floor(wall_x)
            
            # Ajustar textura de puertas deslizantes
            # Para que la textura se mueva con la puerta
            if wall_type == 7:
                 wall_x -= door_offset
            
            # Corregir distorsión fish-eye
            depth *= math.cos(player_angle - ray_angle)
            
            # Calcular altura de la pared
            if depth > 0:
                wall_height = settings.SCREEN_HEIGHT / depth
            else:
                wall_height = settings.SCREEN_HEIGHT
                
            # Información del rayo
            ray_info = {
                'depth': depth,
                'wall_height': wall_height,
                'wall_type': wall_type,
                'side': hit_side,
                'texture_x': wall_x,
                'angle': ray_angle,
                'hit_pos': (map_x, map_y) # Approx pos
            }
            
            self.rays.append(ray_info)
            
            # Siguiente rayo
            ray_angle += settings.DELTA_ANGLE
        
        return self.rays

    def get_rays(self):
        """Retorna los rayos lanzados"""
        return self.rays
