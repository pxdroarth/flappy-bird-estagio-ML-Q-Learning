"""
Ciclo do dia: o fundo passa por dia, tarde e noite com o passar do tempo.

O tempo conta frames desenhados (e não frames de jogo), então o turbo da IA
não faz o céu piscar. Existe um ciclo só para o programa todo, assim o céu
continua de onde estava ao trocar de tela ou reiniciar a partida.
"""
from jogo import config as c
from jogo.imagens import Imagens


class CicloDoDia:
    def __init__(self):
        self.frames = 0

    def avancar(self):
        self.frames += 1

    def estado(self):
        """Retorna (periodo_atual, proximo_periodo, mistura de 0 a 1)."""
        duracao = c.DURACAO_PERIODO * c.FPS
        transicao = c.DURACAO_TRANSICAO * c.FPS
        indice = (self.frames // duracao) % len(c.PERIODOS)
        tempo_no_periodo = self.frames % duracao
        atual = c.PERIODOS[indice]
        proximo = c.PERIODOS[(indice + 1) % len(c.PERIODOS)]
        inicio_transicao = duracao - transicao
        mistura = max(0.0, (tempo_no_periodo - inicio_transicao) / transicao)
        return atual, proximo, mistura

    def desenhar_fundo(self, tela):
        atual, proximo, mistura = self.estado()
        tela.blit(Imagens.fundos[atual], (0, 0))
        if mistura > 0:
            imagem = Imagens.fundos[proximo]
            imagem.set_alpha(int(255 * mistura))
            tela.blit(imagem, (0, 0))
            imagem.set_alpha(None)


ciclo = CicloDoDia()
