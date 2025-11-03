import pygame
from typing import Dict, Any
from config import Colors, GridPositions, GENERATION_FREQUENCIES
from entities.generator import ProcessGenerator
from entities.computer import Computer
from entities.infoPanel import InfoPanel
from entities.process_states import ProcessState
from core.connection_system import ConnectionSystem
from utils.grid_helper import GridHelper

class QueueSimulator:
    def __init__(self):
        # Componentes do sistema
        self.generator = ProcessGenerator()
        self.computer = Computer()
        self.info_panel = InfoPanel()
        self.connection = ConnectionSystem(self.generator, self.computer)
        
        # Passar referências dos componentes para o InfoPanel
        self.info_panel.set_component_references(self.computer, self.generator)
        
        # Estado do simulador
        self.processes = []
        self.time_since_last_process = 0
        self.current_frequency_index = 2  # Frequência padrão: Normal
        self.is_auto_generation_enabled = True  # Sempre ativo
        self.is_generator_blocked = False

        # Sistema de pontuação (NOVO)
        self.score = 0
    
    @property
    def generation_interval(self) -> int:
        return GENERATION_FREQUENCIES[self.current_frequency_index]["value"]
    
    def handle_click(self, pos):
        """Lida com cliques do mouse nos componentes"""
        # Primeiro verifica se o botão de fechar foi clicado
        if self.info_panel.is_close_button_clicked(pos):
            self.info_panel.close_detailed_view()
            print("Visualização detalhada fechada")
            return
        
        # Verifica se o botão de parar/iniciar foi clicado
        if self.info_panel.is_stop_button_clicked(pos):
            self._handle_stop_button_click()
            return
        
        # Depois verifica os outros componentes
        if self.computer.is_clicked(pos):
            self.info_panel.select_component("computer")
            print("CPU clicada - mostrando informações da CPU")
        elif self.generator.is_clicked(pos):
            self.info_panel.select_component("generator")
            print("Gerador clicado - mostrando informações do gerador")
        else:
            # Se clicar em qualquer outro lugar, não muda a seleção atual
            pass
    
    def _handle_stop_button_click(self):
        """Lida com o clique no botão de parar/iniciar"""
        selected_component = self.info_panel.selected_component
        
        if selected_component == "computer":
            self.computer.toggle_stop()
            action = "parada" if self.computer.is_stopped else "retomada"
            print(f"CPU {action}")
        elif selected_component == "generator":
            self.generator.toggle_stop()
            action = "parado" if self.generator.is_stopped else "retomado"
            print(f"Gerador {action}")
    
    def handle_mouse_motion(self, pos):
        """Lida com movimento do mouse para efeitos visuais"""
        # Atualiza o estado de hover dos botões
        self.info_panel.update_button_hover(pos)
    
    def update(self) -> None:
        """Atualiza o estado do simulador"""
        # Geração automática (sempre ativa, a menos que o gerador esteja parado)
        self._handle_auto_generation()
        
        # Atualizar bloqueio do gerador
        self.is_generator_blocked = not self.connection.has_capacity
        
        # Atualizar sistema de conexão (controla todo o fluxo)
        self.connection.update()
        
        # Atualizar InfoPanel com informações atualizadas
        self.info_panel.update_info(self.computer, self.connection, self.processes)
        
        # Verificar conclusão de processamento (a menos que a CPU esteja parada)
        if not self.computer.is_idle and not self.computer.is_stopped:
            if self.computer.check_processing_complete():
                print("CPU liberada - processo finalizado")
                self._add_score()
                self.show_metrics()
        
        # Limpar processos finalizados
        self._cleanup_completed_processes()

    def _add_score(self):
        """Adiciona pontos quando um processo é completado com sucesso"""
        self.score += 1
        print(f"✅ Processo completado! Pontuação: {self.score}")
    
    def _handle_auto_generation(self) -> None:
        """Gerencia a geração automática de processos"""
        if self.connection.has_capacity and not self.generator.is_stopped:
            self.time_since_last_process += 1
            if self.time_since_last_process >= self.generation_interval:
                process = self.generator.create_process()
                if process:  # Só adiciona se o gerador não estiver parado
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
        self.info_panel.draw(screen)  # Desenha o InfoPanel
        
        # Processo sendo processado (dentro da CPU)
        self._draw_processing_process(screen)

        self._draw_score_display(screen)
    
    def _draw_score_display(self, screen: pygame.Surface) -> None:
        """Desenha a pontuação no grid (0,0)"""
        # Criar um retângulo para o display de pontuação
        score_x, score_y, score_width, score_height = GridHelper.grid_to_pixels(
            GridPositions.SCORE_DISPLAY[0], 
            GridPositions.SCORE_DISPLAY[1], 
            1, 1
)
        
        # Fundo do display
        pygame.draw.rect(screen, Colors.DARK_GRAY, (score_x, score_y, score_width, score_height))
        pygame.draw.rect(screen, Colors.WHITE, (score_x, score_y, score_width, score_height), 2)
        
        # Texto da pontuação
        font_large = pygame.font.SysFont(None, 34)
        font_small = pygame.font.SysFont(None, 18)
        
        # Título
        title_text = font_small.render("PONTUAÇÃO", True, Colors.WHITE)
        screen.blit(title_text, (score_x + score_width//2 - title_text.get_width()//2, score_y + 10))
        
        # Valor da pontuação
        score_text = font_large.render(str(self.score), True, Colors.GREEN)
        screen.blit(score_text, (score_x + score_width//2 - score_text.get_width()//2, score_y + 30))

    def _draw_processing_process(self, screen: pygame.Surface) -> None:
        """Desenha o processo atualmente em processamento na CPU"""
        if self.computer.current_process and self.computer.current_process.state == ProcessState.PROCESSING and not self.computer.is_stopped:
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