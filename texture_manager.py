import pygame
import os
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


class TextureManager:
    def __init__(self):
        self.wall_textures = {}
        self.sprite_textures = {}
        self.texture_size = 64  # Standard texture size

    def load_textures(self):
        """Load all wall and sprite textures, with fallbacks and proper alpha handling."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print("Cargando texturas...")

        # ---- Wall textures ----
        wall_texture_files = {
            1: os.path.join(base_dir, 'textures', '1.png'),
            2: os.path.join(base_dir, 'textures', '2.png'),
            3: os.path.join(base_dir, 'textures', '3.png'),
            4: os.path.join(base_dir, 'textures', '4.png'),
            5: os.path.join(base_dir, 'textures', '5.png'),
            6: os.path.join(base_dir, 'textures', '6.png'),
            7: os.path.join(base_dir, 'textures', 'door.png'),
        }
        for wall_id, path in wall_texture_files.items():
            texture_loaded = False
            if os.path.exists(path):
                try:
                    tex = pygame.image.load(path).convert()
                    tex = pygame.transform.scale(tex, (self.texture_size, self.texture_size))
                    self.wall_textures[wall_id] = tex
                    texture_loaded = True
                    print(f"  ✓ Textura {wall_id} cargada desde archivo (PyGame)")
                except Exception as e:
                    print(f"  ! Error PyGame cargando textura {wall_id}: {e}")
                    if HAS_PILLOW:
                        try:
                            pil_img = Image.open(path).convert('RGB')
                            mode = pil_img.mode
                            size = pil_img.size
                            data = pil_img.tobytes()
                            tex = pygame.image.fromstring(data, size, mode).convert()
                            tex = pygame.transform.scale(tex, (self.texture_size, self.texture_size))
                            self.wall_textures[wall_id] = tex
                            texture_loaded = True
                            print(f"  ✓ Textura {wall_id} cargada con Pillow (RGB)")
                        except Exception as pil_e:
                            print(f"  ! Error Pillow cargando textura {wall_id}: {pil_e}")
            if not texture_loaded:
                # fallback solid color
                tex = pygame.Surface((self.texture_size, self.texture_size))
                tex.fill(self._get_fallback_color(wall_id))
                self.wall_textures[wall_id] = tex
                print(f"  ✓ Textura {wall_id} usando color sólido")

        # ---- Sprite textures ----
        sprite_files = {
            'barrel': os.path.join(base_dir, 'sprites', 'barrel.png'),
            'pillar': os.path.join(base_dir, 'sprites', 'pillar.png'),
            'greenlight': os.path.join(base_dir, 'sprites', 'greenlight.png'),
            'guard': os.path.join(base_dir, 'sprites', 'guard.png'),
        }
        for name, path in sprite_files.items():
            sprite_loaded = False
            if os.path.exists(path):
                try:
                    spr = pygame.image.load(path).convert_alpha()
                    spr.set_colorkey((0, 0, 0))
                    self.sprite_textures[name] = spr
                    sprite_loaded = True
                    print(f"  ✓ Sprite {name} cargado desde archivo (PyGame)")
                except Exception as e:
                    print(f"  ! Error PyGame cargando sprite {name}: {e}")
                    if HAS_PILLOW:
                        try:
                            pil_img = Image.open(path).convert('RGBA')
                            mode = pil_img.mode
                            size = pil_img.size
                            data = pil_img.tobytes()
                            spr = pygame.image.fromstring(data, size, mode).convert_alpha()
                            spr.set_colorkey((0, 0, 0))
                            self.sprite_textures[name] = spr
                            sprite_loaded = True
                            print(f"  ✓ Sprite {name} cargado con Pillow")
                        except Exception as pil_e:
                            print(f"  ! Error Pillow cargando sprite {name}: {pil_e}")
            if not sprite_loaded:
                # fallback simple circle sprite
                spr = pygame.Surface((64, 64), pygame.SRCALPHA)
                color_map = {
                    'barrel': (139, 69, 19),
                    'pillar': (192, 192, 192),
                    'greenlight': (0, 255, 0),
                    'guard': (255, 0, 0),
                }
                color = color_map.get(name, (255, 0, 255))
                pygame.draw.circle(spr, color, (32, 32), 30)
                self.sprite_textures[name] = spr
                print(f"  ✓ Sprite {name} usando forma de respaldo")

    def _get_fallback_color(self, wall_id):
        """Fallback solid colors for missing wall textures."""
        colors = {
            1: (128, 128, 128),  # Gray
            2: (139, 69, 19),    # Brown
            3: (0, 0, 139),      # Dark blue
            4: (128, 0, 0),      # Dark red
            5: (128, 0, 128),    # Purple
            6: (0, 128, 0),      # Green
            7: (200, 200, 200),  # Light gray fallback for door
        }
        return colors.get(wall_id, (128, 128, 128))

    def get_wall_texture(self, wall_id):
        """Retrieve wall texture, fallback to texture 1 if missing."""
        return self.wall_textures.get(wall_id, self.wall_textures.get(1))

    def get_sprite_texture(self, sprite_name):
        """Retrieve sprite texture."""
        return self.sprite_textures.get(sprite_name)

    def get_texture_column(self, texture, column, height):
        """Extract a column from a texture and scale to desired height."""
        if column < 0 or column >= self.texture_size:
            column = 0
        column_surface = pygame.Surface((1, self.texture_size))
        column_surface.blit(texture, (0, 0), (column, 0, 1, self.texture_size))
        if height > 0:
            column_surface = pygame.transform.scale(column_surface, (1, int(height)))
        return column_surface
