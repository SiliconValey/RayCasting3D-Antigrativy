import pygame
import settings
from map import WORLD_MAP, MAP_WIDTH, MAP_HEIGHT, get_door_at_position


class Renderer:
    def __init__(self, screen, texture_manager):
        self.screen = screen
        self.texture_manager = texture_manager
        self.font = pygame.font.Font(None, 36)
        self.doors = None
        
    def set_doors(self, doors):
        """Asigna las puertas al renderer"""
        self.doors = doors
        
    def render_scene(self, rays, player, sprites):
        """Renderiza la escena completa"""
        # Obtener offset de bobbing
        bob_offset = player.get_bobbing_offset()
        
        # Dibujar cielo y suelo
        self._draw_background()
        
        # Dibujar paredes
        self._draw_walls(rays, bob_offset)
        
        # Dibujar sprites
        self._draw_sprites(sprites, rays, player, bob_offset)
        
    def _draw_background(self):
        """Dibuja el cielo y el suelo con gradiente para simular textura/profundidad"""
        # Cielo (Color sólido simple)
        pygame.draw.rect(
            self.screen,
            settings.CEILING_COLOR,
            (0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT // 2)
        )
        
        # Suelo (Gradiente vertical para dar sensación de profundidad)
        # Esto es mucho más rápido que el floor casting real en Python puro
        half_height = settings.SCREEN_HEIGHT // 2
        
        # Optimización: Dibujar en bandas de 2 píxeles si se necesita velocidad, 
        # pero línea por línea da mejor gradiente.
        # Color base: settings.FLOOR_COLOR es gris oscuro (50, 50, 50)
        
        for y in range(half_height, settings.SCREEN_HEIGHT):
            # Ratio: 0 en horizonte, 1 en parte inferior
            ratio = (y - half_height) / half_height
            
            # Hacerlo más oscuro al fondo y más claro cerca
            # Base 20, Max 80 (Gris)
            val = int(20 + 60 * ratio)
            
            # Simular un poco de "ruido" o patrón checkerboard sería caro per-pixel.
            # Nos quedamos con gradiente suave por ahora.
            color = (val, val, val)
            
            pygame.draw.line(self.screen, color, (0, y), (settings.SCREEN_WIDTH, y))
    
    def _draw_walls(self, rays, bob_offset=0):
        """Dibuja las paredes usando los rayos"""
        for i, ray in enumerate(rays):
            wall_height = ray['wall_height']
            wall_type = ray['wall_type']
            texture_x = ray['texture_x']
            
            # Calcular posición vertical de la pared con bobbing
            wall_top = (settings.SCREEN_HEIGHT - wall_height) / 2 + bob_offset
            wall_bottom = wall_top + wall_height
            
            # Obtener textura
            texture = self.texture_manager.get_wall_texture(wall_type)
            
            # Obtener columna de textura
            tex_col = int(texture_x * self.texture_manager.texture_size)
            
            # (Legacy door logic removed - RayCaster DDA handles sliding offset/transparency now)
            
            # Obtener columna escalada
            # IMPORTANTE: Escalar al ancho de SCALE para evitar huecos entre columnas
            column = self.texture_manager.get_texture_column(texture, tex_col, wall_height)
            column = pygame.transform.scale(column, (settings.SCALE, int(wall_height)))
            
            # Dibujar columna en pantalla
            x_pos = i * settings.SCALE
            self.screen.blit(column, (x_pos, wall_top))
    
    def _draw_sprites(self, sprites, rays, player, bob_offset=0):
        """Dibuja los sprites en la escena"""
        # Ordenar sprites por distancia (más lejanos primero)
        sorted_sprites = sorted(sprites, key=lambda s: s.distance, reverse=True)
        
        # Crear buffer de profundidad desde los rayos
        depth_buffer = [ray['depth'] for ray in rays]
        
        player_x, player_y = player.get_position()
        
        for sprite in sorted_sprites:
            projection = sprite.get_sprite_projection(
                player_x, player_y, player.angle, 
                settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT
            )
            
            if projection is None:
                continue
            
            # Obtener textura del sprite
            texture = sprite.texture
            if texture is None:
                continue
            
            # Escalar sprite
            try:
                scaled_sprite = pygame.transform.scale(
                    texture,
                    (projection['width'], projection['height'])
                ).convert_alpha()
            except Exception as e:
                print(f"Error escalando sprite: {e}, dims: {projection['width']}x{projection['height']}")
                continue
            
            # Calcular posición de dibujado con bobbing
            sprite_x = projection['x'] - projection['width'] // 2
            sprite_y = projection['y'] + bob_offset
            
            # Dibujar sprite columna por columna, verificando depth buffer
            for x in range(projection['width']):
                screen_x = sprite_x + x
                
                # Verificar límites de pantalla
                if screen_x < 0 or screen_x >= settings.SCREEN_WIDTH:
                    continue
                
                # Verificar depth buffer
                ray_index = screen_x // settings.SCALE
                if ray_index >= len(depth_buffer):
                    continue
                    
                if projection['distance'] < depth_buffer[ray_index]:
                    # Dibujar columna del sprite
                    column_rect = pygame.Rect(x, 0, 1, projection['height'])
                    self.screen.blit(
                        scaled_sprite,
                        (screen_x, sprite_y),
                        column_rect
                    )
    
    def draw_minimap(self, player):
        """Dibuja el minimap"""
        minimap_surface = pygame.Surface(
            (MAP_WIDTH * settings.MINIMAP_TILE_SIZE, 
             MAP_HEIGHT * settings.MINIMAP_TILE_SIZE)
        )
        minimap_surface.set_alpha(200)
        
        # Dibujar mapa
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                color = settings.WHITE if WORLD_MAP[y][x] != 0 else settings.BLACK
                pygame.draw.rect(
                    minimap_surface,
                    color,
                    (x * settings.MINIMAP_TILE_SIZE,
                     y * settings.MINIMAP_TILE_SIZE,
                     settings.MINIMAP_TILE_SIZE,
                     settings.MINIMAP_TILE_SIZE)
                )
        
        # Dibujar jugador
        player_x, player_y = player.get_position()
        pygame.draw.circle(
            minimap_surface,
            settings.RED,
            (int(player_x * settings.MINIMAP_TILE_SIZE),
             int(player_y * settings.MINIMAP_TILE_SIZE)),
            3
        )
        
        # Dibujar en pantalla
        self.screen.blit(
            minimap_surface,
            (settings.MINIMAP_OFFSET_X, settings.MINIMAP_OFFSET_Y)
        )
    
    def draw_fps(self, fps):
        """Dibuja el contador de FPS"""
        fps_text = self.font.render(f'FPS: {int(fps)}', True, settings.YELLOW)
        self.screen.blit(
            fps_text,
            (settings.SCREEN_WIDTH - 150, 10)
        )
    
    def draw_crosshair(self):
        """Dibuja una mira en el centro de la pantalla"""
        center_x = settings.SCREEN_WIDTH // 2
        center_y = settings.SCREEN_HEIGHT // 2
        crosshair_size = 10
        
        # Línea horizontal
        pygame.draw.line(
            self.screen,
            settings.WHITE,
            (center_x - crosshair_size, center_y),
            (center_x + crosshair_size, center_y),
            2
        )
        
        # Línea vertical
        pygame.draw.line(
            self.screen,
            settings.WHITE,
            (center_x, center_y - crosshair_size),
            (center_x, center_y + crosshair_size),
            2
        )
