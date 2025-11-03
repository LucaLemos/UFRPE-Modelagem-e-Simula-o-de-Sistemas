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
        self.is_stopped = False  # New flag to control if computer is stopped
        self.pre_stop_state = None  # To remember state before stopping
        self.processing_time_ms = 2000  # Default: 2 seconds (now adjustable)
    
    def is_clicked(self, pos):
        """Verifica se a CPU foi clicada"""
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
        """Para a CPU"""
        if not self.is_stopped:
            self.is_stopped = True
            self.pre_stop_state = self.is_idle
            print("CPU parada")
    
    def resume(self):
        """Retoma a CPU"""
        if self.is_stopped:
            self.is_stopped = False
            print("CPU retomada")
    
    def set_processing_time(self, seconds):
        """Define o tempo de processamento em segundos"""
        if seconds > 0:
            self.processing_time_ms = int(seconds * 1000)  # Convert to milliseconds
            print(f"Tempo de processamento alterado para: {seconds:.2f} segundos")
    
    @property
    def color(self) -> tuple:
        """Retorna a cor baseada no estado"""
        if self.is_stopped:
            return Colors.DARK_GRAY
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
        if self.is_stopped:
            status = "PARADA"
        else:
            status = "PROCESSANDO" if not self.is_idle else "OCIOSO"
        status_text = font.render(status, True, Colors.WHITE)
        screen.blit(status_text, (self.x + self.width // 2 - 50, self.y + self.height // 2 + 10))
        
        # Processo atual
        if not self.is_idle and self.current_process and not self.is_stopped:
            process_text = font.render(f"P{self.current_process.id}", True, Colors.WHITE)
            screen.blit(process_text, (self.x + self.width // 2 - 10, self.y + self.height // 2 + 40))
    
    def start_processing(self, process: Process) -> None:
        """Inicia o processamento de um processo"""
        if not self.is_stopped:
            self.current_process = process
            self.is_idle = False
            # Set the processing time for the process
            process.processing_time_ms = self.processing_time_ms
            process.start_processing()
    
    def check_processing_complete(self) -> bool:
        """Verifica se o processamento atual foi concluído"""
        if not self.is_stopped and self.current_process and self.current_process.is_processing_complete():
            self.current_process = None
            self.is_idle = True
            return True
        return False
    
    def get_center(self) -> tuple:
        return self.x, self.y + self.height // 2