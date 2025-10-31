import pygame
from config import GRID_COLUMNS, CELL_WIDTH, GRID_ROWS, CELL_HEIGHT, MARGIN, Colors

class GridHelper:
    @staticmethod
    def grid_to_pixels(column: int, row: int, width_cells: int = 1, height_cells: int = 1) -> tuple:
        """Converte coordenadas do grid para pixels"""
        x = column * CELL_WIDTH + MARGIN
        y = row * CELL_HEIGHT + MARGIN
        width = width_cells * CELL_WIDTH - MARGIN * 2
        height = height_cells * CELL_HEIGHT - MARGIN * 2
        return x, y, width, height
    
    @staticmethod
    def grid_center(column: int, row: int, width_cells: int = 1, height_cells: int = 1) -> tuple:
        """Retorna o centro de uma área do grid em pixels"""
        x, y, width, height = GridHelper.grid_to_pixels(column, row, width_cells, height_cells)
        return x + width // 2, y + height // 2
    
    @staticmethod
    def draw_grid(screen: pygame.Surface) -> None:
        """Desenha o grid de fundo (para debug)"""
        # Linhas verticais
        for column in range(GRID_COLUMNS + 1):
            x = column * CELL_WIDTH
            pygame.draw.line(screen, Colors.DARK_GRAY, (x, 0), (x, CELL_HEIGHT * GRID_ROWS), 1)
        
        # Linhas horizontais
        for row in range(GRID_ROWS + 1):
            y = row * CELL_HEIGHT
            pygame.draw.line(screen, Colors.DARK_GRAY, (0, y), (CELL_WIDTH * GRID_COLUMNS, y), 1)
        
        # Coordenadas (debug)
        font = pygame.font.SysFont(None, 16)
        for column in range(GRID_COLUMNS):
            for row in range(GRID_ROWS):
                x = column * CELL_WIDTH + 5
                y = row * CELL_HEIGHT + 5
                text = font.render(f"{column},{row}", True, Colors.DARK_GRAY)
                screen.blit(text, (x, y))