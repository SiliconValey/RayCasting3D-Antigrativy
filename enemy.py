import pygame
import math
import settings
from sprite import Sprite
from map import is_wall

class Enemy(Sprite):
    def __init__(self, x, y, sprite_type, texture, player, raycaster):
        super().__init__(x, y, sprite_type, texture)
        self.player = player
        self.raycaster = raycaster
        self.health = 100
        self.dead = False
        self.speed = 0.05
        self.state = 'IDLE' # IDLE, CHASE, ATTACK, PAIN, DIE
        
        # Animación
        self.frames = {}  # 'idle': [img], 'walk': [img1, img2...], etc.
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 150 # ms por frame
        self.angle = 0
        
    def update(self):
        if self.dead:
            return
            
        now = pygame.time.get_ticks()
        dist = self.calculate_distance(self.player.x, self.player.y)
        
        # Lógica de estados simple
        if self.state == 'IDLE':
            # Verificar LOS
            if self.raycaster.has_line_of_sight(self.x, self.y, self.player.x, self.player.y):
                self.state = 'CHASE'
                if settings.SOUND_ENABLED and hasattr(self, 'sound_manager'):
                    self.sound_manager.play('achtung')
                    
        elif self.state == 'CHASE':
            # Moverse hacia el jugador
            dx = self.player.x - self.x
            dy = self.player.y - self.y
            angle = math.atan2(dy, dx)
            
            # Movimiento simple (sin A*)
            new_x = self.x + math.cos(angle) * self.speed
            new_y = self.y + math.sin(angle) * self.speed
            
            if not is_wall(new_x, new_y):
                self.x = new_x
                self.y = new_y
            
            # Si está cerca, atacar
            if dist < 2.0:
                self.state = 'ATTACK'
                self.last_attack = now
                
            # Animación de caminar
            if self.state == 'CHASE': # puede haber cambiado a ATTACK
                if now - self.last_update > self.frame_rate:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.frames.get('walk', [self.texture]))
                    self.texture = self.frames.get('walk', [self.texture])[self.current_frame]

        elif self.state == 'ATTACK':
            # Disparar
            if now - self.last_attack > 1000: # 1 segundo entre disparos
                self.player.take_damage(10) # 10 de daño
                self.last_attack = now
                if hasattr(self, 'sound_manager'):
                   self.sound_manager.play('pistol') # Sonido de disparo del guardia
            
            # Volver a perseguir si el jugador se aleja
            if dist > 2.5:
                self.state = 'CHASE'
                
        elif self.state == 'DIE':
             # Animación de muerte
             pass # Implementar lógica de frames de muerte

    def take_damage(self, amount):
        if self.dead:
            return
        
        self.health -= amount
        self.state = 'PAIN'
        if self.health <= 0:
            self.state = 'DIE'
            self.dead = True
            self.texture = self.frames.get('die', [self.texture])[-1] # Frame final de muerte
            # Ajustar posición vertical para que el cuerpo quede en el suelo
            # (El valor depende de cómo esté centrado el sprite en la textura)
            self.v_shift = 0.5

class Guard(Enemy):
    def __init__(self, x, y, player, raycaster, texture_manager, sound_manager):
        # Cargar textura base (fallback)
        base_tex = texture_manager.get_sprite_texture('guard')
        super().__init__(x, y, 'guard', base_tex, player, raycaster)
        self.sound_manager = sound_manager
        
        # Cargar sprite sheet y cortar
        self._load_sprites(base_tex)
        
    def _load_sprites(self, sheet):
        # Asumiendo 448x128 pixels.
        # 64x64 por frame -> 7 col, 2 filas.
        # Fila 0: 4 caminar, 3 ataque?
        # Fila 1: 1 pain, 4 muerte?
        
        width = 64
        height = 64
        
        # Helper para extraer
        def get_frame(row, col):
            rect = pygame.Rect(col * width, row * height, width, height)
            return sheet.subsurface(rect)
        
        # Caminar: Fila 0, cols 0-3 (4 frames)
        self.frames['walk'] = [get_frame(0, i) for i in range(4)]
        
        # Ataque: Fila 0, cols 4-6 (3 frames)
        self.frames['attack'] = [get_frame(0, i) for i in range(4, 7)]
        
        # Pain: Fila 1, col 0
        self.frames['pain'] = [get_frame(1, 0)]
        
        # Muerte: Fila 1, cols 1-4 (4 frames)
        self.frames['die'] = [get_frame(1, i) for i in range(1, 5)]
        
        # Frame muerto final
        self.frames['dead'] = [get_frame(1, 4)]
