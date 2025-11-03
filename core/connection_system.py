import pygame
from typing import List, Optional
from config import Colors, MAX_CONNECTION_CAPACITY, TRANSPORT_SPEED
from entities.process import Process
from entities.process_states import ProcessState

class ConnectionSystem:
    def __init__(self, generator, computer):
        self.generator = generator
        self.computer = computer
        
        # Filas do sistema
        self.input_queue: List[Process] = []      # Fila de entrada
        self.transit_processes: List[Process] = [] # Processos em trânsito
        self.cpu_queue: List[Process] = []        # Fila da CPU
        
        self.transport_speed = TRANSPORT_SPEED
        self.max_capacity = MAX_CONNECTION_CAPACITY
        
        # Pontos de conexão
        self.start_point = generator.get_center()
        self.end_point = computer.get_center()
        
        # Calcular direção
        self._calculate_direction()
    
    def _calculate_direction(self) -> None:
        """Calcula a direção e normaliza o vetor"""
        dx = self.end_point[0] - self.start_point[0]
        dy = self.end_point[1] - self.start_point[1]
        length = (dx**2 + dy**2)**0.5
        
        if length > 0:
            self.direction_x = dx / length
            self.direction_y = dy / length
            self.length = length
        else:
            self.direction_x = self.direction_y = 0
            self.length = 0
    
    def add_process(self, process: Process) -> bool:
        """Adiciona um processo ao sistema se houver capacidade"""
        if self.total_processes < self.max_capacity:
            process.x, process.y = self.start_point
            process.state = ProcessState.IN_QUEUE
            self.input_queue.append(process)
            return True
        return False
    
    @property
    def total_processes(self) -> int:
        """Total de processos em todas as filas"""
        return (len(self.input_queue) + 
                len(self.transit_processes) + 
                len(self.cpu_queue))
    
    @property
    def has_capacity(self) -> bool:
        """Verifica se há capacidade disponível"""
        return self.total_processes < self.max_capacity
    
    def update(self) -> None:
        """Atualiza todo o fluxo do sistema"""
        self._move_from_input_to_transit()
        self._update_transit_processes()
        self._process_cpu_queue()
        self._update_visual_positions()
    
    def _move_from_input_to_transit(self) -> None:
        """Move processos da fila de entrada para trânsito"""
        if self.input_queue and len(self.transit_processes) < 5:
            process = self.input_queue.pop(0)
            process.state = ProcessState.IN_TRANSIT
            self.transit_processes.append(process)
    
    def _update_transit_processes(self) -> None:
        """Atualiza processos em trânsito"""
        arrived_processes = []
        
        for process in self.transit_processes[:]:
            if process.state != ProcessState.PROCESSING:
                # Movimento
                process.x += self.direction_x * self.transport_speed
                process.y += self.direction_y * self.transport_speed
                
                # Verificar chegada
                if self._distance_to_end(process) <= self.transport_speed:
                    process.x, process.y = self.end_point
                    arrived_processes.append(process)
                    self.transit_processes.remove(process)
        
        # Processar chegadas
        for process in arrived_processes:
            if self.computer.is_idle:
                self.computer.start_processing(process)
            else:
                process.enter_cpu_queue()  # Set queue entry time
                self.cpu_queue.append(process)
    
    def _process_cpu_queue(self) -> None:
        """Processa a fila da CPU"""
        if self.computer.is_idle and self.cpu_queue:
            next_process = self.cpu_queue.pop(0)
            self.computer.start_processing(next_process)
    
    def _update_visual_positions(self) -> None:
        """Atualiza posições visuais das filas"""
        self._update_input_queue_positions()
        self._update_cpu_queue_positions()
    
    def _update_input_queue_positions(self) -> None:
        """Posiciona processos na fila de entrada"""
        for i, process in enumerate(self.input_queue):
            if process.state == ProcessState.IN_QUEUE:
                offset_x = -30 - (i * 25)
                offset_y = -20 + (i % 3) * 15
                process.x = self.start_point[0] + offset_x
                process.y = self.start_point[1] + offset_y
    
    def _update_cpu_queue_positions(self) -> None:
        """Posiciona processos na fila da CPU"""
        cpu_x, cpu_y = self.computer.get_center()
        for i, process in enumerate(self.cpu_queue):
            if process.state == ProcessState.WAITING_CPU:
                process.x = cpu_x - 60 - (i * 40)
                process.y = cpu_y
    
    def _distance_to_end(self, process: Process) -> float:
        """Calcula distância do processo até o final"""
        dx = self.end_point[0] - process.x
        dy = self.end_point[1] - process.y
        return (dx**2 + dy**2)**0.5
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha todo o sistema de conexão"""
        self._draw_connection_line(screen)
        self._draw_arrow(screen)
        self._draw_capacity_indicator(screen)
        self._draw_all_processes(screen)
    
    def _draw_connection_line(self, screen: pygame.Surface) -> None:
        """Desenha a linha de conexão principal"""
        pygame.draw.line(screen, Colors.WHITE, self.start_point, self.end_point, 4)
    
    def _draw_arrow(self, screen: pygame.Surface) -> None:
        """Desenha seta indicando direção"""
        arrow_size = 10
        mid_x = (self.start_point[0] + self.end_point[0]) / 2
        mid_y = (self.start_point[1] + self.end_point[1]) / 2
        
        tip = (mid_x + self.direction_x * arrow_size, 
               mid_y + self.direction_y * arrow_size)
        
        perp_x = -self.direction_y
        perp_y = self.direction_x
        
        left = (mid_x + perp_x * arrow_size/2, mid_y + perp_y * arrow_size/2)
        right = (mid_x - perp_x * arrow_size/2, mid_y - perp_y * arrow_size/2)
        
        pygame.draw.polygon(screen, Colors.WHITE, [tip, left, right])
    
    def _draw_capacity_indicator(self, screen: pygame.Surface) -> None:
        """Desenha indicador de capacidade"""
        font = pygame.font.SysFont(None, 20)
        capacity_text = font.render(f"Capacidade: {self.total_processes}/{self.max_capacity}", True, Colors.WHITE)
        screen.blit(capacity_text, (self.start_point[0] - 50, self.start_point[1] - 40))
        
        # Barra de progresso
        bar_width = 100
        bar_height = 8
        bar_x = self.start_point[0] - 50
        bar_y = self.start_point[1] - 25
        
        pygame.draw.rect(screen, Colors.DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        percentage = self.total_processes / self.max_capacity
        bar_color = (Colors.LIGHT_GREEN if percentage < 0.7 
                    else Colors.YELLOW if percentage < 0.9 
                    else Colors.RED)
        
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, bar_width * percentage, bar_height))
    
    def _draw_all_processes(self, screen: pygame.Surface) -> None:
        """Desenha todos os processos visíveis"""
        all_processes = (self.input_queue + self.transit_processes + 
                        self.cpu_queue)
        
        for process in all_processes:
            if process.state != ProcessState.PROCESSING:
                process.draw(screen)