import pygame
from config import Colors, ElementSizes
from utils.grid_helper import GridHelper
from entities.process import Process
from entities.process_states import ProcessState

class Computer:
    def __init__(self, computer_id=1, grid_position=None, color=None):
        # Usar posição específica ou padrão
        if grid_position is None:
            from config import GridPositions
            if computer_id == 1:
                grid_position = GridPositions.COMPUTER_1
            elif computer_id == 2:
                grid_position = GridPositions.COMPUTER_2
            else:
                grid_position = GridPositions.COMPUTER_3
        
        col, row = grid_position
        width_cells, height_cells = ElementSizes.COMPUTER
        
        self.x, self.y, self.width, self.height = GridHelper.grid_to_pixels(
            col, row, width_cells, height_cells
        )
        
        self.computer_id = computer_id
        self.name = f"CPU_{computer_id}"
        self.is_idle = True
        self.current_process = None
        self.is_stopped = False
        self.pre_stop_state = None
        self.processing_time_ms = 2000  # Default: 2 seconds
        
        # Cor específica para esta CPU
        self.base_color = color if color else Colors.RED
        self.queue = []  # Fila própria para esta CPU
    
    @property
    def color(self) -> tuple:
        """Retorna a cor baseada no estado"""
        if self.is_stopped:
            return Colors.DARK_GRAY
        return self.base_color if not self.is_idle else Colors.GRAY
    
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
            print(f"{self.name} parada")
    
    def resume(self):
        """Retoma a CPU"""
        if self.is_stopped:
            self.is_stopped = False
            print(f"{self.name} retomada")
    
    def set_processing_time(self, seconds):
        """Define o tempo de processamento em segundos"""
        if seconds > 0:
            self.processing_time_ms = int(seconds * 1000)
            print(f"Tempo de processamento de {self.name} alterado para: {seconds:.2f} segundos")
    
    @property
    def queue_length(self):
        """Retorna o tamanho da fila desta CPU"""
        return len(self.queue)
    
    def add_to_queue(self, process):
        """Adiciona processo à fila desta CPU"""
        process.enter_cpu_queue()
        self.queue.append(process)
        return True
    
    def get_next_process(self):
        """Remove e retorna o próximo processo da fila"""
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha a CPU na tela"""
        # Retângulo principal
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, Colors.WHITE, (self.x, self.y, self.width, self.height), 2)
        
        # Informações de texto
        font = pygame.font.SysFont(None, 24)
        title_font = pygame.font.SysFont(None, 28)
        
        # Nome da CPU
        title_text = title_font.render(self.name, True, Colors.WHITE)
        screen.blit(title_text, (self.x + self.width // 2 - 25, self.y + 10))
        
        # Status
        if self.is_stopped:
            status = "PARADA"
        else:
            status = "PROCESSANDO" if not self.is_idle else "OCIOSA"
        status_text = font.render(status, True, Colors.WHITE)
        screen.blit(status_text, (self.x + self.width // 2 - 40, self.y + self.height // 2 - 10))
        
        # Processo atual
        if not self.is_idle and self.current_process and not self.is_stopped:
            process_text = font.render(f"P{self.current_process.id}", True, Colors.WHITE)
            screen.blit(process_text, (self.x + self.width // 2 - 10, self.y + self.height // 2 + 15))
        
        # Tamanho da fila
        queue_text = font.render(f"Fila: {len(self.queue)}", True, Colors.WHITE)
        screen.blit(queue_text, (self.x + self.width // 2 - 20, self.y + self.height - 30))
    
    def start_processing(self, process: Process) -> None:
        """Inicia o processamento de um processo"""
        if not self.is_stopped:
            self.current_process = process
            self.is_idle = False
            # Set the processing time for the process
            process.processing_time_ms = self.processing_time_ms
            process.start_processing()
            print(f"{self.name} iniciou processamento do Processo {process.id}")
    
    def check_processing_complete(self) -> bool:
        """Verifica se o processamento atual foi concluído"""
        if not self.is_stopped and self.current_process and self.current_process.is_processing_complete():
            print(f"{self.name} completou processamento do Processo {self.current_process.id}")
            self.current_process = None
            self.is_idle = True
            return True
        return False
    
    def get_center(self) -> tuple:
        return self.x + self.width // 2, self.y + self.height // 2
    
    def update_queue_positions(self):
        """Atualiza posições visuais dos processos na fila"""
        cpu_x, cpu_y = self.get_center()
        for i, process in enumerate(self.queue):
            if process.state == ProcessState.WAITING_CPU:
                process.x = cpu_x - 60 - (i * 35)
                process.y = cpu_y - 20 + (i % 2) * 40