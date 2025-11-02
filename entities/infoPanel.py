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

    def update_info(self, computer, queue, processes):
        """Atualiza as informações exibidas no painel"""
        cpu_status = "OCIOSA" if computer.is_idle else f"Processando P{computer.current_process.id}"
        fila_status = f"{len(queue)} processo(s) na fila"
        concluidos = sum(p.state.name == "FINISHED" for p in processes)

        self.info_lines = [
            f"CPU: {cpu_status}",
            f"Fila: {fila_status}",
            f"Concluídos: {concluidos}"
        ]

    def draw(self, screen: pygame.Surface) -> None:
        """Desenha o painel na tela (mesmo estilo da CPU)"""
        # Retângulo principal
        pygame.draw.rect(screen, self.background_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, Colors.WHITE, (self.x, self.y, self.width, self.height), 2)

        # Fonte
        font = pygame.font.SysFont(None, 30)
        title_font = pygame.font.SysFont(None, 32, bold=True)

        # Título
        title_text = title_font.render("INFO", True, Colors.BLACK)
        screen.blit(title_text, (self.x + self.width // 2 - 25, self.y + self.height // 2 - 50))

        # Linhas de informação
        for i, line in enumerate(self.info_lines):
            text = font.render(line, True, Colors.BLACK)
            screen.blit(text, (self.x + 20, self.y + self.height // 2 - 10 + i * 30))
