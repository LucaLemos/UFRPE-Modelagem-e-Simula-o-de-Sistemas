import pygame
from config import VERMELHO, BRANCO, POS_COMPUTADOR, TAMANHO_COMPUTADOR
from utils.grid_helper import GridHelper

class Computador:
    def __init__(self):
        col, lin = POS_COMPUTADOR
        larg_cel, alt_cel = TAMANHO_COMPUTADOR
        self.x, self.y, self.largura, self.altura = GridHelper.para_pixels(col, lin, larg_cel, alt_cel)
        self.cor = VERMELHO
        self.processor_ocioso = True
        self.processo_atual = None
    
    def desenhar(self, tela):
        # Desenha o computador
        pygame.draw.rect(tela, self.cor, (self.x, self.y, self.largura, self.altura))
        pygame.draw.rect(tela, BRANCO, (self.x, self.y, self.largura, self.altura), 2)  # Borda
        
        # Texto
        fonte = pygame.font.SysFont(None, 30)
        texto = fonte.render("CPU", True, BRANCO)
        tela.blit(texto, (self.x + self.largura//2 - 20, self.y + self.altura//2 - 30))
        
        # Status
        status = "OCIOSO" if self.processor_ocioso else "EXECUTANDO"
        texto_status = fonte.render(status, True, BRANCO)
        tela.blit(texto_status, (self.x + self.largura//2 - 40, self.y + self.altura//2 + 10))
    
    def get_centro(self):
        return self.x + self.largura // 2, self.y + self.altura // 2