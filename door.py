import pygame
import time


class Door:
    def __init__(self, x, y):
        """
        Inicializa una puerta
        x, y: Posición de la puerta en el mapa
        """
        self.x = int(x)
        self.y = int(y)
        self.is_open = False
        self.is_opening = False
        self.is_closing = False
        self.open_amount = 0.0  # 0.0 = cerrada, 1.0 = completamente abierta
        self.open_time = None  # Tiempo cuando se abrió la puerta
        self.auto_close_delay = 5.0  # Segundos antes de cerrarse automáticamente
        
        # Velocidad de apertura/cierre (valores más bajos = más lento y realista)
        self.open_speed = 0.012   # Aproximadamente 2.8 segundos para abrir completamente
        self.close_speed = 0.015  # Cierra un poco más rápido (2.2 segundos)
        
    def open(self):
        """Inicia la apertura de la puerta"""
        if not self.is_open and not self.is_opening:
            self.is_opening = True
            self.is_closing = False
            self.open_time = time.time()
            
    def close(self):
        """Inicia el cierre de la puerta"""
        if self.is_open and not self.is_closing:
            self.is_closing = True
            self.is_opening = False
            
    def update(self):
        """Actualiza el estado de la puerta"""
        # Si está abriéndose
        if self.is_opening:
            self.open_amount += self.open_speed
            if self.open_amount >= 1.0:
                self.open_amount = 1.0
                self.is_opening = False
                self.is_open = True
                
        # Si está cerrándose
        if self.is_closing:
            self.open_amount -= self.close_speed
            if self.open_amount <= 0.0:
                self.open_amount = 0.0
                self.is_closing = False
                self.is_open = False
                
        # Auto-cerrar después del delay
        if self.is_open and not self.is_closing and self.open_time:
            elapsed = time.time() - self.open_time
            if elapsed >= self.auto_close_delay:
                self.close()
                
    def get_position(self):
        """Retorna la posición de la puerta"""
        return (self.x, self.y)
        
    def is_passable(self):
        """Retorna True si la puerta está lo suficientemente abierta para pasar"""
        return self.open_amount > 0.7
        
    def get_wall_offset(self):
        """
        Retorna el offset de la textura de la puerta basado en cuánto está abierta.
        Cuando está cerrada (0.0), offset = 0.0
        Cuando está abierta (1.0), offset = 1.0 (puerta completamente a un lado)
        """
        return self.open_amount
