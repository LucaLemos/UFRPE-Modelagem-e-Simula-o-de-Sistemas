SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Sistema de Grid
GRID_COLUMNS = 12
GRID_ROWS = 8
MARGIN = 10

CELL_WIDTH = SCREEN_WIDTH // GRID_COLUMNS
CELL_HEIGHT = SCREEN_HEIGHT // GRID_ROWS

# Cores
class Colors:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    YELLOW = (255, 255, 0)
    DARK_GRAY = (50, 50, 50)
    LIGHT_GREEN = (100, 255, 100)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    CYAN = (0, 255, 255)
    PINK = (255, 192, 203)

# Frequências de Geração
GENERATION_FREQUENCIES = [
    {"name": "Muito Lento", "value": 180, "description": "3 segundos"},
    {"name": "Lento", "value": 120, "description": "2 segundos"},
    {"name": "Normal", "value": 60, "description": "1 segundo"},
    {"name": "Rápido", "value": 30, "description": "0.5 segundos"},
    {"name": "Muito Rápido", "value": 15, "description": "0.25 segundos"}
]

# Posições no Grid
class GridPositions:
    SCORE_DISPLAY = (0, 0)
    TIMER_DISPLAY = (1, 0)
    EVENT_DISPLAY = (2, 0)
    HEALTH_BAR = (6, 0)
    BACK_BUTTON = (9, 0) 
    
    GENERATOR = (1, 1)  
    COMPUTER_1 = (5, 1)  # CPU 1
    COMPUTER_2 = (5, 2)  # CPU 2
    COMPUTER_3 = (5, 3)  # CPU 3
    COMPUTER_4 = (7, 1)  # Nova CPU 4
    COMPUTER_5 = (7, 2)  # Nova CPU 5  
    COMPUTER_6 = (7, 3)  # Nova CPU 6
    INFO_PANEL = (0, 4)
    SHOP_PANEL = (10, 0)

# Tamanhos dos Elementos
class ElementSizes:
    COMPUTER = (1, 1)
    GENERATOR = (1, 1)
    INFO_PANEL = (10, 4)
    SHOP_PANEL = (2, 8)
    HEALTH_BAR = (3, 1)

# Configurações de Processamento
PROCESSING_TIME_MS = 2000  # 2 segundos
MAX_CONNECTION_CAPACITY = 15  # Aumentada para múltiplas CPUs
TRANSPORT_SPEED = 3.0

# Cores para múltiplas CPUs
CPU_COLORS = [Colors.RED, Colors.CYAN, Colors.PINK]  # Adicionada esta linha
MAX_HEALTH_POINTS = 15