import pygame
import sys
import math
import settings
from player import Player
from raycasting import RayCaster
from renderer import Renderer
from texture_manager import TextureManager
from sound_manager import SoundManager
from sprite import Sprite
from door import Door
from hud import HUD
from enemy import Guard
from weapon import Weapon
from map import SPRITE_POSITIONS, DOOR_POSITIONS, ENEMY_POSITIONS, is_door, get_door_at_position


class Game:
    def __init__(self):
        # Inicializar PyGame
        pygame.init()
        
        # Crear ventana
        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Wolfenstein 3D - PyGame")
        
        # Reloj para controlar FPS
        self.clock = pygame.time.Clock()
        
        # Inicializar componentes
        self.texture_manager = TextureManager()
        self.texture_manager.load_textures()
        
        self.sound_manager = SoundManager()
        self.sound_manager.play('guten_tag')  # Sonido de bienvenida
        
        self.player = Player(8.0, 8.0, 0, self.sound_manager)  # Posición inicial en el centro del mapa
        self.raycaster = RayCaster()
        self.renderer = Renderer(self.screen, self.texture_manager)
        self.hud = HUD(self.screen)
        self.weapon = Weapon(self.screen, self.player, self.texture_manager)  # Sistema HUD
        
        # Crear puertas
        self.doors = []
        for door_pos in DOOR_POSITIONS:
            x, y = door_pos
            door = Door(x, y)
            self.doors.append(door)
        
        # Asignar puertas al jugador, raycaster y renderer
        self.player.set_doors(self.doors)
        self.raycaster.set_doors(self.doors)
        self.renderer.set_doors(self.doors)
        
        # Crear sprites
        self.sprites = []
        for sprite_data in SPRITE_POSITIONS:
            x, y, sprite_type = sprite_data
            texture = self.texture_manager.get_sprite_texture(sprite_type)
            sprite = Sprite(x, y, sprite_type, texture)
            self.sprites.append(sprite)
            
        # Crear enemigos
        self.enemies = []
        for pos in ENEMY_POSITIONS:
             x, y, type = pos
             if type == 'guard':
                 # Guard(x, y, player, raycaster, texture_manager, sound_manager)
                 guard = Guard(x, y, self.player, self.raycaster, self.texture_manager, self.sound_manager)
                 self.enemies.append(guard)
        
        # Configurar mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        self.running = True
        
    def handle_events(self):
        """Maneja eventos de PyGame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.try_open_door()
                # Cambio de arma con teclas numéricas
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    weapon_index = event.key - pygame.K_1
                    if weapon_index < len(self.player.weapons):
                        self.player.current_weapon_index = weapon_index
                        self.player.current_weapon = self.player.weapons[weapon_index]
                        if self.sound_manager:
                            self.sound_manager.play('pickup')
                # Tecla E para recolectar ítems (para futuro)
                elif event.key == pygame.K_e:
                    pass  # Aquí se puede agregar lógica de recolección
            # Disparo con clic del mouse
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic izquierdo
                    damage = self.player.get_damage()
                    if self.player.shoot():
                         self.weapon.shoot()
                         self.check_shoot_hit(damage)
                # Cambio de arma con rueda del mouse
                elif event.button == 4:  # Rueda hacia arriba
                    self.player.change_weapon(-1)
                elif event.button == 5:  # Rueda hacia abajo
                    self.player.change_weapon(1)
    
    def try_open_door(self):
        """Intenta abrir una puerta cercana"""
        player_x, player_y = self.player.get_position()
        player_angle = self.player.get_angle()
        
        # Buscar puertas cercanas en múltiples distancias
        found_door = None
        
        # Verificar varias distancias frente al jugador
        for check_distance in [0.5, 1.0, 1.5, 2.0]:
            check_x = player_x + math.cos(player_angle) * check_distance
            check_y = player_y + math.sin(player_angle) * check_distance
            
            # Verificar si hay una puerta en esa posición
            if is_door(int(check_x), int(check_y)):
                door = get_door_at_position(int(check_x), int(check_y), self.doors)
                if door:
                    found_door = door
                    break
        
        # También verificar puertas muy cercanas (al lado del jugador)
        if not found_door:
            nearby_positions = [
                (int(player_x), int(player_y)),
                (int(player_x + 1), int(player_y)),
                (int(player_x - 1), int(player_y)),
                (int(player_x), int(player_y + 1)),
                (int(player_x), int(player_y - 1)),
            ]
            
            for px, py in nearby_positions:
                if is_door(px, py):
                    door = get_door_at_position(px, py, self.doors)
                    if door:
                        found_door = door
                        break
        
        # Abrir la puerta si se encontró una
        if found_door:
            if not found_door.is_open and not found_door.is_opening:
                found_door.open()
                self.sound_manager.play('door')

    def check_shoot_hit(self, damage):
        """Verifica si el disparo impactó a un enemigo"""
        player_x, player_y = self.player.get_position()
        player_angle = self.player.get_angle()
        
        hit_enemy = None
        min_dist = float('inf')
        
        for enemy in self.enemies:
            if enemy.dead: continue
            
            # Vector al enemigo
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Ángulo al enemigo
            enemy_angle = math.atan2(dy, dx) - player_angle
            
            # Normalizar ángulo
            while enemy_angle > math.pi: enemy_angle -= 2 * math.pi
            while enemy_angle < -math.pi: enemy_angle += 2 * math.pi
            
            # Verificar si está en la mira (margen de error pequeño)
            if abs(enemy_angle) < 0.15: # Un poco más indulgente
                # Verificar LOS
                if self.raycaster.has_line_of_sight(player_x, player_y, enemy.x, enemy.y):
                    if dist < min_dist:
                        min_dist = dist
                        hit_enemy = enemy
        
        if hit_enemy:
            hit_enemy.take_damage(damage)
            print(f"Hit enemy! HP: {hit_enemy.health}")


    
    def update(self):
        """Actualiza el estado del juego"""
        # Calcular delta time (opcional pero recomendado, aquí usaremos fijo por ahora)
        dt = 1
        
        # Obtener teclas presionadas
        keys = pygame.key.get_pressed()
        
        # Actualizar jugador (teclado y mouse)
        self.player.move(keys)
        self.player.handle_mouse(dt)
        
        # Actualizar puertas
        for door in self.doors:
            door.update()
            
        # Actualizar enemigos
        for enemy in self.enemies:
            enemy.update()
            
        self.weapon.update()
        
        # Lanzar rayos
        player_x, player_y = self.player.get_position()
        player_angle = self.player.get_angle()
        self.raycaster.cast_rays(player_x, player_y, player_angle)
        
        # Actualizar distancias de sprites
        for sprite in self.sprites:
            sprite.calculate_distance(player_x, player_y)
            sprite.get_sprite_projection(
                player_x, player_y, player_angle,
                settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
            )
    
    def render(self):
        """Renderiza la escena"""
        # Limpiar pantalla
        self.screen.fill(settings.BLACK)
        
        # Renderizar escena 3D
        rays = self.raycaster.get_rays()
        # Combinar sprites y enemigos para el renderizado
        all_sprites = self.sprites + self.enemies
        self.renderer.render_scene(rays, self.player, all_sprites)
        
        # Dibujar arma
        self.weapon.draw()
        
        # Renderizar UI
        self.renderer.draw_minimap(self.player)
        self.renderer.draw_fps(self.clock.get_fps())
        self.renderer.draw_crosshair()
        
        # Renderizar HUD
        self.hud.draw(
            self.player.health,
            self.player.ammo,
            self.player.current_weapon,
            self.player.lives,
            self.player.score
        )
        
        # Actualizar pantalla
        pygame.display.flip()
    
    def run(self):
        """Loop principal del juego"""
        print("=== Wolfenstein 3D - PyGame ===")
        print("Controles:")
        print("  WASD - Movimiento")
        print("  Flechas Izquierda/Derecha - Rotar cámara")
        print("  Mouse - Mirar alrededor")
        print("  Clic Izquierdo - Disparar")
        print("  1/2/3/4 - Cambiar arma")
        print("  Rueda del Mouse - Cambiar arma")
        print("  ESPACIO - Abrir puerta")
        print("  ESC - Salir")
        print("\n¡Iniciando juego!")
        
        while self.running:
            # Manejar eventos
            self.handle_events()
            
            # Actualizar
            self.update()
            
            # Renderizar
            self.render()
            
            # Controlar FPS
            self.clock.tick(settings.FPS)
        
        # Cerrar PyGame
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
