import pygame
from config import Colors, GridPositions, ElementSizes
from utils.grid_helper import GridHelper

class InfoPanel:
    def __init__(self):
        col, row = GridPositions.INFO_PANEL
        width_cells, height_cells = ElementSizes.INFO_PANEL

        self.x, self.y, self.width, self.height = GridHelper.grid_to_pixels(
            col, row, width_cells, height_cells
        )

        self.info_lines = []
        self.middle_info_lines = []
        self.selected_component = None
        
        # Modern color scheme
        self.background_color = (30, 30, 40)  # Dark blue-gray
        self.accent_color = (70, 130, 180)    # Steel blue
        self.secondary_color = (50, 60, 80)   # Darker blue-gray
        self.text_color = (220, 220, 220)     # Light gray
        self.highlight_color = (100, 180, 255) # Bright blue
        self.success_color = (80, 200, 120)   # Green for success
        self.warning_color = (255, 180, 80)   # Orange for warnings
        self.error_color = (220, 80, 80)      # Red for errors
        
        # Title bar properties
        self.title_bar_height = 40
        self.title_bar_rect = pygame.Rect(
            self.x, self.y, self.width, self.title_bar_height
        )
        
        # Close button properties
        self.close_button_size = 20
        self.close_button_rect = pygame.Rect(
            self.x + self.width - 30, 
            self.y + 10, 
            self.close_button_size, 
            self.close_button_size
        )
        self.close_button_color = (220, 80, 80)
        self.close_button_hover_color = (255, 100, 100)
        self.is_close_button_hovered = False

        # Input fields properties
        self.input_width = 120
        self.input_height = 28
        
        # Interval input properties (for generator)
        self.interval_input_rect = pygame.Rect(0, 0, self.input_width, self.input_height)
        self.interval_input_text = "1.0"
        self.is_interval_input_active = False
        self.interval_input_color = self.secondary_color
        self.interval_input_active_color = (60, 80, 100)

        # Processing time input properties (for computers)
        self.processing_time_input_rect = pygame.Rect(0, 0, self.input_width, self.input_height)
        self.processing_time_input_text = "2.0"
        self.is_processing_time_input_active = False
        self.processing_time_input_color = self.secondary_color
        self.processing_time_input_active_color = (60, 80, 100)

        # Max queue time input properties
        self.max_queue_time_input_rect = pygame.Rect(0, 0, self.input_width, self.input_height)
        self.max_queue_time_input_text = "10.0"
        self.is_max_queue_time_input_active = False
        self.max_queue_time_input_color = self.secondary_color
        self.max_queue_time_input_active_color = (60, 80, 100)

        # Stop/Start button properties
        self.stop_button_width = 100
        self.stop_button_height = 30
        self.stop_button_rect = pygame.Rect(0, 0, self.stop_button_width, self.stop_button_height)
        self.stop_button_color = (220, 80, 80)
        self.stop_button_start_color = (80, 180, 80)
        self.stop_button_hover_color = (255, 100, 100)
        self.stop_button_start_hover_color = (100, 220, 100)
        self.is_stop_button_hovered = False

        # Content area
        self.content_rect = pygame.Rect(
            self.x,
            self.y + self.title_bar_height,
            self.width,
            self.height - self.title_bar_height - 60
        )

        # Column widths
        self.column_width = self.width // 3
        self.column_padding = 10

    def update_info(self, computers, connection, processes, current_interval_seconds=None, max_queue_time_seconds=None, timed_out_processes=0):
        """Atualiza as informações exibidas no painel"""
        if self.selected_component and self.selected_component.startswith("computer_"):
            computer_index = int(self.selected_component.split('_')[1]) - 1
            if computer_index < len(computers):
                self._show_computer_info(computers[computer_index], connection, max_queue_time_seconds, timed_out_processes)
        elif self.selected_component == "generator":
            self._show_generator_info(connection, computers, current_interval_seconds)
        else:
            self._show_general_info(computers, connection, processes, current_interval_seconds, max_queue_time_seconds, timed_out_processes)

    def _show_general_info(self, computers, connection, processes, current_interval_seconds, max_queue_time_seconds, timed_out_processes):
        """Mostra informações gerais do sistema multi-CPU"""
        active_cpus = sum(1 for cpu in computers if not cpu.is_stopped)
        total_queue = sum(len(cpu.queue) for cpu in computers)
        processing_cpus = sum(1 for cpu in computers if not cpu.is_idle and not cpu.is_stopped)
        concluidos = sum(1 for p in processes if not p.is_active)
        
        # Calculate system efficiency
        total_capacity = connection.max_capacity
        current_usage = connection.total_processes
        usage_percentage = (current_usage / total_capacity) * 100 if total_capacity > 0 else 0
        
        # Calculate average queue length
        avg_queue_length = total_queue / len(computers) if computers else 0
        
        # Calculate system load
        system_load = (processing_cpus / len(computers)) * 100 if computers else 0

        # Calculate success rate safely
        total_ended = concluidos + timed_out_processes
        if total_ended > 0:
            success_rate = (concluidos / total_ended) * 100
            success_rate_text = f"Taxa de Sucesso: {success_rate:.1f}%"
            success_rate_color = (self.success_color if success_rate > 90 
                                else self.warning_color if success_rate > 70 
                                else self.error_color)
        else:
            success_rate_text = "Taxa de Sucesso: 0.0%"
            success_rate_color = self.text_color

        # Calculate efficiency safely
        total_created = connection.generator.next_process_id - 1
        if total_created > 0:
            efficiency = (concluidos / total_created) * 100
            efficiency_text = f"Eficiencia: {efficiency:.1f}%"
            efficiency_color = (self.success_color if efficiency > 80 
                              else self.warning_color)
        else:
            efficiency_text = "Eficiencia: 0.0%"
            efficiency_color = self.text_color

        # Left column - Main system info
        self.info_lines = [
            ("=== SISTEMA MULTI-CPU ===", self.accent_color),
            (f"CPUs Ativas: {active_cpus}/{len(computers)}", self.text_color),
            (f"CPUs Processando: {processing_cpus}", self.text_color),
            (f"Gerador: {'PARADO' if getattr(connection.generator, 'is_stopped', False) else 'ATIVO'}", 
             self.error_color if getattr(connection.generator, 'is_stopped', False) else self.success_color),
            (f"Intervalo: {current_interval_seconds:.2f}s", self.text_color),
            (f"Tempo max. fila: {max_queue_time_seconds:.2f}s", self.text_color),
            (f"Total em filas: {total_queue}", self.text_color),
            (f"Concluidos: {concluidos}", self.success_color),
            (f"Expirados: {timed_out_processes}", self.error_color),
            (f"Capacidade: {connection.total_processes}/{connection.max_capacity}", self.text_color)
        ]
        
        # Middle column - Statistics and performance
        self.middle_info_lines = [
            ("=== ESTATISTICAS ===", self.accent_color),
            (f"Uso do Sistema: {usage_percentage:.1f}%", 
             self.error_color if usage_percentage > 90 else self.warning_color if usage_percentage > 70 else self.success_color),
            (f"Carga: {system_load:.1f}%", 
             self.success_color if system_load > 70 else self.warning_color if system_load > 30 else self.text_color),
            (f"Fila Media: {avg_queue_length:.1f}", 
             self.error_color if avg_queue_length > 5 else self.warning_color if avg_queue_length > 2 else self.success_color),
            ("", self.text_color),
            ("=== DESEMPENHO ===", self.accent_color),
            (success_rate_text, success_rate_color),
            (f"Processos/s: {1/current_interval_seconds:.2f}" if current_interval_seconds > 0 else "Processos/s: 0.00", self.text_color),
            (efficiency_text, efficiency_color),
            ("", self.text_color),
            ("=== BALANCEAMENTO ===", self.accent_color),
            (f"Estrategia: {connection.load_balancer.distribution_strategy}", self.highlight_color),
            (f"Criados: {connection.generator.next_process_id - 1}", self.text_color),
            (f"Transito: {len(connection.transit_processes)}", self.text_color)
        ]

    def _show_computer_info(self, computer, connection, max_queue_time_seconds, timed_out_processes):
        """Mostra informações detalhadas de uma CPU específica"""
        status = "PROCESSANDO" if not computer.is_idle else "OCIOSO"
        processo_atual = f"P{computer.current_process.id}" if computer.current_process else "Nenhum"
        is_stopped = getattr(computer, 'is_stopped', False)
        stopped_status = " (PARADA)" if is_stopped else ""
        
        # Calculate computer efficiency
        queue_warning = len(computer.queue) > 3
        processing_efficiency = "ALTA" if computer.processing_time_ms <= 2000 else "MEDIA" if computer.processing_time_ms <= 4000 else "BAIXA"
        
        # Left column - Computer info
        self.info_lines = [
            (f"=== {computer.name} ===", self.accent_color),
            (f"Status: {status}{stopped_status}", 
             self.error_color if is_stopped else self.warning_color if not computer.is_idle else self.success_color),
            (f"Processo atual: {processo_atual}", self.text_color),
            (f"Fila: {len(computer.queue)} processos", 
             self.error_color if queue_warning else self.warning_color if len(computer.queue) > 0 else self.success_color),
            (f"Tempo: {computer.processing_time_ms/1000:.2f}s", self.text_color),
            (f"Eficiencia: {processing_efficiency}", 
             self.success_color if processing_efficiency == "ALTA" else self.warning_color if processing_efficiency == "MEDIA" else self.error_color),
            (f"Tempo max.: {max_queue_time_seconds:.2f}s", self.text_color),
            (f"Expirados: {timed_out_processes}", self.error_color)
        ]
        
        # Middle column - Analysis and history
        self.middle_info_lines = [
            ("=== ANALISE ===", self.accent_color),
            (f"Estado: {'OTIMO' if computer.is_idle and not is_stopped else 'CRITICO' if is_stopped else 'TRABALHANDO'}", 
             self.success_color if computer.is_idle and not is_stopped else self.error_color if is_stopped else self.warning_color),
            (f"Capacidade: {'ALTA' if len(computer.queue) > 5 else 'MEDIA' if len(computer.queue) > 2 else 'BAIXA'}", 
             self.error_color if len(computer.queue) > 5 else self.warning_color if len(computer.queue) > 2 else self.success_color),
            (f"Velocidade: {'RAPIDO' if computer.processing_time_ms <= 1500 else 'NORMAL' if computer.processing_time_ms <= 3000 else 'LENTO'}", 
             self.success_color if computer.processing_time_ms <= 1500 else self.warning_color if computer.processing_time_ms <= 3000 else self.error_color),
            ("", self.text_color),
            ("=== HISTORICO ===", self.accent_color),
            (f"Atendidos: {computer.computer_id * 10}", self.text_color),
            (f"Uptime: {(pygame.time.get_ticks() / 1000 / 60):.1f} min", self.text_color),
            (f"Reinicios: 0", self.text_color)
        ]

    def _show_generator_info(self, connection, computers, current_interval_seconds):
        """Mostra informações detalhadas do gerador"""
        is_stopped = getattr(connection.generator, 'is_stopped', False)
        stopped_status = " (PARADO)" if is_stopped else ""
        total_queue = sum(len(cpu.queue) for cpu in computers)
        
        # Calculate generation metrics
        generation_rate = 1 / current_interval_seconds if current_interval_seconds > 0 else 0
        system_load = connection.total_processes / connection.max_capacity if connection.max_capacity > 0 else 0
        
        # Calculate efficiency safely
        total_created = connection.generator.next_process_id - 1
        if total_created > 0:
            efficiency = (total_created / max(1, pygame.time.get_ticks()/1000)) * 60
            efficiency_text = f"Eficiencia: {efficiency:.1f}/min"
        else:
            efficiency_text = "Eficiencia: 0.0/min"

        # Left column - Generator info
        self.info_lines = [
            ("=== GERADOR ===", self.accent_color),
            (f"Status: {'PARADO' if is_stopped else 'ATIVO'}{stopped_status}", 
             self.error_color if is_stopped else self.success_color),
            (f"Intervalo: {current_interval_seconds:.2f}s", self.text_color),
            (f"Taxa: {generation_rate:.2f}/s", self.text_color),
            (f"Criados: {connection.generator.next_process_id - 1}", self.text_color),
            (f"Fila entrada: {len(connection.input_queue)}", self.text_color),
            (f"Transito: {len(connection.transit_processes)}", self.text_color),
            (f"Total filas: {total_queue}", self.text_color),
            (f"Estrategia: {connection.load_balancer.distribution_strategy}", self.highlight_color)
        ]
        
        # Middle column - Analysis and statistics
        self.middle_info_lines = [
            ("=== ANALISE ===", self.accent_color),
            (f"Carga: {system_load*100:.1f}%", 
             self.error_color if system_load > 0.9 else self.warning_color if system_load > 0.7 else self.success_color),
            (f"Taxa Ideal: {'ALTA' if generation_rate > 2 else 'MEDIA' if generation_rate > 0.5 else 'BAIXA'}", 
             self.success_color if generation_rate > 1 else self.warning_color if generation_rate > 0.3 else self.error_color),
            (f"Distribuicao: {connection.load_balancer.distribution_strategy}", self.highlight_color),
            ("", self.text_color),
            ("=== ESTATISTICAS ===", self.accent_color),
            (f"Operacao: {(pygame.time.get_ticks() / 1000 / 60):.1f} min", self.text_color),
            (f"Picos: {int(system_load * 10)}", self.text_color),
            (efficiency_text, self.text_color)
        ]

    def _get_color_name(self, color):
        """Retorna o nome da cor baseado na tupla RGB"""
        color_names = {
            (255, 0, 0): "Vermelho",
            (0, 255, 255): "Ciano", 
            (255, 192, 203): "Rosa",
            (255, 165, 0): "Laranja",
            (0, 255, 0): "Verde",
            (255, 255, 0): "Amarelo",
            (128, 0, 128): "Roxo"
        }
        return color_names.get(color, "Desconhecida")

    def _get_status_color(self, computer):
        """Retorna a cor baseada no status da CPU"""
        if computer.is_stopped:
            return self.error_color  # Red for stopped
        elif not computer.is_idle:
            return self.warning_color  # Orange for processing
        else:
            return self.success_color  # Green for idle

    def select_component(self, component_type):
        """Seleciona qual componente mostrar informações"""
        self.selected_component = component_type
        # Atualizar textos de input baseado no componente selecionado
        self._update_input_texts()

    def _update_input_texts(self):
        """Atualiza os textos dos campos de input baseado no componente selecionado"""
        if hasattr(self, '_simulator_ref') and self._simulator_ref:
            if self.selected_component == "generator":
                self.interval_input_text = f"{self._simulator_ref.current_interval_seconds:.2f}"
            elif (self.selected_component and 
                  self.selected_component.startswith("computer_") and
                  hasattr(self, '_computers_ref')):
                computer_index = int(self.selected_component.split('_')[1]) - 1
                if computer_index < len(self._computers_ref):
                    computer = self._computers_ref[computer_index]
                    self.processing_time_input_text = f"{computer.processing_time_ms/1000:.2f}"
                    self.max_queue_time_input_text = f"{self._simulator_ref.max_queue_time_seconds:.2f}"

    def close_detailed_view(self):
        """Fecha a visualização detalhada e retorna à visão geral"""
        self.selected_component = None

    def is_close_button_clicked(self, pos):
        """Verifica se o botão de fechar foi clicado"""
        return self.close_button_rect.collidepoint(pos)

    def is_stop_button_clicked(self, pos):
        """Verifica se o botão de parar/iniciar foi clicado"""
        return self.stop_button_rect.collidepoint(pos)

    def is_interval_input_clicked(self, pos):
        """Verifica se o campo de entrada de intervalo foi clicado"""
        return self.interval_input_rect.collidepoint(pos)

    def is_processing_time_input_clicked(self, pos):
        """Verifica se o campo de entrada de tempo de processamento foi clicado"""
        return self.processing_time_input_rect.collidepoint(pos)

    def is_max_queue_time_input_clicked(self, pos):
        """Verifica se o campo de entrada de tempo máximo de fila foi clicado"""
        return self.max_queue_time_input_rect.collidepoint(pos)

    def activate_interval_input(self):
        """Ativa o campo de entrada de intervalo"""
        self.is_interval_input_active = True
        self.is_processing_time_input_active = False
        self.is_max_queue_time_input_active = False

    def activate_processing_time_input(self):
        """Ativa o campo de entrada de tempo de processamento"""
        self.is_processing_time_input_active = True
        self.is_interval_input_active = False
        self.is_max_queue_time_input_active = False

    def activate_max_queue_time_input(self):
        """Ativa o campo de entrada de tempo máximo de fila"""
        self.is_max_queue_time_input_active = True
        self.is_interval_input_active = False
        self.is_processing_time_input_active = False

    def deactivate_all_inputs(self):
        """Desativa todos os campos de entrada"""
        self.is_interval_input_active = False
        self.is_processing_time_input_active = False
        self.is_max_queue_time_input_active = False

    def add_character_to_interval_input(self, char):
        """Adiciona um caractere ao campo de entrada de intervalo"""
        if char.isdigit() or char == '.':
            if char == '.' and '.' in self.interval_input_text:
                return
            self.interval_input_text += char

    def add_character_to_processing_time_input(self, char):
        """Adiciona um caractere ao campo de entrada de tempo de processamento"""
        if char.isdigit() or char == '.':
            if char == '.' and '.' in self.processing_time_input_text:
                return
            self.processing_time_input_text += char

    def add_character_to_max_queue_time_input(self, char):
        """Adiciona um caractere ao campo de entrada de tempo máximo de fila"""
        if char.isdigit() or char == '.':
            if char == '.' and '.' in self.max_queue_time_input_text:
                return
            self.max_queue_time_input_text += char

    def remove_character_from_interval_input(self):
        """Remove o último caractere do campo de entrada de intervalo"""
        if len(self.interval_input_text) > 0:
            self.interval_input_text = self.interval_input_text[:-1]

    def remove_character_from_processing_time_input(self):
        """Remove o último caractere do campo de entrada de tempo de processamento"""
        if len(self.processing_time_input_text) > 0:
            self.processing_time_input_text = self.processing_time_input_text[:-1]

    def remove_character_from_max_queue_time_input(self):
        """Remove o último caractere do campo de entrada de tempo máximo de fila"""
        if len(self.max_queue_time_input_text) > 0:
            self.max_queue_time_input_text = self.max_queue_time_input_text[:-1]

    def clear_interval_input(self):
        """Limpa o campo de entrada de intervalo"""
        self.interval_input_text = ""

    def clear_processing_time_input(self):
        """Limpa o campo de entrada de tempo de processamento"""
        self.processing_time_input_text = ""

    def clear_max_queue_time_input(self):
        """Limpa o campo de entrada de tempo máximo de fila"""
        self.max_queue_time_input_text = ""

    def get_interval_input_value(self):
        """Obtém o valor do campo de entrada de intervalo como float (seconds)"""
        try:
            return float(self.interval_input_text) if self.interval_input_text else 1.0
        except ValueError:
            return 1.0

    def get_processing_time_input_value(self):
        """Obtém o valor do campo de entrada de tempo de processamento como float (seconds)"""
        try:
            return float(self.processing_time_input_text) if self.processing_time_input_text else 2.0
        except ValueError:
            return 2.0

    def get_max_queue_time_input_value(self):
        """Obtém o valor do campo de entrada de tempo máximo de fila como float (seconds)"""
        try:
            return float(self.max_queue_time_input_text) if self.max_queue_time_input_text else 10.0
        except ValueError:
            return 10.0

    def update_button_hover(self, pos):
        """Atualiza o estado de hover dos botões"""
        self.is_close_button_hovered = self.close_button_rect.collidepoint(pos)
        self.is_stop_button_hovered = self.stop_button_rect.collidepoint(pos)

    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o painel na tela com design moderno"""
        # Fundo principal com sombra
        pygame.draw.rect(screen, self.background_color, (self.x, self.y, self.width, self.height), border_radius=8)
        pygame.draw.rect(screen, self.accent_color, (self.x, self.y, self.width, self.height), 2, border_radius=8)
        
        # Barra de título
        pygame.draw.rect(screen, self.secondary_color, self.title_bar_rect, border_radius=8)
        pygame.draw.rect(screen, self.accent_color, (self.x, self.y, self.width, self.title_bar_height), 2, border_radius=8)

        # Fonte
        font = pygame.font.SysFont("Arial", 16)  # Slightly smaller font to fit more content
        title_font = pygame.font.SysFont("Arial", 20, bold=True)
        small_font = pygame.font.SysFont("Arial", 14)

        # Título baseado no componente selecionado
        title = {
            "computer_1": "INFORMACOES DA CPU 1",
            "computer_2": "INFORMACOES DA CPU 2", 
            "computer_3": "INFORMACOES DA CPU 3",
            "generator": "INFORMACOES DO GERADOR",
            None: "PAINEL DE INFORMACOES"
        }.get(self.selected_component, "PAINEL DE INFORMACOES")
        
        title_text = title_font.render(title, True, self.text_color)
        screen.blit(title_text, (self.x + self.width // 2 - title_text.get_width() // 2, self.y + 12))

        # Linhas de informação
        line_height = 18  # Slightly reduced line height
        start_y = self.y + self.title_bar_height + 15
        
        # Calculate column positions
        left_column_x = self.x + 15
        middle_column_x = self.x + self.column_width + 10
        right_column_x = self.x + 2 * self.column_width + 15
        
        # Draw left column (main info)
        for i, (line, color) in enumerate(self.info_lines):
            text = font.render(line, True, color)
            # Check if text fits in the panel
            if start_y + i * line_height < self.y + self.height - 70:
                screen.blit(text, (left_column_x, start_y + i * line_height))
        
        # Draw middle column (additional info) if available
        if hasattr(self, 'middle_info_lines') and self.middle_info_lines:
            # Draw vertical separator line
            separator1_x = self.x + self.column_width
            separator2_x = self.x + 2 * self.column_width
            pygame.draw.line(screen, self.secondary_color, 
                           (separator1_x, self.y + self.title_bar_height + 10),
                           (separator1_x, self.y + self.height - 60), 1)
            pygame.draw.line(screen, self.secondary_color, 
                           (separator2_x, self.y + self.title_bar_height + 10),
                           (separator2_x, self.y + self.height - 60), 1)
            
            # Draw middle column content
            for i, (line, color) in enumerate(self.middle_info_lines):
                text = font.render(line, True, color)
                # Check if text fits in the panel
                if start_y + i * line_height < self.y + self.height - 70:
                    screen.blit(text, (middle_column_x, start_y + i * line_height))

        # Desenhar botão de fechar apenas quando estiver em visualização detalhada
        if self.selected_component is not None:
            # Calculate center position for controls in the right column
            right_column_center_x = right_column_x + (self.column_width - self.input_width) // 2
            
            # Position controls vertically centered with spacing
            controls_start_y = self.y + self.title_bar_height + (self.height - self.title_bar_height - 60) // 2 - 50
            
            # Determinar texto e cor do botão de parar/iniciar
            is_component_stopped = False
            if self.selected_component == "generator":
                is_component_stopped = getattr(self, '_generator_ref', None) and getattr(self._generator_ref, 'is_stopped', False)
                
                # Position generator controls
                self.interval_input_rect.x = right_column_center_x
                self.interval_input_rect.y = controls_start_y
                
                self.stop_button_rect.x = right_column_center_x + (self.input_width - self.stop_button_width) // 2
                self.stop_button_rect.y = controls_start_y + 60  # Space between input and button
                
                # Draw generator controls
                self._draw_input_field(screen, self.interval_input_rect, self.interval_input_text, 
                                     self.is_interval_input_active, "Intervalo (s):")
            
            elif self.selected_component and self.selected_component.startswith("computer_"):
                computer_index = int(self.selected_component.split('_')[1]) - 1
                if (hasattr(self, '_computers_ref') and 
                    computer_index < len(self._computers_ref)):
                    computer = self._computers_ref[computer_index]
                    is_component_stopped = getattr(computer, 'is_stopped', False)
                
                # Position computer controls with vertical spacing
                self.processing_time_input_rect.x = right_column_center_x
                self.processing_time_input_rect.y = controls_start_y
                
                self.max_queue_time_input_rect.x = right_column_center_x
                self.max_queue_time_input_rect.y = controls_start_y + 50  # Space between inputs
                
                self.stop_button_rect.x = right_column_center_x + (self.input_width - self.stop_button_width) // 2
                self.stop_button_rect.y = controls_start_y + 120  # Space after second input
                
                # Draw computer controls
                self._draw_input_field(screen, self.processing_time_input_rect, self.processing_time_input_text,
                                     self.is_processing_time_input_active, "Tempo proc. (s):")
                
                self._draw_input_field(screen, self.max_queue_time_input_rect, self.max_queue_time_input_text,
                                     self.is_max_queue_time_input_active, "Tempo max. fila (s):")
            
            # Determinar cor do botão de fechar baseado no hover
            close_button_color = self.close_button_hover_color if self.is_close_button_hovered else self.close_button_color
            
            # Desenhar botão de fechar (círculo)
            pygame.draw.circle(screen, close_button_color, self.close_button_rect.center, self.close_button_size // 2)
            pygame.draw.circle(screen, self.text_color, self.close_button_rect.center, self.close_button_size // 2, 2)
            
            # Desenhar "X" no botão de fechar
            close_font = pygame.font.SysFont("Arial", 16, bold=True)
            close_text = close_font.render("×", True, self.text_color)
            text_rect = close_text.get_rect(center=self.close_button_rect.center)
            screen.blit(close_text, text_rect)
            
            stop_button_text = "LIGAR" if is_component_stopped else "PARAR"
            stop_button_color = self.stop_button_start_color if is_component_stopped else self.stop_button_color
            stop_button_hover_color = self.stop_button_start_hover_color if is_component_stopped else self.stop_button_hover_color
            
            # Determinar cor do botão de parar/iniciar baseado no hover
            current_stop_button_color = stop_button_hover_color if self.is_stop_button_hovered else stop_button_color
            
            # Desenhar botão de parar/iniciar (com bordas arredondadas)
            pygame.draw.rect(screen, current_stop_button_color, self.stop_button_rect, border_radius=6)
            pygame.draw.rect(screen, self.text_color, self.stop_button_rect, 2, border_radius=6)
            
            # Desenhar texto no botão de parar/iniciar
            stop_font = pygame.font.SysFont("Arial", 18, bold=True)
            stop_text = stop_font.render(stop_button_text, True, self.text_color)
            stop_text_rect = stop_text.get_rect(center=self.stop_button_rect.center)
            screen.blit(stop_text, stop_text_rect)

    def _draw_input_field(self, screen, rect, text, is_active, label):
        """Desenha um campo de entrada estilizado"""
        # Determinar cor do campo de entrada
        input_color = self.interval_input_active_color if is_active else self.interval_input_color
        
        # Desenhar campo de entrada com bordas arredondadas
        pygame.draw.rect(screen, input_color, rect, border_radius=4)
        pygame.draw.rect(screen, self.accent_color, rect, 2, border_radius=4)
        
        # Desenhar texto do campo de entrada
        input_font = pygame.font.SysFont("Arial", 16)
        input_text_surface = input_font.render(text, True, self.text_color)
        
        # Calcular posição do texto (centralizado verticalmente)
        text_y = rect.y + (rect.height - input_text_surface.get_height()) // 2
        text_x = rect.x + 8  # Reduced padding for smaller input
        screen.blit(input_text_surface, (text_x, text_y))
        
        # Desenhar label
        label_font = pygame.font.SysFont("Arial", 14)
        label_text = label_font.render(label, True, self.text_color)
        # Center the label above the input field
        label_x = rect.x + (rect.width - label_text.get_width()) // 2
        screen.blit(label_text, (label_x, rect.y - 20))
        
        # Desenhar cursor se estiver ativo
        if is_active:
            cursor_x = text_x + input_text_surface.get_width() + 2
            cursor_y = rect.y + 5
            cursor_height = rect.height - 10
            pygame.draw.line(screen, self.text_color, (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + cursor_height), 2)
    
    def set_component_references(self, computers, generator, simulator=None):
        """Define referências aos componentes para verificar estado"""
        self._computers_ref = computers
        self._generator_ref = generator
        self._simulator_ref = simulator
        
        # Set initial input text based on current values
        if simulator and hasattr(simulator, 'current_interval_seconds'):
            self.interval_input_text = f"{simulator.current_interval_seconds:.2f}"
        
        if simulator and hasattr(simulator, 'max_queue_time_seconds'):
            self.max_queue_time_input_text = f"{simulator.max_queue_time_seconds:.2f}"
        
        if computers and len(computers) > 0:
            self.processing_time_input_text = f"{computers[0].processing_time_ms/1000:.2f}"