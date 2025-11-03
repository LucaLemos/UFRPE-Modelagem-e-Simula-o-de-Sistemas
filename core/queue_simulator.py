import pygame
from typing import Dict, Any
from config import Colors, GridPositions, GENERATION_FREQUENCIES, FPS
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
        
        # Estado do simulador
        self.processes = []
        self.time_since_last_process = 0.0  # Now in seconds
        self.current_interval_seconds = 1.0  # Default: 1 second
        self.max_queue_time_seconds = 10.0  # Default: 10 seconds maximum queue time
        self.is_auto_generation_enabled = True  # Sempre ativo
        self.is_generator_blocked = False
        self.timed_out_processes = 0

        # Sistema de pontuação (NOVO)
        self.score = 0
    
    @property
    def generation_interval(self) -> int:
        self.timed_out_processes = 0  # Counter for timed out processes
        
        # Passar referências dos componentes para o InfoPanel
        self.info_panel.set_component_references(self.computer, self.generator, self)
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
        
        # Verifica se o campo de intervalo foi clicado (apenas para gerador)
        if (self.info_panel.selected_component == "generator" and 
            self.info_panel.is_interval_input_clicked(pos)):
            self.info_panel.activate_interval_input()
            return
        
        # Verifica se o campo de tempo de processamento foi clicado (apenas para computador)
        if (self.info_panel.selected_component == "computer" and 
            self.info_panel.is_processing_time_input_clicked(pos)):
            self.info_panel.activate_processing_time_input()
            return
        
        # Verifica se o campo de tempo máximo de fila foi clicado
        if (self.info_panel.selected_component == "computer" and 
            self.info_panel.is_max_queue_time_input_clicked(pos)):
            self.info_panel.activate_max_queue_time_input()
            return
        
        # Depois verifica os outros componentes
        if self.computer.is_clicked(pos):
            self.info_panel.select_component("computer")
            self.info_panel.deactivate_all_inputs()
            print("CPU clicada - mostrando informações da CPU")
        elif self.generator.is_clicked(pos):
            self.info_panel.select_component("generator")
            print("Gerador clicado - mostrando informações do gerador")
        else:
            # Se clicar em qualquer outro lugar, desativa todos os campos de entrada
            self.info_panel.deactivate_all_inputs()
    
    def handle_key_event(self, event):
        """Lida com eventos de teclado para entrada de texto"""
        # Handle generator interval input
        if (self.info_panel.selected_component == "generator" and 
            self.info_panel.is_interval_input_active):
            
            if event.key == pygame.K_RETURN:
                # Aplica o intervalo digitado
                new_interval = self.info_panel.get_interval_input_value()
                if new_interval > 0:
                    self.current_interval_seconds = new_interval
                    print(f"Intervalo alterado para: {new_interval:.2f} segundos")
                    self.time_since_last_process = 0.0  # Reset timer
                self.info_panel.deactivate_all_inputs()
            
            elif event.key == pygame.K_ESCAPE:
                # Cancela a edição
                self.info_panel.deactivate_all_inputs()
                # Restaura o valor atual
                self.info_panel.interval_input_text = f"{self.current_interval_seconds:.2f}"
            
            elif event.key == pygame.K_BACKSPACE:
                # Remove o último caractere
                self.info_panel.remove_character_from_interval_input()
            
            elif event.key == pygame.K_DELETE:
                # Limpa o campo
                self.info_panel.clear_interval_input()
            
            else:
                # Adiciona o caractere se for um dígito ou ponto decimal
                if event.unicode.isdigit() or event.unicode == '.':
                    self.info_panel.add_character_to_interval_input(event.unicode)
        
        # Handle computer processing time input
        elif (self.info_panel.selected_component == "computer" and 
              self.info_panel.is_processing_time_input_active):
            
            if event.key == pygame.K_RETURN:
                # Aplica o tempo de processamento digitado
                new_processing_time = self.info_panel.get_processing_time_input_value()
                if new_processing_time > 0:
                    self.computer.set_processing_time(new_processing_time)
                self.info_panel.deactivate_all_inputs()
            
            elif event.key == pygame.K_ESCAPE:
                # Cancela a edição
                self.info_panel.deactivate_all_inputs()
                # Restaura o valor atual
                self.info_panel.processing_time_input_text = f"{self.computer.processing_time_ms/1000:.2f}"
            
            elif event.key == pygame.K_BACKSPACE:
                # Remove o último caractere
                self.info_panel.remove_character_from_processing_time_input()
            
            elif event.key == pygame.K_DELETE:
                # Limpa o campo
                self.info_panel.clear_processing_time_input()
            
            else:
                # Adiciona o caractere se for um dígito ou ponto decimal
                if event.unicode.isdigit() or event.unicode == '.':
                    self.info_panel.add_character_to_processing_time_input(event.unicode)
        
        # Handle max queue time input
        elif (self.info_panel.selected_component == "computer" and 
              self.info_panel.is_max_queue_time_input_active):
            
            if event.key == pygame.K_RETURN:
                # Aplica o tempo máximo de fila digitado
                new_max_queue_time = self.info_panel.get_max_queue_time_input_value()
                if new_max_queue_time > 0:
                    self.max_queue_time_seconds = new_max_queue_time
                    print(f"Tempo máximo de fila alterado para: {new_max_queue_time:.2f} segundos")
                self.info_panel.deactivate_all_inputs()
            
            elif event.key == pygame.K_ESCAPE:
                # Cancela a edição
                self.info_panel.deactivate_all_inputs()
                # Restaura o valor atual
                self.info_panel.max_queue_time_input_text = f"{self.max_queue_time_seconds:.2f}"
            
            elif event.key == pygame.K_BACKSPACE:
                # Remove o último caractere
                self.info_panel.remove_character_from_max_queue_time_input()
            
            elif event.key == pygame.K_DELETE:
                # Limpa o campo
                self.info_panel.clear_max_queue_time_input()
            
            else:
                # Adiciona o caractere se for um dígito ou ponto decimal
                if event.unicode.isdigit() or event.unicode == '.':
                    self.info_panel.add_character_to_max_queue_time_input(event.unicode)
    
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
        
        # Verificar timeouts na fila da CPU
        self._check_queue_timeouts()
        
        # Atualizar InfoPanel com informações atualizadas
        self.info_panel.update_info(self.computer, self.connection, self.processes, self.current_interval_seconds, self.max_queue_time_seconds, self.timed_out_processes)
        
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
            # Convert frames to seconds (each frame is 1/FPS seconds)
            self.time_since_last_process += 1.0 / FPS
            
            if self.time_since_last_process >= self.current_interval_seconds:
                process = self.generator.create_process()
                if process:  # Só adiciona se o gerador não estiver parado
                    self.processes.append(process)
                    if self.connection.add_process(process):
                        print(f"Processo {process.id} criado automaticamente")
                    self.time_since_last_process = 0.0
    
    def _check_queue_timeouts(self):
        """Verifica processos na fila da CPU que excederam o tempo máximo de espera"""
        current_time = pygame.time.get_ticks()
        
        for process in self.connection.cpu_queue[:]:
            if process.state == ProcessState.WAITING_CPU:
                # Calculate time spent in queue
                time_in_queue = (current_time - process.queue_entry_time) / 1000.0  # Convert to seconds
                
                if time_in_queue >= self.max_queue_time_seconds:
                    print(f"Processo {process.id} excedeu o tempo máximo de fila ({time_in_queue:.2f}s) e foi removido")
                    self.connection.cpu_queue.remove(process)
                    process.is_active = False
                    process.state = ProcessState.COMPLETED
                    self.timed_out_processes += 1
    
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

        # Parâmetros do sistema
        process_generation_interval_seconds = self.current_interval_seconds
        lambda_rate = 1 / process_generation_interval_seconds  # taxa de chegada
        mu_rate = 1 / (self.computer.processing_time_ms / 1000)  # taxa de serviço (based on computer processing time)

        rho = lambda_rate / mu_rate  # Utilização do sistema
        
        if rho < 1:
            L = rho / (1 - rho)  # Número médio de clientes no sistema
            Lq = rho**2 / (1 - rho)  # Número médio de clientes na fila
            W = 1 / (mu_rate - lambda_rate)  # Tempo médio no sistema
            Wq = rho / (mu_rate - lambda_rate)  # Tempo médio na fila
            
            print(f"Taxa de chegada (lambda): {lambda_rate:.3f} processos/segundo")
            print(f"Taxa de serviço (mu): {mu_rate:.3f} processos/segundo")
            print(f"Utilização do sistema (rho): {rho:.3f}")
            print(f"Número médio de clientes no sistema (L): {L:.3f}")
            print(f"Número médio de clientes na fila (Lq): {Lq:.3f}")
            print(f"Tempo médio no sistema (W): {W:.3f} segundos")
            print(f"Tempo médio na fila (Wq): {Wq:.3f} segundos")
            print(f"Processos expirados na fila: {self.timed_out_processes}")
        else:
            print("Sistema instável: a taxa de chegada é maior ou igual à taxa de serviço.")
            print(f"Taxa de chegada (lambda): {lambda_rate:.3f} processos/segundo")
            print(f"Taxa de serviço (mu): {mu_rate:.3f} processos/segundo")
            print(f"Utilização do sistema (rho): {rho:.3f}")
            print(f"Processos expirados na fila: {self.timed_out_processes}")