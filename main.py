"""
Flappy Bird - Projeto de Estágio
Equipe: Pedro Arthur, Leone, Davi Marques, Paulo

Uso:
    python main.py                  -> abre o menu
    python main.py --treinar 20000  -> treina a IA sem janela
"""
import sys

VERSAO_MINIMA = (3, 10)

if sys.version_info < VERSAO_MINIMA:
    sys.exit(f"Python {sys.version.split()[0]} é antigo demais. "
             f"Use Python {VERSAO_MINIMA[0]}.{VERSAO_MINIMA[1]} ou mais novo (recomendado: 3.12).")

try:
    import pygame
except ImportError:
    sys.exit("O pygame não está instalado. Rode, dentro da pasta do projeto:\n"
             "    python -m pip install -r requirements.txt\n"
             "Diagnóstico completo: python ferramentas/verificar_ambiente.py")

from jogo import config as c
from jogo.imagens import Imagens
from jogo.telas import menu, modo_ia, modo_jogador
from ia.treino import treinar_sem_janela


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--treinar":
        treinar_sem_janela(int(sys.argv[2]))
        return

    pygame.init()
    tela = pygame.display.set_mode((c.LARGURA, c.ALTURA))
    pygame.display.set_caption(c.TITULO)
    Imagens.carregar()
    relogio = pygame.time.Clock()

    while True:
        escolha = menu(tela, relogio)
        if escolha is None:
            break
        if escolha == "jogador":
            continuar = modo_jogador(tela, relogio)
        else:
            continuar = modo_ia(tela, relogio)
        if not continuar:
            break
    pygame.quit()


if __name__ == "__main__":
    main()
