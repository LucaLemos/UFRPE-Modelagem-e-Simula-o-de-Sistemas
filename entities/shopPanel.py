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
        
        # Itens da loja - AGORA COM UPGRADES INFINITOS
        self.shop_items = [
            {
                "id": "upgrade_processing_speed",
                "name": "Processar + Rápido",
                "description": "Reduz tempo de processamento",
                "base_price": 10,  # Preço base
                "price": 10,       # Preço atual
                "color": Colors.LIGHT_GREEN,
                "upgrade_level": 1,  # Nível atual do upgrade
                "price_increase": 1.4  # Fator de aumento de preço (40% por nível)
            },
            {
                "id": "upgrade_capacity",
                "name": "Capacidade +", 
                "description": "Aumenta capacidade do sistema",
                "base_price": 8,
                "price": 8,
                "color": Colors.ORANGE,
                "upgrade_level": 1,
                "price_increase": 1.35  # 35% por nível
            },
            {
                "id": "upgrade_speed",
                "name": "Velocidade +",
                "description": "Aumenta velocidade transporte",
                "base_price": 6,
                "price": 6,
                "color": Colors.CYAN,
                "upgrade_level": 1,
                "price_increase": 1.3  # 30% por nível
            },
            {
                "id": "cpu_2",
                "name": "CPU 2",
                "description": "Nova CPU Ciano",
                "price": 5,
                "color": Colors.CYAN,
                "purchased": False
            },
            {
                "id": "cpu_3", 
                "name": "CPU 3",
                "description": "Nova CPU Rosa",
                "price": 10,
                "color": Colors.PINK,
                "purchased": False
            },
            {
                "id": "cpu_4",
                "name": "CPU 4", 
                "description": "Nova CPU Verde",
                "price": 15,
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
                "price": 25,
                "color": Colors.PURPLE,
                "purchased": False
            }
        ]
        
        # Calcular retângulos dos itens
        self.item_rects = []
        self._calculate_item_rects()
    
    def _calculate_item_rects(self):
        """Calcula os retângulos de cada item da loja"""
        self.item_rects = []
        item_height = 70  # Reduzido para caber mais itens
        padding = 8
        
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
            if item["id"] == item_id:
                # Para upgrades infinitos
                if item["id"] in ["upgrade_processing_speed", "upgrade_capacity", "upgrade_speed"]:
                    if current_score >= item["price"]:
                        # Calcular novo preço para o próximo nível
                        current_level = item["upgrade_level"]
                        item["upgrade_level"] += 1
                        
                        # Calcular novo preço com aumento gradual
                        new_price = self._calculate_upgrade_price(
                            item["base_price"], 
                            current_level + 1, 
                            item["price_increase"]
                        )
                        item["price"] = new_price
                        
                        return True, item["price"]  # Retorna o preço pago (do nível atual)
                
                # Para CPUs (compra única)
                elif not item.get("purchased", False) and current_score >= item["price"]:
                    item["purchased"] = True
                    return True, item["price"]
        
        return False, 0
    
    def _calculate_upgrade_price(self, base_price, level, increase_factor):
        """Calcula o preço do upgrade baseado no nível"""
        # Fórmula: base_price * (increase_factor)^(level-1)
        return int(base_price * (increase_factor ** (level - 1)))
    
    def is_item_purchased(self, item_id):
        """Verifica se um item já foi comprado (apenas para CPUs)"""
        for item in self.shop_items:
            if item["id"] == item_id:
                if item["id"] in ["upgrade_processing_speed", "upgrade_capacity", "upgrade_speed"]:
                    # Upgrades infinitos sempre estão "disponíveis"
                    return False
                return item.get("purchased", False)
        return False
    
    def get_processing_speed_level(self):
        """Retorna o nível atual do upgrade de velocidade de processamento"""
        for item in self.shop_items:
            if item["id"] == "upgrade_processing_speed":
                return item.get("upgrade_level", 1)
        return 1
    
    def get_upgrade_level(self, upgrade_id):
        """Retorna o nível atual de qualquer upgrade"""
        for item in self.shop_items:
            if item["id"] == upgrade_id:
                return item.get("upgrade_level", 1)
        return 1
    
    def draw(self, screen: pygame.Surface, current_score: int) -> None:
        """Desenha o painel da loja"""
        # Fundo
        pygame.draw.rect(screen, self.background_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2)
        
        # Título
        font_large = pygame.font.SysFont(None, 28)
        font_medium = pygame.font.SysFont(None, 20)  # Reduzido
        font_small = pygame.font.SysFont(None, 16)   # Reduzido
        
        title_text = font_large.render("LOJA", True, self.text_color)
        screen.blit(title_text, (self.x + self.width//2 - title_text.get_width()//2, self.y + 10))
        
        # Pontuação atual
        score_text = font_medium.render(f"Pontos: {current_score}", True, Colors.GREEN)
        screen.blit(score_text, (self.x + self.width//2 - score_text.get_width()//2, self.y + 40))
        
        # Itens da loja
        for i, (item, rect) in enumerate(zip(self.shop_items, self.item_rects)):
            # Para upgrades infinitos
            if item["id"] in ["upgrade_processing_speed", "upgrade_capacity", "upgrade_speed"]:
                can_afford = current_score >= item["price"]
                
                if can_afford:
                    bg_color = Colors.GRAY
                    border_color = self.highlight_color
                else:
                    bg_color = Colors.DARK_GRAY
                    border_color = Colors.RED
            else:
                # Itens normais (CPUs)
                if item.get("purchased", False):
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
            screen.blit(name_text, (rect.x + 10, rect.y + 8))
            
            # Descrição
            desc_text = font_small.render(item["description"], True, self.text_color)
            screen.blit(desc_text, (rect.x + 10, rect.y + 28))
            
            # Preço e nível (para upgrades) ou status (para CPUs)
            if item["id"] in ["upgrade_processing_speed", "upgrade_capacity", "upgrade_speed"]:
                price_status = f"Preço: {item['price']} pts (Nv.{item['upgrade_level']})"
                price_color = Colors.GREEN if can_afford else Colors.RED
            else:
                price_status = "COMPRADO" if item.get("purchased", False) else f"Preço: {item['price']} pts"
                price_color = Colors.GREEN if (item.get("purchased", False) or current_score >= item["price"]) else Colors.RED
            
            price_text = font_small.render(price_status, True, price_color)
            screen.blit(price_text, (rect.x + 10, rect.y + 48))