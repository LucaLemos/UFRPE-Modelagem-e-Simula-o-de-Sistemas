import pygame
from config import AZUL, BRANCO, VERDE_CLARO

class Processo:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.raio = 15
        self.cor = AZUL
        self.cor_original = AZUL
        self.velocidade = 2.0
        self.ativo = True
        self.tempo_chegada = pygame.time.get_ticks()
        self.em_fila = False
    
    def desenhar(self, tela):
        # Muda a cor se estiver em fila
        cor = VERDE_CLARO if self.em_fila else self.cor_original
        
        pygame.draw.circle(tela, cor, (int(self.x), int(self.y)), self.raio)
        pygame.draw.circle(tela, BRANCO, (int(self.x), int(self.y)), self.raio, 2)  # Borda
        
        fonte = pygame.font.SysFont(None, 20)
        texto = fonte.render(str(self.id), True, BRANCO)
        tela.blit(texto, (self.x - 5, self.y - 8))
    
    def mover_para(self, alvo_x, alvo_y):
        """Move o processo em direção a coordenadas específicas"""
        dx = alvo_x - self.x
        dy = alvo_y - self.y
        distancia = (dx**2 + dy**2)**0.5
        
        if distancia > self.velocidade:
            self.x += (dx / distancia) * self.velocidade
            self.y += (dy / distancia) * self.velocidade
            return False  # Ainda em movimento
        else:
            self.x, self.y = alvo_x, alvo_y
            return True  # Chegou ao destino
    
    def mover_para_computador(self, computador):
        alvo_x, alvo_y = computador.get_centro()
        return self.mover_para(alvo_x, alvo_y)