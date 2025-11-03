import pygame
from config import Colors, GridPositions, ElementSizes
from utils.grid_helper import GridHelper

class InfoPanel:
    def __init__(self):
        # Mesmas dimensões do computador
        col, row = GridPositions.INFO_PANEL
        width_cells, height_cells = ElementSizes.INFO_PANEL

        self.x, self.y, self.width, self.height = GridHelper.grid_to_pixels(
            col, row, width_cells, height_cells
        )

        self.info_lines = []
        self.background_color = Colors.WHITE
        self.selected_component = None
        
        # Close button properties
        self.close_button_size = 20
        self.close_button_rect = pygame.Rect(
            self.x + self.width - 30, 
            self.y + 10, 
            self.close_button_size, 
            self.close_button_size
        )
        self.close_button_color = Colors.RED
        self.close_button_hover_color = (200, 0, 0)  # Darker red
        self.is_close_button_hovered = False
        
        # Stop/Start button properties
        self.stop_button_rect = pygame.Rect(
            self.x + 20,
            self.y + self.height - 40,
            self.width - 40,
            30
        )
        self.stop_button_color = Colors.RED
        self.stop_button_start_color = Colors.GREEN
        self.stop_button_hover_color = (180, 0, 0)  # Darker red
        self.stop_button_start_hover_color = (0, 180, 0)  # Darker green
        self.is_stop_button_hovered = False

        # Interval input properties (in seconds) - for generator
        self.interval_input_rect = pygame.Rect(
            self.x + 20,
            self.y + self.height - 80,
            self.width - 40,
            30
        )
        self.interval_input_text = "1.0"  # Default value (1 second)
        self.is_interval_input_active = False
        self.interval_input_color = Colors.WHITE
        self.interval_input_active_color = Colors.LIGHT_GREEN

        # Processing time input properties (in seconds) - for computer
        self.processing_time_input_rect = pygame.Rect(
            self.x + 20,
            self.y + self.height - 80,
            self.width - 40,
            30
        )
        self.processing_time_input_text = "2.0"  # Default value (2 seconds)
        self.is_processing_time_input_active = False
        self.processing_time_input_color = Colors.WHITE
        self.processing_time_input_active_color = Colors.LIGHT_GREEN

    def update_info(self, computer, connection, processes, current_interval_seconds=None):
        """Atualiza as informações exibidas no painel"""
        if self.selected_component == "computer":
            self._show_computer_info(computer, connection)
        elif self.selected_component == "generator":
            self._show_generator_info(connection, computer, current_interval_seconds)
        else:
            self._show_general_info(computer, connection, processes, current_interval_seconds)

    def _show_general_info(self, computer, connection, processes, current_interval_seconds):
        """Mostra informações gerais do sistema"""
        cpu_status = "OCIOSA" if computer.is_idle else f"Processando P{computer.current_process.id}"
        cpu_stopped = "(PARADA)" if getattr(computer, 'is_stopped', False) else ""
        generator_stopped = "(PARADO)" if getattr(connection.generator, 'is_stopped', False) else ""
        
        fila_status = f"{len(connection.cpu_queue)} processo(s) na fila"
        concluidos = sum(1 for p in processes if not p.is_active)

        self.info_lines = [
            "=== SISTEMA ===",
            f"CPU: {cpu_status} {cpu_stopped}",
            f"Gerador: {generator_stopped}",
            f"Intervalo: {current_interval_seconds:.2f} segundos",
            f"Processamento: {computer.processing_time_ms/1000:.2f} segundos",
            f"Fila: {fila_status}",
            f"Concluídos: {concluidos}",
            f"Capacidade: {connection.total_processes}/{connection.max_capacity}",
            "",
            "Clique em um componente",
            "para mais informações e controles"
        ]

    def _show_computer_info(self, computer, connection):
        """Mostra informações detalhadas da CPU"""
        status = "PROCESSANDO" if not computer.is_idle else "OCIOSO"
        processo_atual = f"P{computer.current_process.id}" if computer.current_process else "Nenhum"
        is_stopped = getattr(computer, 'is_stopped', False)
        stopped_status = " (PARADA)" if is_stopped else ""
        
        self.info_lines = [
            "=== CPU ===",
            f"Status: {status}{stopped_status}",
            f"Processo atual: {processo_atual}",
            f"Fila de CPU: {len(connection.cpu_queue)} processos",
            f"Tempo de processamento: {computer.processing_time_ms/1000:.2f} segundos",
            "",
            "Estatísticas:",
            f"- Processos na fila: {len(connection.cpu_queue)}",
            f"- Capacidade: {connection.total_processes}/{connection.max_capacity}",
            f"- Velocidade: {connection.transport_speed} px/frame",
            "",
            "Controles:",
            f"- Botão {'LIGAR' if is_stopped else 'PARAR'} para {'retomar' if is_stopped else 'pausar'} processamento",
            "- Digite o tempo de processamento (em segundos) abaixo",
            "- Enter para aplicar, ESC para cancelar",
            "- Clique no X para voltar"
        ]

    def _show_generator_info(self, connection, computer, current_interval_seconds):
        """Mostra informações detalhadas do gerador"""
        is_stopped = getattr(connection.generator, 'is_stopped', False)
        stopped_status = " (PARADO)" if is_stopped else ""
        
        self.info_lines = [
            "=== GERADOR ===",
            f"Status: {'PARADO' if is_stopped else 'ATIVO'}{stopped_status}",
            f"Intervalo atual: {current_interval_seconds:.2f} segundos",
            f"Processos criados: {connection.generator.next_process_id - 1}",
            f"Fila de entrada: {len(connection.input_queue)} processos",
            f"Em trânsito: {len(connection.transit_processes)} processos",
            "",
            "Controles:",
            f"- Botão {'LIGAR' if is_stopped else 'PARAR'} para {'retomar' if is_stopped else 'pausar'} geração",
            "- Digite o intervalo desejado (em segundos) abaixo",
            "- Enter para aplicar, ESC para cancelar",
            "- Clique no X para voltar"
        ]

    def select_component(self, component_type):
        """Seleciona qual componente mostrar informações"""
        self.selected_component = component_type

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

    def activate_interval_input(self):
        """Ativa o campo de entrada de intervalo"""
        self.is_interval_input_active = True
        self.is_processing_time_input_active = False

    def activate_processing_time_input(self):
        """Ativa o campo de entrada de tempo de processamento"""
        self.is_processing_time_input_active = True
        self.is_interval_input_active = False

    def deactivate_all_inputs(self):
        """Desativa todos os campos de entrada"""
        self.is_interval_input_active = False
        self.is_processing_time_input_active = False

    def add_character_to_interval_input(self, char):
        """Adiciona um caractere ao campo de entrada de intervalo"""
        # Allow digits, decimal point, and backspace is handled separately
        if char.isdigit() or char == '.':
            # Only allow one decimal point
            if char == '.' and '.' in self.interval_input_text:
                return
            self.interval_input_text += char

    def add_character_to_processing_time_input(self, char):
        """Adiciona um caractere ao campo de entrada de tempo de processamento"""
        # Allow digits, decimal point, and backspace is handled separately
        if char.isdigit() or char == '.':
            # Only allow one decimal point
            if char == '.' and '.' in self.processing_time_input_text:
                return
            self.processing_time_input_text += char

    def remove_character_from_interval_input(self):
        """Remove o último caractere do campo de entrada de intervalo"""
        if len(self.interval_input_text) > 0:
            self.interval_input_text = self.interval_input_text[:-1]

    def remove_character_from_processing_time_input(self):
        """Remove o último caractere do campo de entrada de tempo de processamento"""
        if len(self.processing_time_input_text) > 0:
            self.processing_time_input_text = self.processing_time_input_text[:-1]

    def clear_interval_input(self):
        """Limpa o campo de entrada de intervalo"""
        self.interval_input_text = ""

    def clear_processing_time_input(self):
        """Limpa o campo de entrada de tempo de processamento"""
        self.processing_time_input_text = ""

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

    def update_button_hover(self, pos):
        """Atualiza o estado de hover dos botões"""
        self.is_close_button_hovered = self.close_button_rect.collidepoint(pos)
        self.is_stop_button_hovered = self.stop_button_rect.collidepoint(pos)

    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o painel na tela (mesmo estilo da CPU)"""
        # Retângulo principal
        pygame.draw.rect(screen, self.background_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, Colors.BLACK, (self.x, self.y, self.width, self.height), 2)

        # Fonte
        font = pygame.font.SysFont(None, 22)  # Slightly smaller font to fit more text
        title_font = pygame.font.SysFont(None, 26, bold=True)  # Slightly smaller title font

        # Título baseado no componente selecionado
        title = {
            "computer": "INFORMAÇÕES DA CPU",
            "generator": "INFORMAÇÕES DO GERADOR",
            None: "PAINEL DE INFORMAÇÕES"
        }.get(self.selected_component, "PAINEL DE INFORMAÇÕES")
        
        title_text = title_font.render(title, True, Colors.BLACK)
        screen.blit(title_text, (self.x + self.width // 2 - title_text.get_width() // 2, self.y + 15))

        # Linhas de informação - adjusted spacing for more room
        line_height = 20  # Reduced line height to fit more lines
        start_y = self.y + 45  # Start lower to make room for title
        
        for i, line in enumerate(self.info_lines):
            text = font.render(line, True, Colors.BLACK)
            screen.blit(text, (self.x + 20, start_y + i * line_height))

        # Desenhar botão de fechar apenas quando estiver em visualização detalhada
        if self.selected_component is not None:
            # Determinar cor do botão de fechar baseado no hover
            close_button_color = self.close_button_hover_color if self.is_close_button_hovered else self.close_button_color
            
            # Desenhar botão de fechar
            pygame.draw.rect(screen, close_button_color, self.close_button_rect)
            pygame.draw.rect(screen, Colors.BLACK, self.close_button_rect, 2)
            
            # Desenhar "X" no botão de fechar
            close_font = pygame.font.SysFont(None, 20)
            close_text = close_font.render("X", True, Colors.WHITE)
            text_rect = close_text.get_rect(center=self.close_button_rect.center)
            screen.blit(close_text, text_rect)
            
            # Determinar texto e cor do botão de parar/iniciar
            is_component_stopped = False
            if self.selected_component == "computer":
                is_component_stopped = getattr(self, '_computer_ref', None) and getattr(self._computer_ref, 'is_stopped', False)
            elif self.selected_component == "generator":
                is_component_stopped = getattr(self, '_generator_ref', None) and getattr(self._generator_ref, 'is_stopped', False)
            
            stop_button_text = "LIGAR" if is_component_stopped else "PARAR"
            stop_button_color = self.stop_button_start_color if is_component_stopped else self.stop_button_color
            stop_button_hover_color = self.stop_button_start_hover_color if is_component_stopped else self.stop_button_hover_color
            
            # Determinar cor do botão de parar/iniciar baseado no hover
            current_stop_button_color = stop_button_hover_color if self.is_stop_button_hovered else stop_button_color
            
            # Desenhar botão de parar/iniciar
            pygame.draw.rect(screen, current_stop_button_color, self.stop_button_rect)
            pygame.draw.rect(screen, Colors.BLACK, self.stop_button_rect, 2)
            
            # Desenhar texto no botão de parar/iniciar
            stop_font = pygame.font.SysFont(None, 22)
            stop_text = stop_font.render(stop_button_text, True, Colors.WHITE)
            stop_text_rect = stop_text.get_rect(center=self.stop_button_rect.center)
            screen.blit(stop_text, stop_text_rect)
            
            # Desenhar campo de entrada apropriado baseado no componente selecionado
            if self.selected_component == "generator":
                # Determinar cor do campo de entrada
                input_color = self.interval_input_active_color if self.is_interval_input_active else self.interval_input_color
                
                # Desenhar campo de entrada
                pygame.draw.rect(screen, input_color, self.interval_input_rect)
                pygame.draw.rect(screen, Colors.BLACK, self.interval_input_rect, 2)
                
                # Desenhar texto do campo de entrada
                input_font = pygame.font.SysFont(None, 22)
                input_text = input_font.render(self.interval_input_text, True, Colors.BLACK)
                
                # Calcular posição do texto (centralizado verticalmente)
                text_y = self.interval_input_rect.y + (self.interval_input_rect.height - input_text.get_height()) // 2
                screen.blit(input_text, (self.interval_input_rect.x + 10, text_y))
                
                # Desenhar label
                label_text = input_font.render("Intervalo (segundos):", True, Colors.BLACK)
                screen.blit(label_text, (self.interval_input_rect.x, self.interval_input_rect.y - 25))
            
            elif self.selected_component == "computer":
                # Determinar cor do campo de entrada
                input_color = self.processing_time_input_active_color if self.is_processing_time_input_active else self.processing_time_input_color
                
                # Desenhar campo de entrada
                pygame.draw.rect(screen, input_color, self.processing_time_input_rect)
                pygame.draw.rect(screen, Colors.BLACK, self.processing_time_input_rect, 2)
                
                # Desenhar texto do campo de entrada
                input_font = pygame.font.SysFont(None, 22)
                input_text = input_font.render(self.processing_time_input_text, True, Colors.BLACK)
                
                # Calcular posição do texto (centralizado verticalmente)
                text_y = self.processing_time_input_rect.y + (self.processing_time_input_rect.height - input_text.get_height()) // 2
                screen.blit(input_text, (self.processing_time_input_rect.x + 10, text_y))
                
                # Desenhar label
                label_text = input_font.render("Tempo processamento (segundos):", True, Colors.BLACK)
                screen.blit(label_text, (self.processing_time_input_rect.x, self.processing_time_input_rect.y - 25))
    
    def set_component_references(self, computer, generator, simulator=None):
        """Define referências aos componentes para verificar estado"""
        self._computer_ref = computer
        self._generator_ref = generator
        self._simulator_ref = simulator
        
        # Set initial input text based on current simulator values
        if simulator and hasattr(simulator, 'current_interval_seconds'):
            self.interval_input_text = f"{simulator.current_interval_seconds:.2f}"
        
        # Set initial processing time text based on computer's current value
        if computer and hasattr(computer, 'processing_time_ms'):
            self.processing_time_input_text = f"{computer.processing_time_ms/1000:.2f}"