import pygame
import os


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sound_dir = os.path.join(self.base_dir, 'sound')
        
        # Inicializar mixer
        pygame.mixer.init()
        
        self.load_sounds()
        
    def load_sounds(self):
        """Carga los sonidos del juego"""
        sound_files = {
            'pistol': 'Pistol.wav',
            'door': 'Door.wav',
            'death': 'Death 1.wav',
            'pain': 'Player Pain 1.wav',
            'pickup': 'Pickup.wav',
            'thud': 'Thud!.wav',
            'achtung': 'Achtung!.wav',
            'guten_tag': 'Guten Tag!.wav'
        }
        
        print("Cargando sonidos...")
        for name, filename in sound_files.items():
            filepath = os.path.join(self.sound_dir, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                    print(f"  ✓ Sonido {name} cargado")
                except Exception as e:
                    print(f"  ! Error cargando sonido {name}: {e}")
            else:
                print(f"  ! Archivo de sonido no encontrado: {filename}")
                
    def play(self, name):
        """Reproduce un sonido"""
        if name in self.sounds:
            self.sounds[name].play()
            
    def play_random_enemy_sound(self):
        """Reproduce un sonido de enemigo aleatorio"""
        import random
        enemy_sounds = ['achtung', 'guten_tag']
        sound = random.choice(enemy_sounds)
        self.play(sound)
