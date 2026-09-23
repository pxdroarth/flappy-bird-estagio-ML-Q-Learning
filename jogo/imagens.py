"""Carrega as imagens de assets/imagens (geradas por ferramentas/gerar_imagens.py)."""
import os

import pygame

from jogo.config import PASTA_IMAGENS, PERIODOS


class Imagens:
    carregadas = False
    passaro = []
    coluna = None
    chao = None
    fundos = {}  # {'dia': Surface, 'tarde': Surface, 'noite': Surface}

    @classmethod
    def carregar(cls):
        """Tenta carregar as imagens. Se faltar alguma, o jogo desenha formas simples."""
        try:
            def abrir(nome, transparente=True):
                imagem = pygame.image.load(os.path.join(PASTA_IMAGENS, nome))
                imagem = imagem.convert_alpha() if transparente else imagem.convert()
                return pygame.transform.scale2x(imagem)

            cls.passaro = [abrir(f"passaro_{i}.png") for i in (1, 2, 3)]
            cls.coluna = abrir("coluna.png")
            cls.chao = abrir("chao.png")
            # fundo sem transparência, assim dá para usar set_alpha na transição
            cls.fundos = {p: abrir(f"fundo_{p}.png", transparente=False) for p in PERIODOS}
            cls.carregadas = True
        except (FileNotFoundError, pygame.error):
            print("Imagens não encontradas. Rode: python ferramentas/gerar_imagens.py")
            cls.carregadas = False
