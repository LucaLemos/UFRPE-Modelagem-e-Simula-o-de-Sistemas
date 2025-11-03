import pygame
from typing import Dict, Any
from config import Colors, GridPositions, GENERATION_FREQUENCIES, FPS, CPU_COLORS
from entities.generator import ProcessGenerator
from entities.computer import Computer
from entities.infoPanel import InfoPanel
from entities.shopPanel import ShopPanel
from entities.process_states import ProcessState
from core.connection_system import ConnectionSystem
from utils.grid_helper import GridHelper

class QueueSimulator:
    def __init__(self):
        # Componentes do sistema com múltiplas CPUs
        self.generator = ProcessGenerator()
        
        # Criar múltiplas CPUs com cores diferentes
        self.computers = [
            Computer(1, GridPositions.COMPUTER_1, CPU_COLORS[0]),
            Computer(2, GridPositions.COMPUTER_2, CPU_COLORS[1]),
            Computer(3, GridPositions.COMPUTER_3, CPU_COLORS[2])
        ]
        
        # Adicionar ShopPanel
        self.shop_panel = ShopPanel()
        self.info_panel = InfoPanel()
        self.connection = ConnectionSystem(self.generator, self.computers)
        
        # Estado do simulador
        self.processes = []
        self.time_since_last_process = 0.0
        self.current_interval_seconds = 1.0
        self.max_queue_time_seconds = 10.0
        self.is_auto_generation_enabled = True
        self.is_generator_blocked = False
        self.timed_out_processes = 0

        # Sistema de pontuação
        self.score = 0
        
        # Passar referências dos componentes para o InfoPanel
        self.info_panel.set_component_references(self.computers, self.generator, self)
    
    def handle_click(self, pos):
        """Lida com cliques do mouse nos componentes"""
        # Primeiro verificar se a loja foi clicada
        shop_item = self.shop_panel.is_clicked(pos)
        if shop_item and not shop_item["purchased"]:
            success, cost = self.shop_panel.purchase_item(shop_item["id"], self.score)
            if success:
                self.score -= cost
                self._apply_shop_purchase(shop_item["id"])
                print(f"Item {shop_item['name']} comprado por {cost} pontos!")
            return
        
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
        
        # Verifica se o campo de tempo de processamento foi clicado (apenas para computador específico)
        if self.info_panel.selected_component and self.info_panel.selected_component.startswith("computer_"):
            if self.info_panel.is_processing_time_input_clicked(pos):
                self.info_panel.activate_processing_time_input()
                return
            elif self.info_panel.is_max_queue_time_input_clicked(pos):
                self.info_panel.activate_max_queue_time_input()
                return
        
        # Verifica se alguma CPU foi clicada
        computer_clicked = False
        for i, computer in enumerate(self.computers):
            if computer.is_clicked(pos):
                self.info_panel.select_component(f"computer_{i+1}")
                self.info_panel.deactivate_all_inputs()
                print(f"CPU {i+1} clicada - mostrando informações")
                computer_clicked = True
                break
        
        # Verifica se o gerador foi clicado
        if not computer_clicked and self.generator.is_clicked(pos):
            self.info_panel.select_component("generator")
            print("Gerador clicado - mostrando informações do gerador")
        elif not computer_clicked:
            # Se clicar em qualquer outro lugar, desativa todos os campos de entrada
            self.info_panel.deactivate_all_inputs()
    
    def handle_key_event(self, event):
        """Lida com eventos de teclado para entrada de texto"""
        # Handle generator interval input
        if (self.info_panel.selected_component == "generator" and 
            self.info_panel.is_interval_input_active):
            
            if event.key == pygame.K_RETURN:
                new_interval = self.info_panel.get_interval_input_value()
                if new_interval > 0:
                    self.current_interval_seconds = new_interval
                    print(f"Intervalo alterado para: {new_interval:.2f} segundos")
                    self.time_since_last_process = 0.0
                self.info_panel.deactivate_all_inputs()
            
            elif event.key == pygame.K_ESCAPE:
                self.info_panel.deactivate_all_inputs()
                self.info_panel.interval_input_text = f"{self.current_interval_seconds:.2f}"
            
            elif event.key == pygame.K_BACKSPACE:
                self.info_panel.remove_character_from_interval_input()
            
            elif event.key == pygame.K_DELETE:
                self.info_panel.clear_interval_input()
            
            else:
                if event.unicode.isdigit() or event.unicode == '.':
                    self.info_panel.add_character_to_interval_input(event.unicode)
        
        # Handle computer processing time input
        elif (self.info_panel.selected_component and 
              self.info_panel.selected_component.startswith("computer_") and 
              self.info_panel.is_processing_time_input_active):
            
            computer_index = int(self.info_panel.selected_component.split('_')[1]) - 1
            computer = self.computers[computer_index]
            
            if event.key == pygame.K_RETURN:
                new_processing_time = self.info_panel.get_processing_time_input_value()
                if new_processing_time > 0:
                    computer.set_processing_time(new_processing_time)
                self.info_panel.deactivate_all_inputs()
            
            elif event.key == pygame.K_ESCAPE:
                self.info_panel.deactivate_all_inputs()
                self.info_panel.processing_time_input_text = f"{computer.processing_time_ms/1000:.2f}"
            
            elif event.key == pygame.K_BACKSPACE:
                self.info_panel.remove_character_from_processing_time_input()
            
            elif event.key == pygame.K_DELETE:
                self.info_panel.clear_processing_time_input()
            
            else:
                if event.unicode.isdigit() or event.unicode == '.':
                    self.info_panel.add_character_to_processing_time_input(event.unicode)
        
        # Handle max queue time input
        elif (self.info_panel.selected_component and 
              self.info_panel.selected_component.startswith("computer_") and 
              self.info_panel.is_max_queue_time_input_active):
            
            if event.key == pygame.K_RETURN:
                new_max_queue_time = self.info_panel.get_max_queue_time_input_value()
                if new_max_queue_time > 0:
                    self.max_queue_time_seconds = new_max_queue_time
                    print(f"Tempo máximo de fila alterado para: {new_max_queue_time:.2f} segundos")
                self.info_panel.deactivate_all_inputs()
            
            elif event.key == pygame.K_ESCAPE:
                self.info_panel.deactivate_all_inputs()
                self.info_panel.max_queue_time_input_text = f"{self.max_queue_time_seconds:.2f}"
            
            elif event.key == pygame.K_BACKSPACE:
                self.info_panel.remove_character_from_max_queue_time_input()
            
            elif event.key == pygame.K_DELETE:
                self.info_panel.clear_max_queue_time_input()
            
            else:
                if event.unicode.isdigit() or event.unicode == '.':
                    self.info_panel.add_character_to_max_queue_time_input(event.unicode)
    
    def _handle_stop_button_click(self):
        """Lida com o clique no botão de parar/iniciar"""
        selected_component = self.info_panel.selected_component
        
        if selected_component == "generator":
            self.generator.toggle_stop()
            action = "parado" if self.generator.is_stopped else "retomado"
            print(f"Gerador {action}")
        
        elif selected_component and selected_component.startswith("computer_"):
            computer_index = int(selected_component.split('_')[1]) - 1
            computer = self.computers[computer_index]
            computer.toggle_stop()
            action = "parada" if computer.is_stopped else "retomada"
            print(f"CPU {computer_index + 1} {action}")
    
    def handle_mouse_motion(self, pos):
        """Lida com movimento do mouse para efeitos visuais"""
        self.info_panel.update_button_hover(pos)
    
    def update(self) -> None:
        """Atualiza o estado do simulador"""
        # Geração automática
        self._handle_auto_generation()
        
        # Atualizar bloqueio do gerador
        self.is_generator_blocked = not self.connection.has_capacity
        
        # Atualizar sistema de conexão
        self.connection.update()
        
        # Verificar timeouts em todas as filas de CPU
        self._check_queue_timeouts()
        
        # Atualizar InfoPanel com informações atualizadas
        self.info_panel.update_info(self.computers, self.connection, self.processes, 
                                  self.current_interval_seconds, self.max_queue_time_seconds, 
                                  self.timed_out_processes)
        
        # Verificar conclusão de processamento em todas as CPUs
        for computer in self.computers:
            if not computer.is_idle and not computer.is_stopped:
                if computer.check_processing_complete():
                    print(f"CPU {computer.computer_id} liberada - processo finalizado")
                    self._add_score()
                    self.show_metrics()
        
        # Limpar processos finalizados
        self._cleanup_completed_processes()

    def _apply_shop_purchase(self, item_id):
        """Aplica os efeitos da compra na loja"""
        if item_id == "cpu_4":
            self._add_new_computer(4, Colors.GREEN, GridPositions.COMPUTER_4)
        elif item_id == "cpu_5":
            self._add_new_computer(5, Colors.YELLOW, GridPositions.COMPUTER_5)
        elif item_id == "cpu_6":
            self._add_new_computer(6, Colors.PURPLE, GridPositions.COMPUTER_6)
        elif item_id == "upgrade_speed":
            self.connection.transport_speed *= 1.5
            print("Velocidade de transporte aumentada!")
        elif item_id == "upgrade_capacity":
            self.connection.max_capacity += 10
            print("Capacidade do sistema aumentada!")
    
    def _add_new_computer(self, computer_id, color, grid_position):
        """Adiciona uma nova CPU ao sistema"""
        new_computer = Computer(computer_id, grid_position, color)
        self.computers.append(new_computer)
        
        # Atualizar o connection system com a nova CPU
        self.connection.computers = self.computers
        self.connection.load_balancer.computers = self.computers
        self.connection._calculate_all_directions()
        
        # Atualizar referências no info panel
        self.info_panel.set_component_references(self.computers, self.generator, self)
        
        print(f"Nova CPU {computer_id} adicionada ao sistema!")

    def _add_score(self):
        """Adiciona pontos quando um processo é completado com sucesso"""
        self.score += 1
        print(f"[SUCESSO] Processo completado! Pontuacao: {self.score}")  # Changed emoji to text
    
    def _handle_auto_generation(self) -> None:
        """Gerencia a geração automática de processos"""
        if self.connection.has_capacity and not self.generator.is_stopped:
            self.time_since_last_process += 1.0 / FPS
            
            if self.time_since_last_process >= self.current_interval_seconds:
                process = self.generator.create_process()
                if process:
                    self.processes.append(process)
                    if self.connection.add_process(process):
                        target_computer = self.connection.process_targets[process.id]
                        print(f"Processo {process.id} criado automaticamente -> {target_computer.name}")
                    self.time_since_last_process = 0.0
    
    def _check_queue_timeouts(self):
        """Verifica processos em todas as filas de CPU que excederam o tempo máximo"""
        current_time = pygame.time.get_ticks()
        
        for computer in self.computers:
            for process in computer.queue[:]:
                if process.state == ProcessState.WAITING_CPU:
                    time_in_queue = (current_time - process.queue_entry_time) / 1000.0
                    
                    if time_in_queue >= self.max_queue_time_seconds:
                        print(f"Processo {process.id} excedeu o tempo máximo de fila ({time_in_queue:.2f}s) e foi removido de {computer.name}")
                        computer.queue.remove(process)
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
        
        # Sistema de conexão (desenha linhas e processos)
        self.connection.draw(screen)
        
        # Componentes principais
        self.generator.draw(screen)
        for computer in self.computers:
            computer.draw(screen)
        self.info_panel.draw(screen)
        
        # Shop Panel (novo)
        self.shop_panel.draw(screen, self.score)

        # Processos sendo processados (dentro das CPUs)
        for computer in self.computers:
            self._draw_processing_process(screen, computer)

        self._draw_score_display(screen)
    
    def _draw_score_display(self, screen: pygame.Surface) -> None:
        """Desenha a pontuação no grid (0,0)"""
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
        title_text = font_small.render("PONTUACAO", True, Colors.WHITE)  # Removed accent
        screen.blit(title_text, (score_x + score_width//2 - title_text.get_width()//2, score_y + 10))
        
        # Valor da pontuação
        score_text = font_large.render(str(self.score), True, Colors.GREEN)
        screen.blit(score_text, (score_x + score_width//2 - score_text.get_width()//2, score_y + 30))
    
    def _draw_processing_process(self, screen: pygame.Surface, computer: Computer) -> None:
        """Desenha o processo atualmente em processamento na CPU"""
        if (computer.current_process and 
            computer.current_process.state == ProcessState.PROCESSING and 
            not computer.is_stopped):
            process = computer.current_process
            cpu_x, cpu_y = computer.get_center()
            process.x, process.y = cpu_x, cpu_y
            process.draw(screen)

    def show_metrics(self):
        """Calcula e exibe métricas do sistema de filas M/M/c"""
        # Parâmetros do sistema
        process_generation_interval_seconds = self.current_interval_seconds
        lambda_rate = 1 / process_generation_interval_seconds  # taxa de chegada
        
        # Calcular taxa de serviço média entre todas as CPUs ativas
        active_cpus = [cpu for cpu in self.computers if not cpu.is_stopped]
        if not active_cpus:
            print("Nenhuma CPU ativa no sistema")
            return
            
        avg_processing_time = sum(cpu.processing_time_ms for cpu in active_cpus) / len(active_cpus)
        mu_rate = 1 / (avg_processing_time / 1000)  # taxa de serviço média
        
        c = len(active_cpus)  # número de servidores
        rho = lambda_rate / (c * mu_rate)  # utilização do sistema
        
        print(f"=== SISTEMA M/M/{c} ===")
        print(f"Numero de CPUs ativas: {c}")  # Removed accent
        print(f"Taxa de chegada (lambda): {lambda_rate:.3f} processos/segundo")
        print(f"Taxa de servico media (mu): {mu_rate:.3f} processos/segundo")  # Removed accent
        print(f"Utilizacao do sistema (rho): {rho:.3f}")  # Removed accent
        
        # Informações individuais de cada CPU
        for i, computer in enumerate(self.computers):
            status = "ATIVA" if not computer.is_stopped else "PARADA"
            print(f"CPU {i+1}: {status}, Fila: {len(computer.queue)}, Tempo processamento: {computer.processing_time_ms/1000:.2f}s")
        
        print(f"Processos expirados na fila: {self.timed_out_processes}")
        print(f"Pontuacao: {self.score}")  # Removed accent
        
        if rho < 1:
            # Cálculos simplificados para M/M/c
            print("Sistema estavel")  # Removed accent
        else:
            print("Sistema instavel: a taxa de chegada e maior que a capacidade total de servico")  # Removed accents