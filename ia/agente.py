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
  - Exploração (epsilon) começa em EPSILON_INICIAL e cai a cada partida,
    com histórico salvo para os gráficos de exploração e desempenho.
"""
import json
import os
import random
from collections import defaultdict

from jogo import config as c
from jogo.entidades import Passaro

RECOMPENSA_VIVO = 1
RECOMPENSA_MORTE = -1000

# Muda sempre que o formato do estado mudar. Tabela de outro formato não serve.
FORMATO_TABELA = 2  # 1 = v1 a v3 (3 números), 2 = v4 em diante (4 números)

EPSILON_INICIAL = 0.3     # 30% das decisões aleatórias no começo
EPSILON_MINIMO = 0.0      # no fim ele só usa o que aprendeu
DECAIMENTO_EPSILON = 0.9995  # a cada partida: epsilon = epsilon * 0.9995


class AgenteQLearning:
    NAO_PULAR, PULAR = 0, 1

    def __init__(self):
        self.alfa = 0.7      # taxa de aprendizado
        self.gama = 1.0      # peso do futuro
        self.epsilon = EPSILON_INICIAL  # taxa de exploração
        self.tabela_q = defaultdict(lambda: [0.0, 0.0])
        self.episodios = 0
        self.recorde = 0
        self.historico_pontos = []
        self.historico_epsilon = []
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
        # diferença de altura para a coluna seguinte: ajuda a se preparar
        # antes de sair do vão (subir ou descer para a próxima)
        seguinte = jogo.coluna_seguinte()
        dprox = 0 if seguinte is None else int((seguinte.topo_vao - coluna.topo_vao) // 60)
        return f"{dx},{dy},{vel},{dprox}"

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
        self.historico_epsilon.append(self.epsilon)
        self.epsilon = max(EPSILON_MINIMO, self.epsilon * DECAIMENTO_EPSILON)

    def media_recente(self, n=100):
        ultimos = self.historico_pontos[-n:]
        return sum(ultimos) / len(ultimos) if ultimos else 0.0

    def taxa_sucesso(self, n=100):
        """% das últimas n partidas que chegaram à meta de pontos (c.META_SUCESSO)."""
        ultimos = self.historico_pontos[-n:]
        if not ultimos:
            return 0.0
        return 100 * sum(p >= c.META_SUCESSO for p in ultimos) / len(ultimos)

    def salvar(self, caminho=c.ARQUIVO_TABELA_Q):
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w") as f:
            json.dump({"formato": FORMATO_TABELA, "tabela_q": dict(self.tabela_q), "episodios": self.episodios,
                       "recorde": self.recorde, "epsilon": self.epsilon,
                       "historico_pontos": self.historico_pontos,
                       "historico_epsilon": self.historico_epsilon}, f)

    def carregar(self, caminho=c.ARQUIVO_TABELA_Q):
        if not os.path.exists(caminho):
            return False
        try:
            with open(caminho) as f:
                dados = json.load(f)
        except (json.JSONDecodeError, OSError):
            return self._descartar(caminho, "o arquivo está corrompido")
        if dados.get("formato") != FORMATO_TABELA:
            return self._descartar(caminho, "é de uma versão anterior do jogo")
        self.tabela_q.update(dados["tabela_q"])
        self.episodios = dados.get("episodios", 0)
        self.recorde = dados.get("recorde", 0)
        self.epsilon = dados.get("epsilon", self.epsilon)
        self.historico_pontos = dados.get("historico_pontos", [])
        self.historico_epsilon = dados.get("historico_epsilon", [])
        return True

    @staticmethod
    def _descartar(caminho, motivo):
        """Guarda a tabela incompatível como .antigo e começa um treino novo."""
        backup = caminho + ".antigo"
        os.replace(caminho, backup)
        print(f"Tabela Q ignorada porque {motivo}. Cópia guardada em {backup}. "
              "A IA vai começar a aprender do zero.")
        return False
