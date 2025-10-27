# Configurações do jogo
LARGURA = 1000
ALTURA = 600
FPS = 60

# Sistema de Grid
COLUNAS = 12
LARGURA_COLUNA = LARGURA // COLUNAS
MARGEM = 20

LINHAS = 8
ALTURA_LINHA = ALTURA // LINHAS

# Cores
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (200, 200, 200)
AMARELO = (255, 255, 0)
CINZA_ESCURO = (50, 50, 50)
VERDE_CLARO = (100, 255, 100)

# Configurações de frequência
FREQUENCIAS = [
    {"nome": "Muito Lento", "valor": 180, "desc": "3 segundos"},
    {"nome": "Lento", "valor": 120, "desc": "2 segundos"},
    {"nome": "Normal", "valor": 60, "desc": "1 segundo"},
    {"nome": "Rápido", "valor": 30, "desc": "0.5 segundos"},
    {"nome": "Muito Rápido", "valor": 15, "desc": "0.25 segundos"}
]

# Posições baseadas no grid (coluna, linha)
POS_GERADOR = (2, 4)      # Coluna 2, Linha 4
POS_COMPUTADOR = (8, 4)   # Coluna 8, Linha 4
POS_UI = (1, 6)           # Coluna 1, Linha 6 (para informações)
POS_INSTRUCOES = (7, 6)   # Coluna 7, Linha 6 (para instruções)

# Tamanhos dos elementos (em células do grid)
TAMANHO_COMPUTADOR = (2, 2)   # 2x2 células
TAMANHO_GERADOR = (2, 2)      # 2x2 células