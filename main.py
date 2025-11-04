import pygame
import sys
from core.queue_simulator import QueueSimulator
from core.main_menu import MainMenu
from config import Colors, SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from utils.grid_helper import GridHelper

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Queue Simulator - Gerenciamento de Processos")
        
        self.clock = pygame.time.Clock()
        self.current_state = "menu"  # menu, sandbox, game
        self.main_menu = MainMenu()
        self.simulator = None
        self.game_mode = None

    def run(self):
        """Loop principal do jogo"""
        while True:
            if self.current_state == "menu":
                self._handle_menu_state()
            elif self.current_state in ["sandbox", "game"]:
                self._handle_simulation_state()
            
            pygame.display.flip()
            self.clock.tick(FPS)

    def _handle_menu_state(self):
        """Gerencia o estado do menu"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    selected_mode = self.main_menu.handle_click(event.pos)
                    if selected_mode:
                        self._start_simulation(selected_mode)
            elif event.type == pygame.MOUSEMOTION:
                self.main_menu.handle_mouse_motion(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # Atalhos para modos
                elif event.key == pygame.K_1:
                    self._start_simulation("sandbox")
                elif event.key == pygame.K_2:
                    self._start_simulation("game")

        self.main_menu.draw(self.screen)

    def _handle_simulation_state(self):
        """Gerencia o estado de simulação"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._return_to_menu()
                else:
                    self.simulator.handle_key_event(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    # --- NOVO: deixar o painel tratar o clique do "X" primeiro ---
                    panel = getattr(self.simulator, 'info_panel', None)
                    if panel:
                        action = getattr(panel, 'handle_click', lambda *_: None)(event.pos)
                        if action == "close":
                            # Evita que o mesmo clique selecione outra coisa na UI
                            continue
                    # Depois, delega para a simulação normal
                    self.simulator.handle_click(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                # --- NOVO: atualizar hover do painel sempre, independente do modo ---
                panel = getattr(self.simulator, 'info_panel', None)
                if panel and hasattr(panel, 'update_button_hover'):
                    panel.update_button_hover(event.pos)
                # Depois, delega para a simulação normal
                self.simulator.handle_mouse_motion(event.pos)

        self.simulator.update()
        self.simulator.draw(self.screen)
        
        # Desenhar botão de voltar ao menu
        self._draw_back_button()

    def _start_simulation(self, mode):
        """Inicia a simulação no modo selecionado"""
        self.game_mode = mode
        self.simulator = QueueSimulator()
        
        self.simulator.set_game_mode(mode)

        # Configurar baseado no modo selecionado
        if mode == "sandbox":
            self._setup_sandbox_mode()
        else:  # game mode
            self._setup_game_mode()
        
        self.current_state = mode
        print(f"Iniciando modo: {mode}")

    def _setup_sandbox_mode(self):
        """Configura o modo sandbox"""
        # No sandbox, o jogador tem controle total
        self.simulator.is_auto_generation_enabled = True
        
        # Todas as CPUs disponíveis desde o início (se implementadas)
        # Configurações mais flexíveis para experimentação
        self.simulator.current_interval_seconds = 1.0
        self.simulator.max_queue_time_seconds = 15.0
        
        print("Modo Sandbox: Controle total habilitado")

    def _setup_game_mode(self):
        """Configura o modo jogo"""
        # No modo jogo, começa com configurações básicas
        self.simulator.is_auto_generation_enabled = True
        
        # Configurações balanceadas para desafio
        self.simulator.current_interval_seconds = 1.0
        self.simulator.max_queue_time_seconds = 8.0
        
        # Resetar pontuação para começar do zero
        self.simulator.score = 0
        
        print("Modo Jogo: Sistema de progressão ativado")

    def _return_to_menu(self):
        """Volta para o menu principal"""
        self.current_state = "menu"
        self.simulator = None
        self.game_mode = None
        print("Retornando ao menu principal")

    def _draw_back_button(self):
        """Desenha botão para voltar ao menu no grid (9,0)"""
        # Usar GridHelper para posicionar no grid (9,0)
        back_x, back_y, back_width, back_height = GridHelper.grid_to_pixels(9, 0, 1, 1)
        
        back_button = pygame.Rect(back_x, back_y, back_width, back_height)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = back_button.collidepoint(mouse_pos)
        
        # Cor do botão
        color = (200, 80, 80) if is_hovered else (150, 60, 60)
        
        # Desenhar botão
        pygame.draw.rect(self.screen, color, back_button, border_radius=6)
        pygame.draw.rect(self.screen, Colors.WHITE, back_button, 2, border_radius=6)
        
        # Texto
        font = pygame.font.SysFont("Arial", 18, bold=True)
        text = font.render("MENU", True, Colors.WHITE)
        text_rect = text.get_rect(center=back_button.center)
        self.screen.blit(text, text_rect)
        
        # Verificar clique
        if (is_hovered and pygame.mouse.get_pressed()[0] and 
            pygame.time.get_ticks() > 500):  # Pequeno delay para evitar clique acidental
            self._return_to_menu()

def main():
    game_manager = GameManager()
    game_manager.run()

if __name__ == "__main__":
    main()
