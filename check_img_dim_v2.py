import os

def check_dims():
    base_dir = os.getcwd()
    path = os.path.join(base_dir, 'sprites', 'wolfweapons.png')
    
    if not os.path.exists(path):
        print("File not found:", path)
        return

    print(f"Checking: {path}")

    try:
        from PIL import Image
        with Image.open(path) as img:
            print(f"Dimensions (Pillow): {img.width}x{img.height}")
            return
    except ImportError:
        pass
        
    try:
        import pygame
        img = pygame.image.load(path)
        print(f"Dimensions (PyGame): {img.get_width()}x{img.get_height()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_dims()
