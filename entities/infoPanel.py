import pygame
from config import Colors, GridPositions, ElementSizes
from utils.grid_helper import GridHelper

class InfoPanel:
    def __init__(self):
        # Mesmas dimensões do computador
        col, row = GridPositions.INFO_PANEL
        width_cells, height_cells = ElementSizes.INFO_PANEL  # mesmo tamanho da CPU

        self.x, self.y, self.width, self.height = GridHelper.grid_to_pixels(
            col, row, width_cells, height_cells
        )

        self.info_lines = []
        self.background_color = Colors.WHITE
        self.selected_component = None

    def update_info(self, computer, connection, processes):
        """Atualiza as informações exibidas no painel"""
        if self.selected_component == "computer":
            self._show_computer_info(computer, connection)
        elif self.selected_component == "generator":
            self._show_generator_info(connection)
        else:
            self._show_general_info(computer, connection, processes)

    def _show_general_info(self, computer, connection, processes):
        """Mostra informações gerais do sistema"""
        cpu_status = "OCIOSA" if computer.is_idle else f"Processando P{computer.current_process.id}"
        fila_status = f"{len(connection.cpu_queue)} processo(s) na fila"
        concluidos = sum(1 for p in processes if not p.is_active)

        self.info_lines = [
            "=== SISTEMA ===",
            f"CPU: {cpu_status}",
            f"Fila: {fila_status}",
            f"Concluídos: {concluidos}",
            f"Capacidade: {connection.total_processes}/{connection.max_capacity}",
            "",
            "Clique em um componente",
            "para mais informações"
        ]

    def _show_computer_info(self, computer, connection):
        """Mostra informações detalhadas da CPU"""
        status = "PROCESSANDO" if not computer.is_idle else "OCIOSO"
        processo_atual = f"P{computer.current_process.id}" if computer.current_process else "Nenhum"
        
        self.info_lines = [
            "=== CPU ===",
            f"Status: {status}",
            f"Processo atual: {processo_atual}",
            f"Fila de CPU: {len(connection.cpu_queue)} processos",
            "",
            "Estatísticas:",
            f"- Processos na fila: {len(connection.cpu_queue)}",
            f"- Capacidade: {connection.total_processes}/{connection.max_capacity}",
            f"- Velocidade: {connection.transport_speed} px/frame"
        ]

    def _show_generator_info(self, connection):
        """Mostra informações detalhadas do gerador"""
        self.info_lines = [
            "=== GERADOR ===",
            f"Processos criados: {connection.generator.next_process_id - 1}",
            f"Fila de entrada: {len(connection.input_queue)} processos",
            f"Em trânsito: {len(connection.transit_processes)} processos",
            "",
            "Capacidades:",
            f"- Máxima: {connection.max_capacity} processos",
            f"- Atual: {connection.total_processes} processos",
            f"- Disponível: {connection.max_capacity - connection.total_processes} processos"
        ]

    def select_component(self, component_type):
        """Seleciona qual componente mostrar informações"""
        self.selected_component = component_type

    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o painel na tela (mesmo estilo da CPU)"""
        # Retângulo principal
        pygame.draw.rect(screen, self.background_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, Colors.BLACK, (self.x, self.y, self.width, self.height), 2)

        # Fonte
        font = pygame.font.SysFont(None, 24)
        title_font = pygame.font.SysFont(None, 28, bold=True)

        # Título baseado no componente selecionado
        title = {
            "computer": "INFORMAÇÕES DA CPU",
            "generator": "INFORMAÇÕES DO GERADOR",
            None: "PAINEL DE INFORMAÇÕES"
        }.get(self.selected_component, "PAINEL DE INFORMAÇÕES")
        
        title_text = title_font.render(title, True, Colors.BLACK)
        screen.blit(title_text, (self.x + self.width // 2 - title_text.get_width() // 2, self.y + 20))

        # Linhas de informação
        for i, line in enumerate(self.info_lines):
            text = font.render(line, True, Colors.BLACK)
            screen.blit(text, (self.x + 20, self.y + 60 + i * 25))