import pygame
import sys
from core.queue_simulator import QueueSimulator
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def main():
    # Inicialização
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Queue Simulator - Gerenciamento de Processos")
    
    # Criar simulador
    simulator = QueueSimulator()
    clock = pygame.time.Clock()
    is_running = True
    
    # Loop principal
    while is_running:
        # Processar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo do mouse
                    simulator.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                simulator.handle_mouse_motion(event.pos)
            elif event.type == pygame.KEYDOWN:
                simulator.handle_key_event(event)
        
        # Atualizar e desenhar
        simulator.update()
        simulator.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()