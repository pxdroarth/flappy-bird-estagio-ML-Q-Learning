"""Regras do jogo, sem nada de teclado: usado tanto pelo jogador quanto pela IA."""
import pygame

from jogo import config as c
from jogo.entidades import Coluna, Passaro
from jogo.ciclo import ciclo
from jogo.imagens import Imagens


class Jogo:
    def __init__(self, acelerar=True):
        self.acelerar = acelerar
        self.reiniciar()

    def reiniciar(self):
        self.passaro = Passaro()
        self.colunas = [Coluna(c.LARGURA + 100)]
        self.pontos = 0
        self.velocidade = c.VELOCIDADE_INICIAL
        self.deslocamento_chao = 0.0
        self.fim = False

    def proxima_coluna(self):
        for coluna in self.colunas:
            if coluna.x + c.LARGURA_COLUNA > Passaro.X:
                return coluna
        return self.colunas[-1]

    def atualizar_colunas(self):
        """F3 - gera colunas automaticamente. F5 - conta pontos."""
        passou = False
        for coluna in self.colunas:
            coluna.mover(self.velocidade)
            if not coluna.passou and coluna.x + c.LARGURA_COLUNA < Passaro.X:
                coluna.passou = True
                self.pontos += 1
                passou = True
                if self.acelerar:
                    nivel = self.pontos // c.PONTOS_POR_NIVEL
                    self.velocidade = min(c.VELOCIDADE_INICIAL + nivel, c.VELOCIDADE_FINAL)

        self.colunas = [col for col in self.colunas if col.x + c.LARGURA_COLUNA > 0]
        if self.colunas[-1].x < c.LARGURA - c.ESPACO_ENTRE_COLUNAS:
            self.colunas.append(Coluna(c.LARGURA, self.colunas[-1]))
        return passou

    def verificar_colisao(self):
        """F4 - colisão com coluna, chão ou teto."""
        r = self.passaro.retangulo()
        if r.bottom >= c.Y_CHAO or r.top <= 0:
            return True
        return any(r.colliderect(parte)
                   for coluna in self.colunas for parte in coluna.retangulos())

    def passo(self, pular):
        """Avança um frame. Retorna (passou_coluna, morreu)."""
        if pular:
            self.passaro.pular()
        self.passaro.mover()
        passou = self.atualizar_colunas()
        self.deslocamento_chao += self.velocidade
        self.fim = self.verificar_colisao()
        return passou, self.fim

    def desenhar(self, tela):
        ciclo.avancar()
        if Imagens.carregadas:
            ciclo.desenhar_fundo(tela)
        else:
            tela.fill((190, 80, 120))
        for coluna in self.colunas:
            coluna.desenhar(tela)
        if Imagens.carregadas:
            largura = Imagens.chao.get_width()
            x = -(self.deslocamento_chao % largura)
            tela.blit(Imagens.chao, (x, c.Y_CHAO))
            tela.blit(Imagens.chao, (x + largura, c.Y_CHAO))
        else:
            pygame.draw.rect(tela, (150, 100, 60), (0, c.Y_CHAO, c.LARGURA, c.ALTURA - c.Y_CHAO))
        self.passaro.desenhar(tela)
