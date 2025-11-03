import pygame
from config import Colors, GridPositions, ElementSizes, CPU_COLORS
from utils.grid_helper import GridHelper

class ShopPanel:
    def __init__(self):
        # Posicionar na parte direita da tela (coluna 10, linha 0)
        col, row = 10, 0
        width_cells, height_cells = 2, 8  # 2 colunas de largura, altura total
        
        self.x, self.y, self.width, self.height = GridHelper.grid_to_pixels(
            col, row, width_cells, height_cells
        )
        
        self.background_color = Colors.DARK_GRAY
        self.border_color = Colors.WHITE
        self.text_color = Colors.WHITE
        self.highlight_color = Colors.GREEN
        
        # Itens da loja
        self.shop_items = [
            {
                "id": "cpu_4",
                "name": "CPU 4",
                "description": "Nova CPU Verde",
                "price": 10,
                "color": Colors.GREEN,
                "purchased": False
            },
            {
                "id": "cpu_5", 
                "name": "CPU 5",
                "description": "Nova CPU Amarela",
                "price": 20,
                "color": Colors.YELLOW,
                "purchased": False
            },
            {
                "id": "cpu_6",
                "name": "CPU 6", 
                "description": "Nova CPU Roxa",
                "price": 30,
                "color": Colors.PURPLE,
                "purchased": False
            },
            {
                "id": "upgrade_speed",
                "name": "Velocidade +",
                "description": "Aumenta velocidade transporte",
                "price": 15,
                "color": Colors.CYAN,
                "purchased": False
            },
            {
                "id": "upgrade_capacity",
                "name": "Capacidade +", 
                "description": "Aumenta capacidade do sistema",
                "price": 25,
                "color": Colors.ORANGE,
                "purchased": False
            }
        ]
        
        # Calcular retângulos dos itens
        self.item_rects = []
        self._calculate_item_rects()
    
    def _calculate_item_rects(self):
        """Calcula os retângulos de cada item da loja"""
        self.item_rects = []
        item_height = 80
        padding = 10
        
        for i, item in enumerate(self.shop_items):
            rect_y = self.y + padding + (i * (item_height + padding))
            rect = pygame.Rect(
                self.x + padding,
                rect_y,
                self.width - (padding * 2),
                item_height
            )
            self.item_rects.append(rect)
    
    def is_clicked(self, pos):
        """Verifica se algum item foi clicado"""
        for i, rect in enumerate(self.item_rects):
            if rect.collidepoint(pos):
                return self.shop_items[i]
        return None
    
    def purchase_item(self, item_id, current_score):
        """Tenta comprar um item"""
        for item in self.shop_items:
            if item["id"] == item_id and not item["purchased"] and current_score >= item["price"]:
                item["purchased"] = True
                return True, item["price"]
        return False, 0
    
    def is_item_purchased(self, item_id):
        """Verifica se um item já foi comprado"""
        for item in self.shop_items:
            if item["id"] == item_id:
                return item["purchased"]
        return False
    
    def draw(self, screen: pygame.Surface, current_score: int) -> None:
        """Desenha o painel da loja"""
        # Fundo
        pygame.draw.rect(screen, self.background_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2)
        
        # Título
        font_large = pygame.font.SysFont(None, 28)
        font_medium = pygame.font.SysFont(None, 22)
        font_small = pygame.font.SysFont(None, 18)
        
        title_text = font_large.render("LOJA", True, self.text_color)
        screen.blit(title_text, (self.x + self.width//2 - title_text.get_width()//2, self.y + 10))
        
        # Pontuação atual
        score_text = font_medium.render(f"Pontos: {current_score}", True, Colors.GREEN)
        screen.blit(score_text, (self.x + self.width//2 - score_text.get_width()//2, self.y + 40))
        
        # Itens da loja
        for i, (item, rect) in enumerate(zip(self.shop_items, self.item_rects)):
            # Cor do fundo baseado no estado
            if item["purchased"]:
                bg_color = Colors.DARK_GRAY
                border_color = Colors.GREEN
            elif current_score >= item["price"]:
                bg_color = Colors.GRAY
                border_color = self.highlight_color
            else:
                bg_color = Colors.DARK_GRAY
                border_color = Colors.RED
            
            # Fundo do item
            pygame.draw.rect(screen, bg_color, rect)
            pygame.draw.rect(screen, border_color, rect, 2)
            
            # Nome do item
            name_text = font_medium.render(item["name"], True, item["color"])
            screen.blit(name_text, (rect.x + 10, rect.y + 10))
            
            # Descrição
            desc_text = font_small.render(item["description"], True, self.text_color)
            screen.blit(desc_text, (rect.x + 10, rect.y + 35))
            
            # Preço
            price_color = Colors.GREEN if current_score >= item["price"] else Colors.RED
            price_status = "COMPRADO" if item["purchased"] else f"Preço: {item['price']} pts"
            price_text = font_small.render(price_status, True, price_color)
            screen.blit(price_text, (rect.x + 10, rect.y + 55))