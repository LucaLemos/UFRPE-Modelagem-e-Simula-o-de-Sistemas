import pygame
from config import Colors, SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu:
    def __init__(self):
        self.background_color = (20, 25, 45)  # Dark blue background
        self.title_color = (70, 130, 180)     # Steel blue
        self.button_color = (40, 90, 140)     # Medium blue
        self.button_hover_color = (60, 120, 190)  # Light blue
        self.text_color = Colors.WHITE
        self.highlight_color = (100, 200, 255)  # Bright blue
        
        # Title
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 24)
        self.button_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.description_font = pygame.font.SysFont("Arial", 18)
        
        # Game mode buttons
        button_width, button_height = 300, 80
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.sandbox_button = pygame.Rect(
            button_x, SCREEN_HEIGHT // 2 - 60, 
            button_width, button_height
        )
        
        self.game_button = pygame.Rect(
            button_x, SCREEN_HEIGHT // 2 + 60, 
            button_width, button_height
        )
        
        # Hover states
        self.sandbox_hovered = False
        self.game_hovered = False

    def handle_click(self, pos):
        """Verifica qual botão foi clicado"""
        if self.sandbox_button.collidepoint(pos):
            return "sandbox"
        elif self.game_button.collidepoint(pos):
            return "game"
        return None

    def handle_mouse_motion(self, pos):
        """Atualiza estados de hover"""
        self.sandbox_hovered = self.sandbox_button.collidepoint(pos)
        self.game_hovered = self.game_button.collidepoint(pos)

    def draw(self, screen):
        """Desenha o menu principal"""
        # Fundo gradiente simples
        screen.fill(self.background_color)
        
        # Desenhar elementos decorativos
        self._draw_background_elements(screen)
        
        # Título
        title_text = self.title_font.render("QUEUE SIMULATOR", True, self.title_color)
        subtitle_text = self.subtitle_font.render("Sistema de Gerenciamento de Processos", True, self.text_color)
        
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 160))
        
        # Botões dos modos
        self._draw_button(screen, self.sandbox_button, "MODO SANDBOX", self.sandbox_hovered)
        self._draw_button(screen, self.game_button, "MODO JOGO", self.game_hovered)
        
        # Descrições dos modos
        self._draw_descriptions(screen)

    def _draw_background_elements(self, screen):
        """Desenha elementos decorativos de fundo"""
        # Linhas decorativas
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(screen, (30, 40, 60), (i, 0), (i, SCREEN_HEIGHT), 1)
        
        # Partículas decorativas (simulando processos)
        for i in range(20):
            x = (i * 80) % SCREEN_WIDTH
            y = (i * 60) % SCREEN_HEIGHT
            size = 3 + (i % 3)
            color = [(100, 180, 255), (80, 200, 120), (255, 180, 80)][i % 3]
            pygame.draw.circle(screen, color, (x, y), size)

    def _draw_button(self, screen, button_rect, text, is_hovered):
        """Desenha um botão estilizado"""
        # Cor baseada no hover
        color = self.button_hover_color if is_hovered else self.button_color
        
        # Botão principal com sombra
        pygame.draw.rect(screen, (20, 30, 50), 
                        (button_rect.x + 4, button_rect.y + 4, button_rect.width, button_rect.height),
                        border_radius=12)
        
        # Botão principal
        pygame.draw.rect(screen, color, button_rect, border_radius=12)
        pygame.draw.rect(screen, self.highlight_color, button_rect, 3, border_radius=12)
        
        # Texto do botão
        text_surface = self.button_font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)
        
        # Ícone decorativo baseado no modo
        if "SANDBOX" in text:
            self._draw_sandbox_icon(screen, button_rect)
        else:
            self._draw_game_icon(screen, button_rect)

    def _draw_sandbox_icon(self, screen, button_rect):
        """Desenha ícone para modo sandbox"""
        icon_x = button_rect.x + 30
        icon_y = button_rect.centery
        
        # Chave inglesa e lupa (símbolos de ferramentas/experimentação)
        pygame.draw.rect(screen, self.highlight_color, (icon_x, icon_y - 8, 16, 4), border_radius=2)
        pygame.draw.rect(screen, self.highlight_color, (icon_x + 6, icon_y - 12, 4, 8), border_radius=1)
        pygame.draw.circle(screen, self.highlight_color, (icon_x + 25, icon_y), 10, 2)
        pygame.draw.line(screen, self.highlight_color, (icon_x + 25, icon_y), (icon_x + 32, icon_y - 7), 2)

    def _draw_game_icon(self, screen, button_rect):
        """Desenha ícone para modo jogo"""
        icon_x = button_rect.x + 30
        icon_y = button_rect.centery
        
        # Troféu (símbolo de desafio/conquista)
        pygame.draw.rect(screen, self.highlight_color, (icon_x + 5, icon_y + 5, 6, 8), border_radius=1)
        pygame.draw.polygon(screen, (255, 215, 0), [
            (icon_x, icon_y - 5),
            (icon_x + 8, icon_y - 10),
            (icon_x + 16, icon_y - 5),
            (icon_x + 12, icon_y),
            (icon_x + 4, icon_y)
        ])

    def _draw_descriptions(self, screen):
        """Desenha as descrições dos modos"""
        desc_start_y = SCREEN_HEIGHT // 2 + 160
        
