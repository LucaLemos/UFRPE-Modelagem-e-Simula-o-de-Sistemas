import pygame
from typing import List, Optional
from config import Colors, MAX_CONNECTION_CAPACITY, TRANSPORT_SPEED
from entities.process import Process
from entities.process_states import ProcessState

class LoadBalancer:
    """Balanceador de carga para distribuir processos entre CPUs"""
    
    def __init__(self, computers):
        self.computers = computers
        self.current_index = 0
        self.distribution_strategy = "round_robin"  # "round_robin", "least_loaded"
    
    def set_strategy(self, strategy):
        """Define a estratégia de distribuição"""
        self.distribution_strategy = strategy
    
    def get_target_computer(self, process=None):
        """Retorna a CPU alvo para o processo"""
        # CORREÇÃO: Verificar se há CPUs disponíveis
        if not self.computers:
            return None
            
        if self.distribution_strategy == "round_robin":
            return self._round_robin()
        elif self.distribution_strategy == "least_loaded":
            return self._least_loaded()
        else:
            return self._round_robin()
    
    def _round_robin(self):
        """Distribuição round-robin entre CPUs"""
        # CORREÇÃO: Verificar se há CPUs disponíveis
        if not self.computers:
            return None
            
        computer = self.computers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.computers)
        return computer
    
    def _least_loaded(self):
        """Retorna a CPU com menor carga (fila + processamento)"""
        # CORREÇÃO: Verificar se há CPUs disponíveis
        if not self.computers:
            return None
            
        return min(self.computers, key=lambda cpu: 
                  cpu.queue_length + (0 if cpu.is_idle else 1))
    
    def get_system_load(self):
        """Retorna informações de carga do sistema"""
        load_info = {}
        for computer in self.computers:
            load_info[computer.name] = {
                'queue_length': computer.queue_length,
                'is_processing': not computer.is_idle,
                'is_stopped': computer.is_stopped
            }
        return load_info

class ConnectionSystem:
    def __init__(self, generator, computers):
        self.generator = generator
        self.computers = computers if isinstance(computers, list) else [computers]
        self.load_balancer = LoadBalancer(self.computers)
        
        # Filas do sistema
        self.input_queue: List[Process] = []      # Fila de entrada
        self.transit_processes: List[Process] = [] # Processos em trânsito
        
        self.transport_speed = TRANSPORT_SPEED
        self.max_capacity = MAX_CONNECTION_CAPACITY
        
        # Mapeamento de processos para CPUs alvo
        self.process_targets = {}  # process_id -> computer
        
        # Calcular direções para cada CPU
        self.computer_directions = {}
        self._calculate_all_directions()
    
    def _calculate_all_directions(self):
        """Calcula direções para todas as CPUs"""
        start_point = self.generator.get_center()
        
        for computer in self.computers:
            end_point = computer.get_center()
            dx = end_point[0] - start_point[0]
            dy = end_point[1] - start_point[1]
            length = (dx**2 + dy**2)**0.5
            
            if length > 0:
                self.computer_directions[computer] = {
                    'dx': dx / length,
                    'dy': dy / length,
                    'length': length,
                    'end_point': end_point
                }
            else:
                self.computer_directions[computer] = {
                    'dx': 0, 'dy': 0, 'length': 0, 'end_point': end_point
                }
    
    def add_process(self, process: Process) -> bool:
        """Adiciona um processo ao sistema se houver capacidade"""
        # CORREÇÃO: Verificar se há CPUs disponíveis antes de adicionar
        if not self.computers:
            return False
            
        if self.total_processes < self.max_capacity:
            # Escolhe a CPU alvo usando o balanceador de carga
            target_computer = self.load_balancer.get_target_computer(process)
            
            # CORREÇÃO: Verificar se encontrou uma CPU válida
            if target_computer is None:
                return False
                
            self.process_targets[process.id] = target_computer
            
            process.x, process.y = self.generator.get_center()
            process.state = ProcessState.IN_QUEUE
            self.input_queue.append(process)
            return True
        return False
    
    @property
    def total_processes(self) -> int:
        """Total de processos em todas as filas"""
        total = len(self.input_queue) + len(self.transit_processes)
        for computer in self.computers:
            total += len(computer.queue)
            if computer.current_process and computer.current_process.state == ProcessState.PROCESSING:
                total += 1
        return total
    
    @property
    def has_capacity(self) -> bool:
        """Verifica se há capacidade disponível"""
        # CORREÇÃO: Também verificar se há CPUs disponíveis
        return len(self.computers) > 0 and self.total_processes < self.max_capacity
    
    def update(self) -> None:
        """Atualiza todo o fluxo do sistema"""
        self._move_from_input_to_transit()
        self._update_transit_processes()
        self._process_cpu_queues()
        self._update_visual_positions()
    
    def _move_from_input_to_transit(self) -> None:
        """Move processos da fila de entrada para trânsito"""
        # CORREÇÃO: Verificar se há CPUs disponíveis
        if self.input_queue and len(self.transit_processes) < 8 and self.computers:
            process = self.input_queue.pop(0)
            process.state = ProcessState.IN_TRANSIT
            self.transit_processes.append(process)
    
    def _update_transit_processes(self) -> None:
        """Atualiza processos em trânsito"""
        arrived_processes = []
        
        for process in self.transit_processes[:]:
            if process.state != ProcessState.PROCESSING:
                # Obter CPU alvo e direção
                target_computer = self.process_targets.get(process.id)
                if not target_computer:
                    continue
                    
                direction_info = self.computer_directions.get(target_computer)
                if not direction_info:
                    continue
                
                # Movimento em direção à CPU alvo
                process.x += direction_info['dx'] * self.transport_speed
                process.y += direction_info['dy'] * self.transport_speed
                
                # Verificar chegada
                if self._distance_to_computer(process, target_computer) <= self.transport_speed:
                    process.x, process.y = direction_info['end_point']
                    arrived_processes.append((process, target_computer))
                    self.transit_processes.remove(process)
        
        # Processar chegadas
        for process, target_computer in arrived_processes:
            if target_computer.is_idle and not target_computer.is_stopped:
                target_computer.start_processing(process)
            else:
                target_computer.add_to_queue(process)
    
    def _process_cpu_queues(self) -> None:
        """Processa as filas de todas as CPUs"""
        for computer in self.computers:
            if computer.is_idle and not computer.is_stopped and computer.queue:
                next_process = computer.get_next_process()
                if next_process:
                    computer.start_processing(next_process)
    
    def _update_visual_positions(self) -> None:
        """Atualiza posições visuais das filas"""
        self._update_input_queue_positions()
        for computer in self.computers:
            computer.update_queue_positions()
    
    def _update_input_queue_positions(self) -> None:
        """Posiciona processos na fila de entrada"""
        for i, process in enumerate(self.input_queue):
            if process.state == ProcessState.IN_QUEUE:
                offset_x = -30 - (i * 25)
                offset_y = -20 + (i % 3) * 15
                process.x = self.generator.get_center()[0] + offset_x
                process.y = self.generator.get_center()[1] + offset_y
    
    def _distance_to_computer(self, process: Process, computer) -> float:
        """Calcula distância do processo até a CPU alvo"""
        end_point = self.computer_directions[computer]['end_point']
        dx = end_point[0] - process.x
        dy = end_point[1] - process.y
        return (dx**2 + dy**2)**0.5
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha todo o sistema de conexão"""
        self._draw_connection_lines(screen)
        self._draw_arrows(screen)
        self._draw_capacity_indicator(screen)
        self._draw_all_processes(screen)
    
    def _draw_connection_lines(self, screen: pygame.Surface) -> None:
        """Desenha as linhas de conexão para todas as CPUs"""
        start_point = self.generator.get_center()
        
        for computer in self.computers:
            end_point = computer.get_center()
            # Usar a cor da CPU para a linha de conexão
            line_color = computer.base_color
            pygame.draw.line(screen, line_color, start_point, end_point, 3)
    
    def _draw_arrows(self, screen: pygame.Surface) -> None:
        """Desenha setas indicando direção para cada CPU"""
        arrow_size = 8
        start_point = self.generator.get_center()
        
        for computer in self.computers:
            direction_info = self.computer_directions.get(computer)
            if not direction_info:
                continue
                
            # Ponto no meio do caminho
            mid_x = start_point[0] + direction_info['dx'] * direction_info['length'] * 0.5
            mid_y = start_point[1] + direction_info['dy'] * direction_info['length'] * 0.5
            
            tip = (mid_x + direction_info['dx'] * arrow_size, 
                   mid_y + direction_info['dy'] * arrow_size)
            
            perp_x = -direction_info['dy']
            perp_y = direction_info['dx']
            
            left = (mid_x + perp_x * arrow_size/2, mid_y + perp_y * arrow_size/2)
            right = (mid_x - perp_x * arrow_size/2, mid_y - perp_y * arrow_size/2)
            
            pygame.draw.polygon(screen, computer.base_color, [tip, left, right])
    
    def _draw_capacity_indicator(self, screen: pygame.Surface) -> None:
        """Desenha indicador de capacidade"""
        font = pygame.font.SysFont(None, 20)
        
        # CORREÇÃO: Mensagem diferente quando não há CPUs
        if not self.computers:
            capacity_text = font.render("SISTEMA SEM CPUS!", True, Colors.RED)
            screen.blit(capacity_text, (self.generator.get_center()[0] - 50, self.generator.get_center()[1] - 40))
            
            # Mostrar instrução para comprar CPUs
            instruction_text = font.render("Compre CPUs na loja!", True, Colors.YELLOW)
            screen.blit(instruction_text, (self.generator.get_center()[0] - 50, self.generator.get_center()[1] - 20))
            return
        
        capacity_text = font.render(f"Capacidade: {self.total_processes}/{self.max_capacity}", True, Colors.WHITE)
        screen.blit(capacity_text, (self.generator.get_center()[0] - 50, self.generator.get_center()[1] - 40))
        
        # Barra de progresso
        bar_width = 100
        bar_height = 8
        bar_x = self.generator.get_center()[0] - 50
        bar_y = self.generator.get_center()[1] - 25
        
        pygame.draw.rect(screen, Colors.DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        percentage = self.total_processes / self.max_capacity
        bar_color = (Colors.LIGHT_GREEN if percentage < 0.7 
                    else Colors.YELLOW if percentage < 0.9 
                    else Colors.RED)
        
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, bar_width * percentage, bar_height))
        
        # Informações de carga das CPUs
        load_info = self.load_balancer.get_system_load()
        load_y = bar_y + 15
        for computer_name, info in load_info.items():
            status = "PARADA" if info['is_stopped'] else "ATIVA"
            status_color = Colors.RED if info['is_stopped'] else Colors.GREEN
            load_text = font.render(f"{computer_name}: {info['queue_length']} na fila", True, Colors.WHITE)
            status_text = font.render(f"({status})", True, status_color)
            
            screen.blit(load_text, (bar_x, load_y))
            screen.blit(status_text, (bar_x + 120, load_y))
            load_y += 15
    
    def _draw_all_processes(self, screen: pygame.Surface) -> None:
        """Desenha todos os processos visíveis"""
        # Processos na fila de entrada e em trânsito
        for process in self.input_queue + self.transit_processes:
            if process.state != ProcessState.PROCESSING:
                process.draw(screen)
        
        # Processos nas filas das CPUs
        for computer in self.computers:
            for process in computer.queue:
                if process.state != ProcessState.PROCESSING:
                    process.draw(screen)