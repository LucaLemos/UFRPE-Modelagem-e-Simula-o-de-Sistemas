# Configurações de Display
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
    GENERATOR = (1, 1)  
    COMPUTER = (9, 1)
    INFO_PANEL = (0, 6)  # ao lado do computador, por exemplo
  

# Tamanhos dos Elementos
class ElementSizes:
    COMPUTER = (2, 2)
    GENERATOR = (2, 2)
    INFO_PANEL = (12, 2)

# Configurações de Processamento
PROCESSING_TIME_MS = 2000  # 2 segundos
MAX_CONNECTION_CAPACITY = 10
TRANSPORT_SPEED = 3.0