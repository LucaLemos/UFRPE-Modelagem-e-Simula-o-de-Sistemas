import pygame
import random
from typing import Dict, Any
from config import Colors, GridPositions, GENERATION_FREQUENCIES, FPS, CPU_COLORS, MAX_HEALTH_POINTS, SCREEN_WIDTH, SCREEN_HEIGHT
from entities.generator import ProcessGenerator
from entities.computer import Computer
from entities.infoPanel import InfoPanel
from entities.shopPanel import ShopPanel
from entities.process_states import ProcessState
from core.connection_system import ConnectionSystem
from utils.grid_helper import GridHelper

class QueueSimulator:
    def __init__(self):
        # Componentes do sistema - COMEÇA APENAS COM CPU 1
        self.generator = ProcessGenerator()
        
        # Criar apenas a CPU 1 inicialmente
        self.computers = [
            Computer(1, GridPositions.COMPUTER_1, CPU_COLORS[0])
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
        
        # Variável para controlar o modo de jogo
        self._game_mode = "sandbox"  # padrão: sandbox
        
        # Timer para modo jogo
        self.game_start_time = pygame.time.get_ticks()
        self.game_time_elapsed = 0.0
        self.last_event_time = 0.0  # Tempo do último evento
        self.event_messages = []  # Mensagens de eventos para display
        self.event_message_timer = 0.0  # Timer para mostrar mensagens
        
        # NOVO: Sistema de vida para modo jogo
        self.health_points = MAX_HEALTH_POINTS
        self.game_over = False
        
        # Passar referências dos componentes para o InfoPanel
        self.info_panel.set_component_references(self.computers, self.generator, self)
    
    def set_game_mode(self, mode):
        """Define o modo de operação (sandbox ou game)"""
        self._game_mode = mode
        print(f"Modo definido para: {mode}")
    
    def is_game_mode(self):
        """Verifica se está no modo jogo"""
        return self._game_mode == "game"
    
    def handle_click(self, pos):
        """Lida com cliques do mouse nos componentes"""
        # Se o jogo acabou, apenas permitir voltar ao menu
        if self.game_over:
            return
        
        # **CORREÇÃO: Primeiro verificar se o botão de fechar do InfoPanel foi clicado**
        # **ISSO DEVE FUNCIONAR EM AMBOS OS MODOS**
        if self.info_panel.is_close_button_clicked(pos):
            self.info_panel.close_detailed_view()
            print("Visualização detalhada fechada")
            return
        
        # Depois verificar se a loja foi clicada (permitido em ambos os modos)
        shop_item = self.shop_panel.is_clicked(pos)
        if shop_item:
            # Para upgrades infinitos, sempre permitir compra se tiver pontos suficientes
            # Para CPUs, verificar se não foi comprado
            if (shop_item["id"] in ["upgrade_processing_speed", "upgrade_capacity", "upgrade_speed"] or 
                not shop_item.get("purchased", False)):
                
                success, cost = self.shop_panel.purchase_item(shop_item["id"], self.score)
                if success:
                    self.score -= cost
                    self._apply_shop_purchase(shop_item["id"])
                    print(f"Item {shop_item['name']} comprado por {cost} pontos!")
            return
        
        # **NO MODO JOGO: Restringir controles avançados**
        if self.is_game_mode():
            # No modo jogo, apenas permitir visualização de informações
            # mas não permitir interação com controles
            computer_clicked = False
            for i, computer in enumerate(self.computers):
                if computer.is_clicked(pos):
                    self.info_panel.select_component(f"computer_{i+1}")
                    self.info_panel.deactivate_all_inputs()
                    print(f"CPU {i+1} clicada - modo visualização apenas")
                    computer_clicked = True
                    break
            
            if not computer_clicked and self.generator.is_clicked(pos):
                self.info_panel.select_component("generator")
                print("Gerador clicado - modo visualização apenas")
            elif not computer_clicked:
                self.info_panel.deactivate_all_inputs()
            return
        
        # **MODO SANDBOX: Controles completos**
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
        # Se o jogo acabou, ignorar todas as entradas
        if self.game_over:
            return
            
        # **NO MODO JOGO: Ignorar todas as entradas de teclado para controles**
        if self.is_game_mode():
            return
        
        # **MODO SANDBOX: Controles completos de teclado**
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
        # **NO MODO JOGO: Este método não deve ser chamado**
        if self.is_game_mode():
            return
        
        # **MODO SANDBOX: Controles completos**
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
        # **NO MODO JOGO: Atualizar hover apenas para elementos visíveis**
        if self.is_game_mode():
            # No modo jogo, apenas atualizar hover do botão de fechar se estiver visível
            if self.info_panel.selected_component is not None:
                self.info_panel.update_button_hover(pos)
            return
        
        # **MODO SANDBOX: Atualizar todos os hovers**
        self.info_panel.update_button_hover(pos)
    
    def update(self) -> None:
        """Atualiza o estado do simulador"""
        # Se o jogo acabou, não atualizar mais nada
        if self.game_over:
            return
            
        # Geração automática
        self._handle_auto_generation()
        
        # Atualizar bloqueio do gerador
        self.is_generator_blocked = not self.connection.has_capacity
        
        # Atualizar sistema de conexão
        self.connection.update()
        
        # Verificar timeouts em todas as filas de CPU
        self._check_queue_timeouts()
        
        # Atualizar timer no modo jogo
        if self.is_game_mode():
            self.game_time_elapsed = (pygame.time.get_ticks() - self.game_start_time) / 1000.0
            
            # Verificar se é hora de um evento aleatório (a cada 10 segundos)
            if self.game_time_elapsed - self.last_event_time >= 10.0:
                self._trigger_random_event()
                self.last_event_time = self.game_time_elapsed
        
        # Atualizar timer das mensagens de evento
        if self.event_messages:
            self.event_message_timer += 1.0 / FPS
            if self.event_message_timer >= 5.0:  # Mostrar mensagem por 5 segundos
                self.event_messages.pop(0)
                self.event_message_timer = 0.0
        
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

    def _trigger_random_event(self):
        """Dispara um evento aleatório no modo jogo"""
        if not self.is_game_mode():
            return
        
        # Probabilidades dos eventos
        event_roll = random.random()
        
        if event_roll < 0.5:  # 50% de chance - Aumento de carga
            self._trigger_increased_load_event()
        elif event_roll < 0.8:  # 30% de chance - Perda de upgrade
            self._trigger_upgrade_loss_event()
        else:  # 20% de chance - Quebra de CPU
            self._trigger_cpu_break_event()
    
    def _trigger_increased_load_event(self):
        """Evento: Aumento da carga (diminui intervalo de geração)"""
        # Reduzir o intervalo em 10-30%
        reduction = random.uniform(0.1, 0.3)
        new_interval = max(0.3, self.current_interval_seconds * (1 - reduction))
        old_interval = self.current_interval_seconds
        self.current_interval_seconds = new_interval
        
        # Mensagem de debuff
        reduction_percent = int(reduction * 100)
        message = f"CARGA AUMENTADA! -{reduction_percent}% intervalo"
        self.event_messages.append((message, Colors.ORANGE))
        print(f"[EVENTO] {message}")
    
    def _trigger_upgrade_loss_event(self):
        """Evento: Perda de um upgrade comprado"""
        # Verificar quais upgrades estão disponíveis para remover
        available_upgrades = []
        upgrade_items = ["upgrade_processing_speed", "upgrade_capacity", "upgrade_speed"]
        
        for item_id in upgrade_items:
            level = self.shop_panel.get_upgrade_level(item_id)
            if level > 1:  # Só pode remover se tiver pelo menos nível 2
                available_upgrades.append(item_id)
        
        if available_upgrades:
            # Escolher um upgrade aleatório para remover
            upgrade_to_remove = random.choice(available_upgrades)
            current_level = self.shop_panel.get_upgrade_level(upgrade_to_remove)
            
            # Reduzir o nível do upgrade
            for item in self.shop_panel.shop_items:
                if item["id"] == upgrade_to_remove:
                    item["upgrade_level"] = max(1, current_level - 1)
                    # Recalcular preço baseado no novo nível
                    new_price = self.shop_panel._calculate_upgrade_price(
                        item["base_price"], item["upgrade_level"], item["price_increase"]
                    )
                    item["price"] = new_price
                    
                    # Aplicar as consequências da perda do upgrade
                    self._apply_upgrade_loss(upgrade_to_remove, current_level - 1)
                    
                    upgrade_names = {
                        "upgrade_processing_speed": "Veloc. Processamento",
                        "upgrade_capacity": "Capacidade Sistema", 
                        "upgrade_speed": "Veloc. Transporte"
                    }
                    
                    # Mensagem de debuff
                    message = f"UPGRADE PERDIDO! {upgrade_names[upgrade_to_remove]} Nv.{current_level}→{current_level-1}"
                    self.event_messages.append((message, Colors.YELLOW))
                    print(f"[EVENTO] {message}")
                    break
        else:
            # Se não há upgrades para remover, disparar outro evento
            self._trigger_increased_load_event()
    
    def _trigger_cpu_break_event(self):
        """Evento: Quebra de uma CPU comprada"""
        # Verificar quais CPUs estão disponíveis para quebrar (excluindo a CPU 1 inicial)
        available_cpus = [cpu for cpu in self.computers if cpu.computer_id > 1]

        if available_cpus:
            # Escolher uma CPU aleatória para quebrar
            cpu_to_break = random.choice(available_cpus)
            cpu_id = cpu_to_break.computer_id

            # Remover a CPU do sistema
            self.computers.remove(cpu_to_break)

            # CORREÇÃO: Atualizar o connection system com a nova lista
            self.connection.update_computers_list(self.computers)

            # Marcar como não comprada na loja
            for item in self.shop_panel.shop_items:
                if item["id"] == f"cpu_{cpu_id}":
                    item["purchased"] = False
                    break
                
            # Mensagem de debuff
            message = f"CPU {cpu_id} QUEBROU! Perdeu processamento"
            self.event_messages.append((message, Colors.RED))
            print(f"[EVENTO] {message}")
        else:
            # Se não há CPUs para quebrar, disparar aumento de carga
            self._trigger_increased_load_event()
    
    def _apply_upgrade_loss(self, upgrade_id, new_level):
        """Aplica as consequências da perda de um upgrade"""
        if upgrade_id == "upgrade_speed":
            # Reverter velocidade de transporte
            self.connection.transport_speed = 3.0 * (1.25 ** (new_level - 1))
        elif upgrade_id == "upgrade_capacity":
            # Reverter capacidade
            self.connection.max_capacity = 15 + (8 * (new_level - 1))
        elif upgrade_id == "upgrade_processing_speed":
            # Reverter velocidade de processamento
            reduction_factor = 0.85 ** (new_level - 1)
            base_processing_time = 2000
            new_processing_time = base_processing_time * reduction_factor
            
            for computer in self.computers:
                computer.processing_time_ms = max(300, new_processing_time)

    def _apply_shop_purchase(self, item_id):
        """Aplica os efeitos da compra na loja"""
        if item_id == "cpu_2":
            self._add_new_computer(2, Colors.CYAN, GridPositions.COMPUTER_2)
        elif item_id == "cpu_3":
            self._add_new_computer(3, Colors.PINK, GridPositions.COMPUTER_3)
        elif item_id == "cpu_4":
            self._add_new_computer(4, Colors.GREEN, GridPositions.COMPUTER_4)
        elif item_id == "cpu_5":
            self._add_new_computer(5, Colors.YELLOW, GridPositions.COMPUTER_5)
        elif item_id == "cpu_6":
            self._add_new_computer(6, Colors.PURPLE, GridPositions.COMPUTER_6)
        elif item_id == "upgrade_speed":
            # Aumento gradual da velocidade de transporte
            speed_level = self.shop_panel.get_upgrade_level("upgrade_speed")
            # Cada nível aumenta a velocidade em 25%
            self.connection.transport_speed = 3.0 * (1.25 ** (speed_level - 1))
            print(f"Velocidade de transporte aumentada para nível {speed_level}! ({self.connection.transport_speed:.1f}x)")
        elif item_id == "upgrade_capacity":
            # Aumento gradual da capacidade
            capacity_level = self.shop_panel.get_upgrade_level("upgrade_capacity")
            # Cada nível aumenta a capacidade em 8
            self.connection.max_capacity = 15 + (8 * (capacity_level - 1))
            print(f"Capacidade do sistema aumentada para nível {capacity_level}! ({self.connection.max_capacity})")
        elif item_id == "upgrade_processing_speed":
            # Aplicar redução no tempo de processing de todas as CPUs
            processing_speed_level = self.shop_panel.get_processing_speed_level()
            # Cada nível reduz o tempo em 15% (mínimo de 0.3 segundos)
            reduction_factor = 0.85 ** (processing_speed_level - 1)
            
            for computer in self.computers:
                # Reduzir o tempo base (2000ms) pelo fator de redução
                base_processing_time = 2000  # 2 segundos base
                new_processing_time = base_processing_time * reduction_factor
                computer.processing_time_ms = max(300, new_processing_time)  # Mínimo de 0.3 segundos
            
            print(f"Velocidade de processamento aumentada para nível {processing_speed_level}!")
            print(f"Tempo de processamento reduzido para {reduction_factor*100:.1f}% do original")
    
    def _add_new_computer(self, computer_id, color, grid_position):
        """Adiciona uma nova CPU ao sistema"""
        new_computer = Computer(computer_id, grid_position, color)
        self.computers.append(new_computer)

        # CORREÇÃO: Atualizar o connection system com a nova lista
        self.connection.update_computers_list(self.computers)

        # Atualizar referências no info panel
        self.info_panel.set_component_references(self.computers, self.generator, self)

        print(f"Nova CPU {computer_id} adicionada ao sistema!")

    def _add_score(self):
        """Adiciona pontos quando um processo é completado com sucesso"""
        self.score += 1
        print(f"[SUCESSO] Processo completado! Pontuacao: {self.score}")

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
                        
                        # NOVO: Remover ponto de vida no modo jogo
                        if self.is_game_mode() and not self.game_over:
                            self._remove_health_point()
    
    def _remove_health_point(self):
        """Remove um ponto de vida no modo jogo"""
        if self.health_points > 0:
            self.health_points -= 1
            print(f"💔 Perdeu 1 ponto de vida! Vida restante: {self.health_points}/{MAX_HEALTH_POINTS}")
            
            # Verificar se o jogo acabou
            if self.health_points <= 0:
                self._end_game()
    
    def _end_game(self):
        """Finaliza o jogo quando a vida chega a zero"""
        self.game_over = True
        print("🎮 FIM DE JOGO! Sua pontuação final foi:", self.score)
        
        # Parar todos os componentes
        self.generator.stop()
        for computer in self.computers:
            computer.stop()
        
        # Mensagem de fim de jogo
        game_over_message = f"FIM DE JOGO! Pontuação: {self.score}"
        self.event_messages.append((game_over_message, Colors.RED))
    
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
        
        # **ATUALIZAÇÃO: Passar informação do modo para o InfoPanel**
        if hasattr(self.info_panel, '_simulator_ref'):
            self.info_panel._simulator_ref = self
        
        self.info_panel.draw(screen)
        
        # Shop Panel (novo)
        self.shop_panel.draw(screen, self.score)

        # Processos sendo processados (dentro das CPUs)
        for computer in self.computers:
            self._draw_processing_process(screen, computer)

        self._draw_score_display(screen)
        
        # Desenhar timer no modo jogo
        if self.is_game_mode():
            self._draw_timer_display(screen)
            self._draw_event_messages(screen)
            self._draw_health_bar(screen)  # NOVO: Desenhar barra de vida
        
        # Desenhar tela de game over se aplicável
        if self.game_over:
            self._draw_game_over_screen(screen)
    
    def _draw_health_bar(self, screen: pygame.Surface) -> None:
        """Desenha a barra de vida no grid 6,0 até 8,0"""
        health_x, health_y, health_width, health_height = GridHelper.grid_to_pixels(
            GridPositions.HEALTH_BAR[0], 
            GridPositions.HEALTH_BAR[1], 
            3, 1  # 3 células de largura, 1 de altura
        )
        
        # Fundo da barra de vida
        pygame.draw.rect(screen, Colors.DARK_GRAY, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, Colors.WHITE, (health_x, health_y, health_width, health_height), 2)
        
        # Calcular largura da vida atual
        health_percentage = self.health_points / MAX_HEALTH_POINTS
        current_health_width = int((health_width - 4) * health_percentage)
        
        # Determinar cor baseada na vida restante
        if health_percentage > 0.6:
            health_color = Colors.GREEN
        elif health_percentage > 0.3:
            health_color = Colors.YELLOW
        else:
            health_color = Colors.RED
        
        # Desenhar barra de vida atual
        if current_health_width > 0:
            pygame.draw.rect(screen, health_color, 
                           (health_x + 2, health_y + 2, current_health_width, health_height - 4))
        
        # Texto da barra de vida
        font = pygame.font.SysFont(None, 24)
        health_text = font.render(f"VIDA: {self.health_points}/{MAX_HEALTH_POINTS}", True, Colors.WHITE)
        screen.blit(health_text, (health_x + health_width//2 - health_text.get_width()//2, 
                                health_y + health_height//2 - health_text.get_height()//2))
    
    def _draw_game_over_screen(self, screen: pygame.Surface) -> None:
        """Desenha a tela de fim de jogo"""
        # Criar uma superfície semi-transparente para o fundo
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Preto semi-transparente
        screen.blit(overlay, (0, 0))
        
        # Texto de Game Over
        font_large = pygame.font.SysFont(None, 72)
        font_medium = pygame.font.SysFont(None, 36)
        font_small = pygame.font.SysFont(None, 24)
        
        game_over_text = font_large.render("FIM DE JOGO", True, Colors.RED)
        time_text = font_medium.render(f"Tempo: {int(self.game_time_elapsed)} segundos", True, Colors.WHITE)
        
        # Centralizar textos
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, SCREEN_HEIGHT//2))
    
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
        title_text = font_small.render("PONTUACAO", True, Colors.WHITE)
        screen.blit(title_text, (score_x + score_width//2 - title_text.get_width()//2, score_y + 10))
        
        # Valor da pontuação
        score_text = font_large.render(str(self.score), True, Colors.GREEN)
        screen.blit(score_text, (score_x + score_width//2 - score_text.get_width()//2, score_y + 30))
        
        # **ADICIONADO: Indicador de modo atual**
        mode_text = font_small.render(f"Modo: {self._game_mode.upper()}", True, 
                                    Colors.YELLOW if self.is_game_mode() else Colors.CYAN)
        screen.blit(mode_text, (score_x + score_width//2 - mode_text.get_width()//2, score_y + 55))
    
    def _draw_timer_display(self, screen: pygame.Surface) -> None:
        """Desenha o timer no grid (1,0) - APENAS NO MODO JOGO"""
        timer_x, timer_y, timer_width, timer_height = GridHelper.grid_to_pixels(
            GridPositions.TIMER_DISPLAY[0], 
            GridPositions.TIMER_DISPLAY[1], 
            1, 1
        )
        
        # Fundo mais escuro para melhor contraste
        pygame.draw.rect(screen, (40, 40, 50), (timer_x, timer_y, timer_width, timer_height), border_radius=6)
        pygame.draw.rect(screen, Colors.CYAN, (timer_x, timer_y, timer_width, timer_height), 2, border_radius=6)
        
        # Texto do timer
        font_large = pygame.font.SysFont("Arial", 28, bold=True)
        font_small = pygame.font.SysFont("Arial", 16)
        
        # Título
        title_text = font_small.render("TEMPO", True, Colors.WHITE)
        screen.blit(title_text, (timer_x + timer_width//2 - title_text.get_width()//2, timer_y + 10))
        
        # Valor do tempo (formato MM:SS)
        minutes = int(self.game_time_elapsed) // 60
        seconds = int(self.game_time_elapsed) % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        
        time_display = font_large.render(time_text, True, Colors.CYAN)
        screen.blit(time_display, (timer_x + timer_width//2 - time_display.get_width()//2, timer_y + 30))
        
        # Indicador de próximo evento
        if not self.event_messages:
            next_event = 10 - (int(self.game_time_elapsed) % 10)
            event_text = font_small.render(f"Próx: {next_event}s", True, Colors.ORANGE)
            screen.blit(event_text, (timer_x + timer_width//2 - event_text.get_width()//2, timer_y + 55))
        else:
            # Mostrar "EVENTO!" quando há mensagem ativa
            event_text = font_small.render("EVENTO!", True, Colors.RED)
            screen.blit(event_text, (timer_x + timer_width//2 - event_text.get_width()//2, timer_y + 55))
    
    def _draw_event_messages(self, screen: pygame.Surface) -> None:
        """Desenha mensagens de eventos nos grids (2,0) até (4,0)"""
        if not self.event_messages:
            return
        
        # Mostrar apenas a mensagem mais recente
        message, color = self.event_messages[0]
        
        # Usar grids (2,0) até (4,0) - 3 células de largura, 1 de altura (fixa)
        message_x, message_y, message_width, message_height = GridHelper.grid_to_pixels(
            GridPositions.EVENT_DISPLAY[0],  # Grid 2,0
            GridPositions.EVENT_DISPLAY[1],  # Linha 0
            3, 1  # 3 células de largura, 1 de altura FIXA
        )
        
        # Fonte para mensagens
        font = pygame.font.SysFont("Arial", 20, bold=True)
        
        # **ALTURA FIXA** - Não ajustar baseado no conteúdo
        total_height = message_height
        
        # Fundo semi-transparente com borda colorida
        bg_rect = pygame.Rect(message_x, message_y, message_width, total_height)
        s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        s.fill((30, 30, 40, 230))  # Azul escuro semi-transparente
        screen.blit(s, bg_rect)
        
        # Borda colorida ao redor
        pygame.draw.rect(screen, color, bg_rect, 3, border_radius=8)
        
        # **SEM ÍCONES** - Apenas texto centralizado
        text_surface = font.render(message, True, color)
        text_x = message_x + (message_width - text_surface.get_width()) // 2
        text_y = message_y + (total_height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def _draw_processing_process(self, screen: pygame.Surface, computer: Computer) -> None:
        """Desenha o processo atualmente em processamento na CPU"""
        # CORREÇÃO: Usar computer.is_idle em vez de computer.is_processing
        if (computer.current_process and 
            computer.current_process.state == ProcessState.PROCESSING and 
            not computer.is_stopped and not computer.is_idle):
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
        print(f"Numero de CPUs ativas: {c}")
        print(f"Taxa de chegada (lambda): {lambda_rate:.3f} processos/segundo")
        print(f"Taxa de servico media (mu): {mu_rate:.3f} processos/segundo")
        print(f"Utilizacao do sistema (rho): {rho:.3f}")
        
        # Informações individuais de cada CPU
        for i, computer in enumerate(self.computers):
            status = "ATIVA" if not computer.is_stopped else "PARADA"
            print(f"CPU {i+1}: {status}, Fila: {len(computer.queue)}, Tempo processamento: {computer.processing_time_ms/1000:.2f}s")
        
        print(f"Processos expirados na fila: {self.timed_out_processes}")
        print(f"Pontuacao: {self.score}")
        
        if rho < 1:
            # Cálculos simplificados para M/M/c
            print("Sistema estavel")
        else:
            print("Sistema instavel: a taxa de chegada e maior que a capacidade total de servico")