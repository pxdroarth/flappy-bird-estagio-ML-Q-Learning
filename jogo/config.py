"""Todas as configurações do jogo num lugar só."""
import os

# Pastas (calculadas a partir deste arquivo, então funciona de qualquer lugar)
PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_IMAGENS = os.path.join(PASTA_PROJETO, "assets", "imagens")
PASTA_DADOS = os.path.join(PASTA_PROJETO, "dados")
ARQUIVO_RECORDE = os.path.join(PASTA_DADOS, "recorde.txt")
ARQUIVO_TABELA_Q = os.path.join(PASTA_DADOS, "tabela_q.json")

# Tela
LARGURA, ALTURA = 500, 800
Y_CHAO = 730
FPS = 30
TITULO = "Flappy Bird"

# Física do pássaro
GRAVIDADE = 1.0          # aceleração para baixo por frame
VELOCIDADE_PULO = -10.0  # velocidade ao pular
VELOCIDADE_MAXIMA = 12.0 # limite de queda

# Colunas (obstáculos)
VAO_COLUNA = 200             # espaço entre a coluna de cima e a de baixo
LARGURA_COLUNA = 104
ESPACO_ENTRE_COLUNAS = 300
VARIACAO_MAXIMA_ALTURA = 220 # diferença máxima de altura entre colunas seguidas

# Dificuldade
VELOCIDADE_INICIAL = 5
VELOCIDADE_FINAL = 10
PONTOS_POR_NIVEL = 10        # a cada 10 pontos o jogo acelera 1

# Cores das telas
BRANCO = (255, 255, 255)
AMARELO = (255, 230, 90)
VERMELHO = (255, 90, 90)
