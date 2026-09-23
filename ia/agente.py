"""
Agente de Q-Learning.

Mudanças em relação ao projeto base (Stalone Augusto):
  - O original pulava a atualização no frame da morte (if rodando:), então a
    punição de -1000 nunca chegava na tabela Q. Aqui ela chega.
  - Aprendizado de trás pra frente: no fim da partida percorremos os frames do
    último para o primeiro, então a punição da batida alcança os frames que a
    causaram na mesma partida.
  - Se bateu por cima (coluna de cima ou teto), o último pulo leva a culpa.
  - Distância até a coluna medida em frames, então vale em qualquer velocidade.
  - Tabela Q salva em arquivo: o aprendizado continua entre execuções.
"""
import json
import os
import random
from collections import defaultdict

from jogo import config as c
from jogo.entidades import Passaro

RECOMPENSA_VIVO = 1
RECOMPENSA_MORTE = -1000


class AgenteQLearning:
    NAO_PULAR, PULAR = 0, 1

    def __init__(self):
        self.alfa = 0.7      # taxa de aprendizado
        self.gama = 1.0      # peso do futuro
        self.epsilon = 0.0   # exploração (a punição forte já força a explorar)
        self.tabela_q = defaultdict(lambda: [0.0, 0.0])
        self.episodios = 0
        self.recorde = 0
        self.historico_pontos = []
        self.memoria = []    # (estado, acao, proximo_estado) da partida atual

    @staticmethod
    def obter_estado(jogo):
        """Resume a situação do jogo em 3 números (distância x, distância y, velocidade)."""
        coluna = jogo.proxima_coluna()
        distancia = coluna.x + c.LARGURA_COLUNA - Passaro.X
        dx = int(distancia / jogo.velocidade // 3)  # em frames, não em pixels
        dy = int((jogo.passaro.y + Passaro.TAMANHO[1] - coluna.base_vao) // 10)
        dy = max(-40, min(40, dy))
        vel = int(jogo.passaro.velocidade)
        return f"{dx},{dy},{vel}"

    def escolher_acao(self, estado, treinando=True):
        if treinando and random.random() < self.epsilon:
            return self.PULAR if random.random() < 0.1 else self.NAO_PULAR
        q = self.tabela_q[estado]
        return self.PULAR if q[1] > q[0] else self.NAO_PULAR

    def lembrar(self, estado, acao, prox_estado):
        self.memoria.append((estado, acao, prox_estado))

    def aprender_partida(self, morreu, bateu_em_cima):
        """Atualiza a tabela Q com a partida inteira, do fim para o começo."""
        culpou_pulo = False
        for i, (estado, acao, prox) in enumerate(reversed(self.memoria)):
            if morreu and i <= 1:
                r = RECOMPENSA_MORTE
            elif morreu and bateu_em_cima and not culpou_pulo and acao == self.PULAR:
                r = RECOMPENSA_MORTE
                culpou_pulo = True
            else:
                r = RECOMPENSA_VIVO
            terminal = morreu and i == 0
            alvo = r if terminal else r + self.gama * max(self.tabela_q[prox])
            # Q(s,a) <- Q(s,a) + alfa * (alvo - Q(s,a))
            self.tabela_q[estado][acao] += self.alfa * (alvo - self.tabela_q[estado][acao])
        self.memoria = []

    def fim_episodio(self, pontos):
        self.episodios += 1
        self.recorde = max(self.recorde, pontos)
        self.historico_pontos.append(pontos)

    def salvar(self, caminho=c.ARQUIVO_TABELA_Q):
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w") as f:
            json.dump({"tabela_q": dict(self.tabela_q), "episodios": self.episodios,
                       "recorde": self.recorde}, f)

    def carregar(self, caminho=c.ARQUIVO_TABELA_Q):
        if not os.path.exists(caminho):
            return False
        with open(caminho) as f:
            dados = json.load(f)
        self.tabela_q.update(dados["tabela_q"])
        self.episodios = dados.get("episodios", 0)
        self.recorde = dados.get("recorde", 0)
        return True
