import pygame
import os

try:
    pygame.init()
    base_dir = os.getcwd()
    path = os.path.join(base_dir, 'sprites', 'bjface.png')
    if not os.path.exists(path):
        print("File not found:", path)
    else:
        img = pygame.image.load(path)
        print(f"Image: {path}")
        print(f"Dimensions: {img.get_width()}x{img.get_height()}")
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
