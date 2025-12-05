import pygame
import os

class Weapon:
    def __init__(self, screen, player, texture_manager):
        self.screen = screen
        self.player = player
        self.texture_manager = texture_manager
        self.sprites = {} # 'knife': [frames], 'pistol': [frames]...
        self.current_frame = 0
        self.animating = False
        self.last_update = 0
        self.frame_rate = 100 # ms
        
        # Load sprites
        self.load_weapons()
        
    def load_weapons(self):
        # Cargar wolfweapons.png (320x128)
        # Asumiendo 64x64 frames
        # Row 0: Knife (5 frames)
        # Row 1: Pistol (5 frames)
        # Machinegun/Minigun might be elsewhere or reusing?
        # For now, just implement Knife and Pistol from this sheet. 
        # For others, use Pistol as placeholder or try to find them.
        # Actually user has hudmachinegun.png etc, but those are small icons.
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, 'sprites', 'wolfweapons.png')
        
        if os.path.exists(path):
            try:
                sheet = pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"Error PyGame loading weapons: {e}")
                try:
                    from PIL import Image
                    pil_img = Image.open(path).convert('RGBA')
                    mode = pil_img.mode
                    size = pil_img.size
                    data = pil_img.tobytes()
                    sheet = pygame.image.fromstring(data, size, mode).convert_alpha()
                    print("Weapons loaded with Pillow")
                except Exception as pil_e:
                     print(f"Error Pillow loading weapons: {pil_e}")
                     return
            # Escalar si es necesario (pixel art scale)
            # Pero para el arma en mano, queremos que sea grande.
            # 64x64 es muy chico para la pantalla 1280x720. Escalar x4 -> 256x256.
            
            w = 64
            h = 64
            
            frames_knife = [sheet.subsurface((i*w, 0, w, h)) for i in range(5)]
            frames_pistol = [sheet.subsurface((i*w, h, w, h)) for i in range(5)]
            
            # Escalar
            # Escalar para ocupar buena parte de la pantalla (aprox 50-60%)
            target_h = int(self.screen.get_height() * 0.6)
            scale_ratio = target_h / h
            target_w = int(w * scale_ratio)
            
            self.sprites['knife'] = [pygame.transform.scale(img, (target_w, target_h)) for img in frames_knife]
            self.sprites['pistol'] = [pygame.transform.scale(img, (target_w, target_h)) for img in frames_pistol]
            
            # Fallback for others
            self.sprites['machinegun'] = self.sprites['pistol']
            self.sprites['minigun'] = self.sprites['pistol']
            
    def shoot(self):
        if not self.animating:
            self.animating = True
            self.current_frame = 0
            self.last_update = pygame.time.get_ticks()
            
    def update(self):
        if self.animating:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.current_frame += 1
                if self.current_frame >= len(self.sprites.get(self.player.current_weapon, [])):
                    self.animating = False
                    self.current_frame = 0
                    
    def draw(self):
        weapon_sprites = self.sprites.get(self.player.current_weapon)
        if not weapon_sprites:
            return
            
        # Frame actual
        # Si disparando, usa animación. Si no, frame 0 (idle)
        frame_idx = self.current_frame
        
        img = weapon_sprites[frame_idx]
        
        # Centrar abajo con bobbing
        bob_offset = 0
        if hasattr(self.player, 'get_bobbing_offset'):
            bob_offset = self.player.get_bobbing_offset()
            
        r = img.get_rect()
        r.centerx = self.screen.get_width() // 2 + int(bob_offset * 0.5) # Movimiento lateral ligero
        r.bottom = self.screen.get_height() + int(abs(bob_offset)) # Movimiento vertical
        
        self.screen.blit(img, r)
