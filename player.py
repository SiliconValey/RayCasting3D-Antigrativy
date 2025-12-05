import pygame
import math
import settings
from map import is_wall


class Player:
    def __init__(self, x, y, angle, sound_manager=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.bobbing_phase = 0.0
        self.bobbing_offset = 0.0
        self.sound_manager = sound_manager
        self.last_step_phase = 0.0
        self.doors = None
        
        # Estadísticas del jugador
        self.health = 100
        self.max_health = 100
        self.ammo = 80
        self.max_ammo = 100
        self.lives = 3
        self.score = 0
        
        # Sistema de armas
        self.weapons = ['knife', 'pistol', 'machinegun', 'minigun']
        self.current_weapon_index = 1  # Comenzar con pistola
        self.current_weapon = self.weapons[self.current_weapon_index]
        
    def set_doors(self, doors):
        """Asigna las puertas al jugador"""
        self.doors = doors
        
    def change_weapon(self, direction):
        """Cambia el arma (1 = siguiente, -1 = anterior)"""
        self.current_weapon_index = (self.current_weapon_index + direction) % len(self.weapons)
        self.current_weapon = self.weapons[self.current_weapon_index]
        if self.sound_manager:
            self.sound_manager.play('pickup')  # Sonido de cambio de arma
    
    def take_damage(self, amount):
        """El jugador recibe daño"""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.die()
        elif self.sound_manager:
            self.sound_manager.play('pain')
    
    def heal(self, amount):
        """El jugador se cura"""
        self.health = min(self.max_health, self.health + amount)
        if self.sound_manager:
            self.sound_manager.play('pickup')
    
    def add_ammo(self, amount):
        """Agregar munición"""
        self.ammo = min(self.max_ammo, self.ammo + amount)
        if self.sound_manager:
            self.sound_manager.play('pickup')
    
    def add_score(self, points):
        """Agregar puntos"""
        self.score += points
    
    def die(self):
        """El jugador muere"""
        self.lives -= 1
        if self.sound_manager:
            self.sound_manager.play('death')
        if self.lives > 0:
            # Respawn
            self.health = self.max_health
            self.ammo = 50
        
    def get_damage(self):
        """Retorna el daño del arma actual"""
        if self.current_weapon == 'knife': return 15
        elif self.current_weapon == 'pistol': return 25
        elif self.current_weapon == 'machinegun': return 20
        elif self.current_weapon == 'minigun': return 15
        return 0

    def shoot(self):
        """Disparar el arma actual"""
        if self.current_weapon == 'knife':
            # El cuchillo no usa munición
            if self.sound_manager:
                # Puedes añadir sonido de cuchillo si lo tienes
                pass
            return True
        elif self.ammo > 0:
            self.ammo -= 1
            if self.sound_manager:
                self.sound_manager.play('pistol') # Todo: add weapon specific sounds
            return True
        return False
        
    def move(self, keys):
        """Maneja el movimiento del jugador"""
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        
        dx, dy = 0, 0
        speed = settings.PLAYER_SPEED
        
        # Movimiento adelante/atrás
        if keys[pygame.K_w]:
            dx += cos_a * speed
            dy += sin_a * speed
        if keys[pygame.K_s]:
            dx -= cos_a * speed
            dy -= sin_a * speed
        
        # Movimiento lateral (strafe)
        if keys[pygame.K_a]:
            dx += sin_a * speed
            dy -= cos_a * speed
        if keys[pygame.K_d]:
            dx -= sin_a * speed
            dy += cos_a * speed
            
        # Sonido de pasos
        if (dx != 0 or dy != 0) and self.sound_manager:
            # Reproducir sonido cada medio ciclo de bobbing (cada paso)
            if int(self.bobbing_phase / math.pi) > int(self.last_step_phase / math.pi):
                self.sound_manager.play('thud')
            self.last_step_phase = self.bobbing_phase
        
        # Verificar colisiones antes de mover
        self._check_collision(dx, dy)
        
        # Rotación
        if keys[pygame.K_LEFT]:
            self.angle -= settings.PLAYER_ROT_SPEED
        if keys[pygame.K_RIGHT]:
            self.angle += settings.PLAYER_ROT_SPEED
        
        # Normalizar ángulo
        self.angle = self.angle % (2 * math.pi)
        
        # Head Bobbing (Efecto de caminar)
        if dx != 0 or dy != 0:
            # Si se mueve, incrementar fase
            self.bobbing_phase += 0.15
        else:
            # Si está quieto, resetear suavemente a 0
            self.bobbing_phase = 0
            
        # Calcular offset vertical (seno de la fase)
        # Amplitud de 10 píxeles
        self.bobbing_offset = math.sin(self.bobbing_phase) * 10

    def handle_mouse(self, dt):
        """Maneja la rotación con el mouse"""
        mx, my = pygame.mouse.get_pos()
        
        # Calcular diferencia con el centro de la pantalla
        center_x = settings.SCREEN_WIDTH // 2
        dx = mx - center_x
        
        # Si hubo movimiento, rotar
        if dx != 0:
            # Sensibilidad del mouse (Reducida a petición del usuario)
            SENSITIVITY = 0.001
            self.angle += dx * SENSITIVITY
            self.angle = self.angle % (2 * math.pi)
            
            # Resetear mouse al centro
            pygame.mouse.set_pos((center_x, settings.SCREEN_HEIGHT // 2))
            
    def get_bobbing_offset(self):
        """Retorna el offset vertical para el efecto de caminar"""
        return self.bobbing_offset
    
    def _check_collision(self, dx, dy):
        """Verifica colisiones y actualiza posición"""
        # Margen de colisión
        collision_margin = 0.2
        
        # Verificar colisión en X
        new_x = self.x + dx
        if not is_wall(new_x + collision_margin * (1 if dx > 0 else -1), self.y, self.doors):
            self.x = new_x
        
        # Verificar colisión en Y
        new_y = self.y + dy
        if not is_wall(self.x, new_y + collision_margin * (1 if dy > 0 else -1), self.doors):
            self.y = new_y
    
    def get_position(self):
        """Retorna la posición actual del jugador"""
        return self.x, self.y
    
    def get_angle(self):
        """Retorna el ángulo actual del jugador"""
        return self.angle
