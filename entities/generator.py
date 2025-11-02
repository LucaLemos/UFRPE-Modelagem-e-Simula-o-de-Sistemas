import pygame
from config import Colors, GridPositions, ElementSizes
from utils.grid_helper import GridHelper
from entities.process import Process

class ProcessGenerator:
    def __init__(self):
        col, row = GridPositions.GENERATOR
        width_cells, height_cells = ElementSizes.GENERATOR
        
        self.x, self.y, self.width, self.height = GridHelper.grid_to_pixels(
            col, row, width_cells, height_cells
        )
        
        self.triangle_size = min(self.width, self.height) * 0.8
        self.color = Colors.GREEN
        self.next_process_id = 1
        self.is_stopped = False  # New flag to control if generator is stopped
    
    def is_clicked(self, pos):
        """Verifica se o gerador foi clicado"""
        x, y = pos
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def toggle_stop(self):
        """Alterna entre parado e executando"""
        if self.is_stopped:
            self.resume()
        else:
            self.stop()
    
    def stop(self):
        """Para o gerador"""
        if not self.is_stopped:
            self.is_stopped = True
            print("Gerador parado")
    
    def resume(self):
        """Retoma o gerador"""
        if self.is_stopped:
            self.is_stopped = False
            print("Gerador retomado")
    
    def create_process(self) -> Process:
        """Cria um novo processo"""
        if not self.is_stopped:
            center_x, center_y = self.get_center()
            new_process = Process(self.next_process_id, center_x, center_y)
            self.next_process_id += 1
            return new_process
        return None
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o gerador na tela"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Cor baseada no estado
        current_color = Colors.DARK_GRAY if self.is_stopped else self.color
        
        # Triângulo
        points = [
            (center_x, center_y - self.triangle_size // 2),  # Topo
            (center_x - self.triangle_size // 2, center_y + self.triangle_size // 2),  # Esq
            (center_x + self.triangle_size // 2, center_y + self.triangle_size // 2)   # Dir
        ]
        
        pygame.draw.polygon(screen, current_color, points)
        pygame.draw.polygon(screen, Colors.WHITE, points, 2)
        
        # Texto
        font = pygame.font.SysFont(None, 24)
        status = " (PARADO)" if self.is_stopped else ""
        text = font.render(f"Gerador{status}", True, Colors.WHITE)
        screen.blit(text, (center_x - 45, center_y + self.triangle_size // 2 + 10))
    
    def get_center(self) -> tuple:
        return self.x + self.width // 2, self.y + self.height // 2