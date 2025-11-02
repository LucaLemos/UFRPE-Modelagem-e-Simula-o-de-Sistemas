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
    
    def is_clicked(self, pos):
        """Verifica se o gerador foi clicado"""
        x, y = pos
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def create_process(self) -> Process:
        """Cria um novo processo"""
        center_x, center_y = self.get_center()
        new_process = Process(self.next_process_id, center_x, center_y)
        self.next_process_id += 1
        return new_process
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o gerador na tela"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Triângulo
        points = [
            (center_x, center_y - self.triangle_size // 2),  # Topo
            (center_x - self.triangle_size // 2, center_y + self.triangle_size // 2),  # Esq
            (center_x + self.triangle_size // 2, center_y + self.triangle_size // 2)   # Dir
        ]
        
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, Colors.WHITE, points, 2)
        
        # Texto
        font = pygame.font.SysFont(None, 24)
        text = font.render("Gerador", True, Colors.WHITE)
        screen.blit(text, (center_x - 35, center_y + self.triangle_size // 2 + 10))
    
    def get_center(self) -> tuple:
        return self.x + self.width // 2, self.y + self.height // 2