import pygame
from typing import Dict, Any
from config import Colors, GENERATION_FREQUENCIES
from entities.generator import ProcessGenerator
from entities.computer import Computer
from entities.process_states import ProcessState
from core.connection_system import ConnectionSystem
from utils.grid_helper import GridHelper

class QueueSimulator:
    def __init__(self):
        # Componentes do sistema
        self.generator = ProcessGenerator()
        self.computer = Computer()
        self.connection = ConnectionSystem(self.generator, self.computer)
        
        # Estado do simulador
        self.processes = []
        self.time_since_last_process = 0
        self.current_frequency_index = 2  # Frequência padrão: Normal
        self.is_auto_generation_enabled = True  # Sempre ativo
        self.is_generator_blocked = False
    
    @property
    def generation_interval(self) -> int:
        return GENERATION_FREQUENCIES[self.current_frequency_index]["value"]
    
    def update(self) -> None:
        """Atualiza o estado do simulador"""
        # Geração automática (sempre ativa)
        self._handle_auto_generation()
        
        # Atualizar bloqueio do gerador
        self.is_generator_blocked = not self.connection.has_capacity
        
        # Atualizar sistema de conexão (controla todo o fluxo)
        self.connection.update()
        
        # Verificar conclusão de processamento
        if not self.computer.is_idle:
            if self.computer.check_processing_complete():
                print("CPU liberada - processo finalizado")
                self.show_metrics()
        
        # Limpar processos finalizados
        self._cleanup_completed_processes()

    
    def _handle_auto_generation(self) -> None:
        """Gerencia a geração automática de processos"""
        if self.connection.has_capacity:
            self.time_since_last_process += 1
            if self.time_since_last_process >= self.generation_interval:
                process = self.generator.create_process()
                self.processes.append(process)
                if self.connection.add_process(process):
                    print(f"Processo {process.id} criado automaticamente")
                self.time_since_last_process = 0
    
    def _cleanup_completed_processes(self) -> None:
        """Remove processos finalizados do sistema"""
        for process in self.processes[:]:
            if not process.is_active and process.state != ProcessState.PROCESSING:
                self.processes.remove(process)
                print(f"Processo {process.id} removido do sistema")
    
    def draw(self, screen: pygame.Surface) -> None:
        """Desenha todo o simulador"""
        # Fundo
        screen.fill(Colors.BLACK)
        
        # Grid (para debug)
        GridHelper.draw_grid(screen)
        
        # Sistema de conexão (desenha linha e processos)
        self.connection.draw(screen)
        
        # Componentes principais
        self.generator.draw(screen)
        self.computer.draw(screen)
        
        # Processo sendo processado (dentro da CPU)
        self._draw_processing_process(screen)
    
    def _draw_processing_process(self, screen: pygame.Surface) -> None:
        """Desenha o processo atualmente em processamento na CPU"""
        if self.computer.current_process and self.computer.current_process.state == ProcessState.PROCESSING:
            process = self.computer.current_process
            cpu_x, cpu_y = self.computer.get_center()
            process.x, process.y = cpu_x, cpu_y
            process.draw(screen)


    def show_metrics(self):
        """Calcula e exibe métricas do sistema de filas M/M/1"""

        # Parâmetros do sistema (ainda falta poder configurar dinamicamente)
        process_generation_interval = GENERATION_FREQUENCIES[self.current_frequency_index]["value"]  # em segundos
        _lambda = 1 / (process_generation_interval/60)  # taxa de chegada
        mu = 1 / 2  # taxa de serviço

        rho = _lambda / mu  # Utilização do sistema
        L = rho / (1 - rho)  # Número médio de clientes no sistema
        Lq = rho**2 / (1 - rho)  # Número médio de clientes na fila
        W = 1 / (mu - _lambda)  # Tempo médio no sistema
        Wq = rho / (mu - _lambda)  # Tempo médio na fila

        if rho >= 1:
            print("Sistema instável: a taxa de chegada é maior ou igual à taxa de serviço.")
        else:
            print(f"Taxa de chegada (λ): {_lambda:.3f} processos/unidade de tempo")
            print(f"Taxa de serviço (μ): {mu:.3f} processos/unidade de tempo")
            print(f"Utilização do sistema (ρ): {rho:.3f}")
            print(f"Número médio de clientes no sistema (L): {L:.3f}")
            print(f"Número médio de clientes na fila (Lq): {Lq:.3f}")
            print(f"Tempo médio no sistema (W): {W:.3f} unidades de tempo")
            print(f"Tempo médio na fila (Wq): {Wq:.3f} unidades de tempo")
