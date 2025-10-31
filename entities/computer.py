import pygame
from config import Colors, GridPositions, ElementSizes
from utils.grid_helper import GridHelper
from entities.process import Process
from entities.process_states import ProcessState

class Computer:
    def __init__(self):
        col, row = GridPositions.COMPUTER
        width_cells, height_cells = ElementSizes.COMPUTER
        
        self.x, self.y, self.width, self.height = GridHelper.grid_to_pixels(
            col, row, width_cells, height_cells
        )
        
        self.is_idle = True
        self.current_process = None
    
    @property
    def color(self) -> tuple:
        """Retorna a cor baseada no estado"""
        return Colors.ORANGE if not self.is_idle else Colors.RED
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha a CPU na tela"""
        # Retângulo principal
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, Colors.WHITE, (self.x, self.y, self.width, self.height), 2)
        
        # Informações de texto
        font = pygame.font.SysFont(None, 30)
        
        # Título
        title_text = font.render("CPU", True, Colors.WHITE)
        screen.blit(title_text, (self.x + self.width // 2 - 20, self.y + self.height // 2 - 30))
        
        # Status
        status = "PROCESSANDO" if not self.is_idle else "OCIOSO"
        status_text = font.render(status, True, Colors.WHITE)
        screen.blit(status_text, (self.x + self.width // 2 - 50, self.y + self.height // 2 + 10))
        
        # Processo atual
        if not self.is_idle and self.current_process:
            process_text = font.render(f"P{self.current_process.id}", True, Colors.WHITE)
            screen.blit(process_text, (self.x + self.width // 2 - 10, self.y + self.height // 2 + 40))
    
    def start_processing(self, process: Process) -> None:
        """Inicia o processamento de um processo"""
        self.current_process = process
        self.is_idle = False
        process.start_processing()
    
    def check_processing_complete(self) -> bool:
        """Verifica se o processamento atual foi concluído"""
        if self.current_process and self.current_process.is_processing_complete():
            self.current_process = None
            self.is_idle = True
            return True
        return False
    
    def get_center(self) -> tuple:
        return self.x, self.y + self.height // 2