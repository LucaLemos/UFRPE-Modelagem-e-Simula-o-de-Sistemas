import pygame
from config import VERDE, BRANCO, POS_GERADOR, TAMANHO_GERADOR
from utils.grid_helper import GridHelper

class GeradorProcessos:
    def __init__(self):
        col, lin = POS_GERADOR
        larg_cel, alt_cel = TAMANHO_GERADOR
        self.x, self.y, self.largura, self.altura = GridHelper.para_pixels(col, lin, larg_cel, alt_cel)
        self.tamanho_triangulo = min(self.largura, self.altura) * 0.8
        self.cor = VERDE
    
    def desenhar(self, tela):
        centro_x = self.x + self.largura // 2
        centro_y = self.y + self.altura // 2
        
        # Desenha triângulo
        pontos = [
            (centro_x, centro_y - self.tamanho_triangulo//2),  # Topo
            (centro_x - self.tamanho_triangulo//2, centro_y + self.tamanho_triangulo//2),  # Inferior esq
            (centro_x + self.tamanho_triangulo//2, centro_y + self.tamanho_triangulo//2)   # Inferior dir
        ]
        pygame.draw.polygon(tela, self.cor, pontos)
        pygame.draw.polygon(tela, BRANCO, pontos, 2)  # Borda
        
        # Texto
        fonte = pygame.font.SysFont(None, 24)
        texto = fonte.render("Gerador", True, BRANCO)
        tela.blit(texto, (centro_x - 35, centro_y + self.tamanho_triangulo//2 + 10))
    
    def get_centro(self):
        return self.x + self.largura // 2, self.y + self.altura // 2