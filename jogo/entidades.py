"""Objetos do jogo: o pássaro e as colunas."""
import random

import pygame

from jogo import config as c
from jogo.imagens import Imagens


class Passaro:
    X = 120
    TAMANHO = (68, 48)  # mesmo tamanho da imagem ampliada
    MARGEM_COLISAO = 6  # deixa a colisão um pouco mais justa que a imagem

    def __init__(self):
        self.y = 350.0
        self.velocidade = 0.0
        self.quadro = 0

    def pular(self):
        """F1 - subir ao clicar/tocar."""
        self.velocidade = c.VELOCIDADE_PULO

    def mover(self):
        """F2 - gravidade puxando para baixo."""
        self.velocidade = min(self.velocidade + c.GRAVIDADE, c.VELOCIDADE_MAXIMA)
        self.y += self.velocidade

    def retangulo(self):
        m = self.MARGEM_COLISAO
        return pygame.Rect(self.X + m, int(self.y) + m,
                           self.TAMANHO[0] - 2 * m, self.TAMANHO[1] - 2 * m)

    def desenhar(self, tela):
        self.quadro = (self.quadro + 1) % 15
        angulo = max(-90, min(25, -self.velocidade * 4))
        centro = (self.X + self.TAMANHO[0] // 2, int(self.y) + self.TAMANHO[1] // 2)
        if Imagens.carregadas:
            imagem = Imagens.passaro[self.quadro // 5]
            girada = pygame.transform.rotate(imagem, angulo)
            tela.blit(girada, girada.get_rect(center=centro))
        else:
            pygame.draw.ellipse(tela, (70, 130, 220), (self.X, int(self.y), *self.TAMANHO))


class Coluna:
    def __init__(self, x, anterior=None):
        self.x = float(x)
        minimo, maximo = 80, c.Y_CHAO - c.VAO_COLUNA - 80
        if anterior is not None:
            minimo = max(minimo, anterior.topo_vao - c.VARIACAO_MAXIMA_ALTURA)
            maximo = min(maximo, anterior.topo_vao + c.VARIACAO_MAXIMA_ALTURA)
        self.topo_vao = random.randint(minimo, maximo)
        self.passou = False

    @property
    def base_vao(self):
        return self.topo_vao + c.VAO_COLUNA

    def mover(self, velocidade):
        self.x -= velocidade

    def retangulos(self):
        cima = pygame.Rect(int(self.x), 0, c.LARGURA_COLUNA, self.topo_vao)
        baixo = pygame.Rect(int(self.x), self.base_vao, c.LARGURA_COLUNA, c.Y_CHAO - self.base_vao)
        return cima, baixo

    def desenhar(self, tela):
        if Imagens.carregadas:
            img = Imagens.coluna
            tela.blit(pygame.transform.flip(img, False, True),
                      (self.x, self.topo_vao - img.get_height()))
            tela.blit(img, (self.x, self.base_vao))
        else:
            for r in self.retangulos():
                pygame.draw.rect(tela, (120, 130, 150), r)
