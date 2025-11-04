import pygame
from config import Colors
from entities.process_states import ProcessState

class Process:
    def __init__(self, process_id: int, spawn_x: int, spawn_y: int):
        self.id = process_id
        self.x = spawn_x
        self.y = spawn_y
        self.radius = 15
        self.speed = 3.0
        self.is_active = True
        self.creation_time = pygame.time.get_ticks()
        
        # Estado do processo
        self.state = ProcessState.CREATED
        
        # Tempo de processamento
        self.processing_time_ms = 2000
        self.processing_start_time = None
        
        # Tempo de entrada na fila da CPU (para controle de timeout)
        self.queue_entry_time = None
    
    @property
    def color(self) -> tuple:
        """Retorna a cor baseada no estado atual"""
        color_map = {
            ProcessState.CREATED: Colors.BLUE,
            ProcessState.IN_QUEUE: Colors.LIGHT_GREEN,
            ProcessState.IN_TRANSIT: Colors.PURPLE,
            ProcessState.WAITING_CPU: Colors.ORANGE,
            ProcessState.PROCESSING: Colors.ORANGE,
            ProcessState.COMPLETED: Colors.DARK_GRAY
        }
        return color_map.get(self.state, Colors.BLUE)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o processo na tela"""
        # Círculo principal
        if self.state in (ProcessState.PROCESSING, ProcessState.WAITING_CPU):
            return

        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, Colors.WHITE, (int(self.x), int(self.y)), self.radius, 2)
        
        # ID do processo
        font = pygame.font.SysFont(None, 20)
        id_text = font.render(str(self.id), True, Colors.WHITE)
        screen.blit(id_text, (self.x - 5, self.y - 8))
        
        # Tempo restante se estiver processando
        if self.state == ProcessState.PROCESSING:
            elapsed = pygame.time.get_ticks() - self.processing_start_time
            remaining = max(0, self.processing_time_ms - elapsed)
            seconds = remaining / 1000.0
            
            time_text = font.render(f"{seconds:.1f}s", True, Colors.WHITE)
            screen.blit(time_text, (self.x - 15, self.y + 15))
        
        # Tempo na fila se estiver esperando
        elif self.state == ProcessState.WAITING_CPU and self.queue_entry_time:
            time_in_queue = (pygame.time.get_ticks() - self.queue_entry_time) / 1000.0
            queue_time_text = font.render(f"{time_in_queue:.1f}s", True, Colors.WHITE)
            screen.blit(queue_time_text, (self.x - 15, self.y + 15))
    
    def start_processing(self) -> None:
        """Inicia o processamento na CPU"""
        self.state = ProcessState.PROCESSING
        self.processing_start_time = pygame.time.get_ticks()
        self.queue_entry_time = None  # Reset queue time when processing starts
    
    def enter_cpu_queue(self):
        """Marca o tempo de entrada na fila da CPU"""
        self.queue_entry_time = pygame.time.get_ticks()
        self.state = ProcessState.WAITING_CPU
    
    def is_processing_complete(self) -> bool:
        """Verifica se o processamento foi concluído"""
        if self.state == ProcessState.PROCESSING:
            elapsed = pygame.time.get_ticks() - self.processing_start_time
            if elapsed >= self.processing_time_ms:
                self.state = ProcessState.COMPLETED
                self.is_active = False
                return True
        return False
    
    def update_position(self, target_x: float, target_y: float) -> bool:
        """Move o processo em direção às coordenadas alvo"""
        if self.state in [ProcessState.IN_TRANSIT, ProcessState.PROCESSING]:
            return True
            
        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx**2 + dy**2)**0.5
        
        if distance > self.speed:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            return False
        else:
            self.x, self.y = target_x, target_y
            return True