import pygame
from config import COLUNAS, LARGURA_COLUNA, LINHAS, ALTURA_LINHA, MARGEM, CINZA_ESCURO

class GridHelper:
    @staticmethod
    def para_pixels(coluna, linha, largura_celulas=1, altura_celulas=1):
        """Converte coordenadas do grid para pixels"""
        x = coluna * LARGURA_COLUNA + MARGEM
        y = linha * ALTURA_LINHA + MARGEM
        largura = largura_celulas * LARGURA_COLUNA - MARGEM * 2
        altura = altura_celulas * ALTURA_LINHA - MARGEM * 2
        return x, y, largura, altura
    
    @staticmethod
    def centro_pixels(coluna, linha, largura_celulas=1, altura_celulas=1):
        """Retorna o centro de uma célula/área do grid em pixels"""
        x, y, largura, altura = GridHelper.para_pixels(coluna, linha, largura_celulas, altura_celulas)
        return x + largura // 2, y + altura // 2
    
    @staticmethod
    def desenhar_grid(tela):
        """Desenha o grid de fundo (útil para debug)"""
        # Linhas verticais
        for coluna in range(COLUNAS + 1):
            x = coluna * LARGURA_COLUNA
            pygame.draw.line(tela, CINZA_ESCURO, (x, 0), (x, ALTURA_LINHA * LINHAS), 1)
        
        # Linhas horizontais
        for linha in range(LINHAS + 1):
            y = linha * ALTURA_LINHA
            pygame.draw.line(tela, CINZA_ESCURO, (0, y), (LARGURA_COLUNA * COLUNAS, y), 1)
        
        # Números das colunas (debug)
        fonte = pygame.font.SysFont(None, 16)
        for coluna in range(COLUNAS):
            for linha in range(LINHAS):
                x = coluna * LARGURA_COLUNA + 5
                y = linha * ALTURA_LINHA + 5
                texto = fonte.render(f"{coluna},{linha}", True, CINZA_ESCURO)
                tela.blit(texto, (x, y))