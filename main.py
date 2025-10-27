import pygame
import sys
from core.queue_simulator import QueueSimulator
from config import LARGURA, ALTURA, FPS

def main():
    # Inicialização
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Queue Simulator - Gerenciamento de Processos")
    
    # Cria o simulador
    simulador = QueueSimulator()
    clock = pygame.time.Clock()
    executando = True
    
    # Loop principal
    while executando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    simulador.gerar_processo()
                elif evento.key == pygame.K_a:
                    simulador.aumentar_frequencia()
                elif evento.key == pygame.K_z:
                    simulador.diminuir_frequencia()
                elif evento.key == pygame.K_g:
                    simulador.toggle_geracao_automatica()
                elif evento.key == pygame.K_ESCAPE:
                    executando = False
        
        # Atualiza e desenha
        simulador.atualizar()
        simulador.desenhar(tela)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()