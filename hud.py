import pygame
import os

class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Altura del HUD
        self.hud_height = 100
        self.hud_y = self.screen_height - self.hud_height
        
        # Fuentes
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Colores clásicos de Wolfenstein 3D
        self.hud_bg_color = (0, 0, 170)      # Azul oscuro de fondo
        self.border_color = (0, 170, 170)    # Cian para bordes
        self.text_color = (255, 255, 255)    # Blanco
        self.label_color = (170, 170, 170)   # Gris claro para etiquetas
        self.bg_gray = (50, 50, 50)          # Gris oscuro para fondo general
        self.gold_color = (255, 215, 0)      # Dorado (por si acaso)
        
        # Inicializar variables de imágenes
        self.bj_faces = []
        self.player_face = None  # Needed for fallback or currently displayed face
        self.weapon_images = {}
        
        # Cargar imágenes del HUD
        self.load_hud_images()
        
    def load_hud_images(self):
        """Carga las imágenes del HUD"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sprite_dir = os.path.join(base_dir, 'sprites')
        
        # Intentar importar Pillow para fallback
        try:
            from PIL import Image
            HAS_PILLOW = True
        except ImportError:
            HAS_PILLOW = False
            
        def load_image_safe(path, size=None):
            if not os.path.exists(path):
                return None
            
            try:
                img = pygame.image.load(path).convert_alpha()
                if size:
                    img = pygame.transform.scale(img, size)
                print(f"  ✓ HUD Image {os.path.basename(path)} cargada (PyGame)")
                return img
            except Exception as e:
                print(f"  ! Error PyGame cargando HUD image {os.path.basename(path)}: {e}")
                if HAS_PILLOW:
                    try:
                        pil_img = Image.open(path).convert('RGBA')
                        mode = pil_img.mode
                        img_size = pil_img.size
                        data = pil_img.tobytes()
                        img = pygame.image.fromstring(data, img_size, mode).convert_alpha()
                        if size:
                            img = pygame.transform.scale(img, size)
                        print(f"  ✓ HUD Image {os.path.basename(path)} cargada (Pillow)")
                        return img
                    except Exception as pil_e:
                        print(f"  ! Error Pillow cargando HUD image {os.path.basename(path)}: {pil_e}")
                return None

        # Cara del jugador (BJ)
        face_path = os.path.join(sprite_dir, 'bjface.png')
        raw_face = load_image_safe(face_path)
        
        self.bj_faces = []
        if raw_face:
            # The image is 672x32, containing 21 faces of 32x32
            # We need to slice it
            sheet_w = raw_face.get_width()
            sheet_h = raw_face.get_height()
            # Assuming square faces based on height
            face_size = sheet_h
            
            num_faces = sheet_w // face_size
            
            for i in range(num_faces):
                # Create subsurface for each face
                rect = (i * face_size, 0, face_size, face_size)
                try:
                    face = raw_face.subsurface(rect).copy()
                    self.bj_faces.append(face)
                except Exception as e:
                    print(f"  ! Error slicing face {i}: {e}")
            
            print(f"  ✓ Loaded {len(self.bj_faces)} BJ face frames")
            
            # Set default face
            if self.bj_faces:
                self.player_face = self.bj_faces[0]
            
        # Armas del HUD
        self.weapon_images = {}
        weapon_files = {
            'knife': 'hudknife.png',
            'pistol': 'hudgun.png',
            'machinegun': 'hudmachinegun.png',
            'minigun': 'hudmini.png'
        }
        
        for weapon_name, filename in weapon_files.items():
            path = os.path.join(sprite_dir, filename)
            self.weapon_images[weapon_name] = load_image_safe(path, (60, 60))
            
    def draw_panel(self, surface, x, y, width, height, label, value, is_percentage=False):
        """Dibuja un panel individual del HUD"""
        # Fondo del panel
        pygame.draw.rect(surface, self.hud_bg_color, (x, y, width, height))
        
        # Bordes (efecto 3D simple)
        pygame.draw.rect(surface, self.border_color, (x, y, width, height), 2)
        
        # Etiqueta
        label_surf = self.font_small.render(label, True, self.label_color)
        label_rect = label_surf.get_rect(center=(x + width // 2, y + 15))
        surface.blit(label_surf, label_rect)
        
        # Valor
        val_str = str(value)
        if is_percentage:
            val_str += "%"
        val_surf = self.font_large.render(val_str, True, self.text_color)
        val_rect = val_surf.get_rect(center=(x + width // 2, y + 50))
        surface.blit(val_surf, val_rect)

    def draw(self, player_health, player_ammo, current_weapon, player_lives, score):
        """Dibuja el HUD completo estilo Wolfenstein 3D"""
        # Fondo general (gris oscuro detrás de los paneles)
        hud_surface = pygame.Surface((self.screen_width, self.hud_height))
        hud_surface.fill(self.bg_gray)
        
        # Borde superior cian
        pygame.draw.line(hud_surface, self.border_color, (0, 0), (self.screen_width, 0), 4)
        
        # Dimensiones y posiciones
        panel_h = self.hud_height - 10
        y_pos = 5
        
        # Anchos de paneles (proporcionales)
        w_floor = self.screen_width * 0.1
        w_score = self.screen_width * 0.15
        w_lives = self.screen_width * 0.1
        w_face = self.screen_width * 0.1
        w_health = self.screen_width * 0.15
        w_ammo = self.screen_width * 0.1
        w_weapon = self.screen_width * 0.3
        
        current_x = 0
        
        # 1. FLOOR (Nivel)
        self.draw_panel(hud_surface, current_x, y_pos, w_floor, panel_h, "FLOOR", 1)
        current_x += w_floor
        
        # 2. SCORE
        self.draw_panel(hud_surface, current_x, y_pos, w_score, panel_h, "SCORE", score)
        current_x += w_score
        
        # 3. LIVES
        self.draw_panel(hud_surface, current_x, y_pos, w_lives, panel_h, "LIVES", player_lives)
        current_x += w_lives
        
        # 4. FACE (Cara)
        pygame.draw.rect(hud_surface, self.hud_bg_color, (current_x, y_pos, w_face, panel_h))
        pygame.draw.rect(hud_surface, self.border_color, (current_x, y_pos, w_face, panel_h), 2)
        
        # Determine which face to show based on health
        face_to_draw = self.player_face
        if self.bj_faces:
            # Wolf3D typically has 7 health states (100-85, 84-70, etc.)
            # and 3 view angles per state (straight, right, left) -> total 21
            # For simplicity, we'll pick the 'straight' face for each health bracket
            # The straight faces are usually at indices 0, 3, 6, 9, 12, 15, 18, (20=dead?)
            # Actually, standard strip is: 
            # [Health 100: C, R, L], [Health 85: C, R, L], ...
            # Let's verify mapping later, for now assuming sets of 3.
            
            # Simple mapping: 7 tiers of health
            # Health 100-86 -> Tier 0
            # Health 85-71 -> Tier 1
            # ...
            # Health 15-1  -> Tier 6
            # Health 0     -> Tier 7 (Dead)
            
            health_percentage = max(0, min(100, int(player_health)))
            if health_percentage <= 0:
                 # Dead face (last one usually)
                 face_idx = min(20, len(self.bj_faces) - 1)
            else:
                # Invert logic: 100 is index 0.
                # (100 - health) approx 0..99
                # 7 tiers * 14.3 health per tier
                # tier = int((100 - health) / 14.3)
                tier = int((100 - health_percentage) / 14.3)
                tier = max(0, min(6, tier))
                
                # Each tier has 3 faces. We'll show the center one (index 1 of the group? or 0?)
                # Usually: Center, Right, Left or similar.
                # Let's try index = tier * 3 + 1 (Center often has some animation?)
                # Or just tier * 3 for now.
                face_idx = tier * 3
                
                # Verify bounds
                if face_idx >= len(self.bj_faces):
                    face_idx = 0
            
            face_to_draw = self.bj_faces[face_idx]

        if face_to_draw:
            # Mantener proporción de aspecto
            img_rect = face_to_draw.get_rect()
            aspect_ratio = img_rect.width / img_rect.height
            
            # Calcular nuevas dimensiones ajustadas al panel (con margen)
            target_h = panel_h - 10
            target_w = int(target_h * aspect_ratio)
            
            # Si el ancho excede el panel, ajustar por ancho
            if target_w > w_face - 10:
                target_w = w_face - 10
                target_h = int(target_w / aspect_ratio)
            
            scaled_face = pygame.transform.scale(face_to_draw, (target_w, target_h))
            face_rect = scaled_face.get_rect(center=(current_x + w_face // 2, y_pos + panel_h // 2))
            hud_surface.blit(scaled_face, face_rect)
        current_x += w_face
        
        # 5. HEALTH
        self.draw_panel(hud_surface, current_x, y_pos, w_health, panel_h, "HEALTH", int(player_health), True)
        current_x += w_health
        
        # 6. AMMO
        self.draw_panel(hud_surface, current_x, y_pos, w_ammo, panel_h, "AMMO", int(player_ammo))
        current_x += w_ammo
        
        # 7. WEAPON (Arma)
        pygame.draw.rect(hud_surface, self.hud_bg_color, (current_x, y_pos, w_weapon, panel_h))
        pygame.draw.rect(hud_surface, self.border_color, (current_x, y_pos, w_weapon, panel_h), 2)
        if current_weapon in self.weapon_images and self.weapon_images[current_weapon]:
            img = self.weapon_images[current_weapon]
            # Escalar arma para que encaje bien
            img_rect = img.get_rect(center=(current_x + w_weapon // 2, y_pos + panel_h // 2))
            hud_surface.blit(img, img_rect)
            
        # Dibujar el HUD en la pantalla
        self.screen.blit(hud_surface, (0, self.hud_y))
    
    def get_hud_height(self):
        """Retorna la altura del HUD"""
        return self.hud_height
