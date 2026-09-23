"""
Flappy Bird - Projeto de Estágio
Equipe: Pedro Arthur, Leone, Davi Marques, Paulo

Baseado em: github.com/HardWareGCR/FlappyBirdQLearning-01656165-StaloneAugusto
(Stalone Augusto), com o modo jogador adicionado e correções no Q-Learning.

Modos:
  1 - Jogador: você controla o pássaro (ESPAÇO, SETA PRA CIMA ou clique)
  2 - IA: o pássaro aprende sozinho com Q-Learning

Funcionalidades exigidas:
  F1 - Subir ao clicar/tocar ........ Passaro.pular() + tratar_eventos_jogador()
  F2 - Gravidade .................... Passaro.mover()
  F3 - Gerar canos automaticamente .. Jogo.atualizar_canos()
  F4 - Colisão com cano ou chão ..... Jogo.verificar_colisao()
  F5 - Contador de pontos ........... Jogo.atualizar_canos() (cano ultrapassado)

Uso:
  python flappy_bird.py                  -> abre o menu
  python flappy_bird.py --treinar 3000   -> treina a IA sem janela (rápido)
"""
import json
import os
import random
import sys
from collections import defaultdict

import pygame

# ----------------------------------------------------------------------------
# Configurações
# ----------------------------------------------------------------------------
LARGURA, ALTURA = 500, 800
Y_CHAO = 730
FPS = 30

GRAVIDADE = 1.0          # aceleração para baixo por frame
VELOCIDADE_PULO = -10.0  # velocidade ao pular
VELOCIDADE_MAXIMA = 12.0 # limite de queda

VAO_CANO = 200           # espaço entre o cano de cima e o de baixo
LARGURA_CANO = 104
ESPACO_ENTRE_CANOS = 300
VELOCIDADE_CANO_INICIAL = 5
VELOCIDADE_CANO_MAXIMA = 10
PONTOS_POR_NIVEL = 10    # a cada 10 pontos o jogo acelera 1 (modo jogador)

ARQUIVO_RECORDE = "recorde.txt"
ARQUIVO_TABELA_Q = "tabela_q.json"
PASTA_IMGS = "imgs"


# ----------------------------------------------------------------------------
# Imagens (usa a pasta imgs do projeto base se existir, senão desenha formas)
# ----------------------------------------------------------------------------
class Imagens:
    carregadas = False
    passaro = []
    cano = None
    chao = None
    fundo = None

    @classmethod
    def carregar(cls):
        try:
            def img(nome):
                return pygame.transform.scale2x(
                    pygame.image.load(os.path.join(PASTA_IMGS, nome)).convert_alpha())
            cls.passaro = [img("bird1.png"), img("bird2.png"), img("bird3.png")]
            cls.cano = img("pipe.png")
            cls.chao = img("base.png")
            cls.fundo = img("bg.png")
            cls.carregadas = True
        except (FileNotFoundError, pygame.error):
            cls.carregadas = False  # segue com formas simples


# ----------------------------------------------------------------------------
# Entidades
# ----------------------------------------------------------------------------
class Passaro:
    X = 120
    TAMANHO = (68, 48)  # mesmo tamanho da imagem do pássaro

    def __init__(self):
        self.y = 350.0
        self.velocidade = 0.0
        self.quadro = 0

    # F1 - subir ao clicar
    def pular(self):
        self.velocidade = VELOCIDADE_PULO

    # F2 - gravidade
    def mover(self):
        self.velocidade = min(self.velocidade + GRAVIDADE, VELOCIDADE_MAXIMA)
        self.y += self.velocidade

    def retangulo(self):
        margem = 6  # deixa a colisão um pouco mais justa que a imagem
        return pygame.Rect(self.X + margem, int(self.y) + margem,
                           self.TAMANHO[0] - 2 * margem, self.TAMANHO[1] - 2 * margem)

    def desenhar(self, tela):
        self.quadro = (self.quadro + 1) % 15
        angulo = max(-90, min(25, -self.velocidade * 4))
        if Imagens.carregadas:
            imagem = Imagens.passaro[self.quadro // 5]
            girada = pygame.transform.rotate(imagem, angulo)
            centro = (self.X + self.TAMANHO[0] // 2, int(self.y) + self.TAMANHO[1] // 2)
            tela.blit(girada, girada.get_rect(center=centro))
        else:
            pygame.draw.ellipse(tela, (250, 210, 40), (self.X, int(self.y), *self.TAMANHO))
            pygame.draw.circle(tela, (0, 0, 0), (self.X + 44, int(self.y) + 14), 4)


class Cano:
    VARIACAO_MAXIMA = 220  # diferença máxima de altura para o cano anterior

    def __init__(self, x, anterior=None):
        self.x = float(x)
        minimo, maximo = 80, Y_CHAO - VAO_CANO - 80
        if anterior is not None:
            minimo = max(minimo, anterior.topo_vao - self.VARIACAO_MAXIMA)
            maximo = min(maximo, anterior.topo_vao + self.VARIACAO_MAXIMA)
        self.topo_vao = random.randint(minimo, maximo)
        self.passou = False

    @property
    def base_vao(self):
        return self.topo_vao + VAO_CANO

    def mover(self, velocidade):
        self.x -= velocidade

    def retangulos(self):
        cima = pygame.Rect(int(self.x), 0, LARGURA_CANO, self.topo_vao)
        baixo = pygame.Rect(int(self.x), self.base_vao, LARGURA_CANO, Y_CHAO - self.base_vao)
        return cima, baixo

    def desenhar(self, tela):
        if Imagens.carregadas:
            img = Imagens.cano
            tela.blit(pygame.transform.flip(img, False, True),
                      (self.x, self.topo_vao - img.get_height()))
            tela.blit(img, (self.x, self.base_vao))
        else:
            for r in self.retangulos():
                pygame.draw.rect(tela, (80, 190, 60), r)
                pygame.draw.rect(tela, (40, 110, 30), r, 3)


# ----------------------------------------------------------------------------
# Lógica do jogo (sem desenho: usada pelo jogador e pela IA)
# ----------------------------------------------------------------------------
class Jogo:
    def __init__(self, acelerar=True):
        self.acelerar = acelerar
        self.reiniciar()

    def reiniciar(self):
        self.passaro = Passaro()
        self.canos = [Cano(LARGURA + 100)]
        self.pontos = 0
        self.velocidade = VELOCIDADE_CANO_INICIAL
        self.chao_x = 0.0
        self.fim = False

    def proximo_cano(self):
        for cano in self.canos:
            if cano.x + LARGURA_CANO > Passaro.X:
                return cano
        return self.canos[-1]

    # F3 e F5 - gerar canos e contar pontos
    def atualizar_canos(self):
        passou_cano = False
        for cano in self.canos:
            cano.mover(self.velocidade)
            if not cano.passou and cano.x + LARGURA_CANO < Passaro.X:
                cano.passou = True
                self.pontos += 1
                passou_cano = True
                if self.acelerar:
                    nivel = self.pontos // PONTOS_POR_NIVEL
                    self.velocidade = min(VELOCIDADE_CANO_INICIAL + nivel,
                                          VELOCIDADE_CANO_MAXIMA)

        self.canos = [c for c in self.canos if c.x + LARGURA_CANO > 0]
        if self.canos[-1].x < LARGURA - ESPACO_ENTRE_CANOS:
            self.canos.append(Cano(LARGURA, self.canos[-1]))
        return passou_cano

    # F4 - colisão com cano, chão ou teto
    def verificar_colisao(self):
        r = self.passaro.retangulo()
        if r.bottom >= Y_CHAO or r.top <= 0:
            return True
        return any(r.colliderect(parte)
                   for cano in self.canos for parte in cano.retangulos())

    def passo(self, pular):
        """Avança um frame. Retorna (passou_cano, morreu)."""
        if pular:
            self.passaro.pular()
        self.passaro.mover()
        passou = self.atualizar_canos()
        self.chao_x += self.velocidade
        self.fim = self.verificar_colisao()
        return passou, self.fim

    def desenhar(self, tela):
        if Imagens.carregadas:
            tela.blit(Imagens.fundo, (0, 0))
        else:
            tela.fill((110, 195, 230))
        for cano in self.canos:
            cano.desenhar(tela)
        if Imagens.carregadas:
            largura = Imagens.chao.get_width()
            x = -(self.chao_x % largura)
            tela.blit(Imagens.chao, (x, Y_CHAO))
            tela.blit(Imagens.chao, (x + largura, Y_CHAO))
        else:
            pygame.draw.rect(tela, (220, 200, 120), (0, Y_CHAO, LARGURA, ALTURA - Y_CHAO))
        self.passaro.desenhar(tela)


# ----------------------------------------------------------------------------
# Agente Q-Learning
# ----------------------------------------------------------------------------
class AgenteQLearning:
    """
    Mudanças em relação ao projeto base:
      - O original pulava a atualização no frame da morte (if rodando:), então a
        punição de -1000 nunca chegava na tabela Q. Aqui ela chega.
      - Aprendizado de trás pra frente: no fim da partida percorremos os frames
        do último para o primeiro. Assim a punição da batida se espalha pelos
        frames que a causaram na mesma partida, em vez de levar centenas de
        partidas para "descer" frame a frame.
      - Se bateu por cima (cano de cima ou teto), o último pulo leva a culpa.
      - Distância ao cano medida em frames, então funciona em qualquer velocidade.
      - Tabela Q salva em arquivo: o aprendizado continua entre execuções.
    """
    NAO_PULAR, PULAR = 0, 1

    def __init__(self):
        self.alfa = 0.7
        self.gama = 1.0
        self.epsilon = 0.0   # a punição forte já força a exploração
        self.tabela_q = defaultdict(lambda: [0.0, 0.0])
        self.episodios = 0
        self.recorde = 0
        self.historico_pontos = []
        self.memoria = []    # (estado, acao, proximo_estado) da partida atual

    @staticmethod
    def obter_estado(jogo):
        cano = jogo.proximo_cano()
        # distância medida em frames até o cano (não em pixels), assim o que ele
        # aprende em uma velocidade vale para as outras
        dx = int((cano.x + LARGURA_CANO - Passaro.X) / jogo.velocidade // 3)
        dy = int((jogo.passaro.y + Passaro.TAMANHO[1] - cano.base_vao) // 10)
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
            self.tabela_q[estado][acao] += self.alfa * (alvo - self.tabela_q[estado][acao])
        self.memoria = []

    def fim_episodio(self, pontos):
        self.episodios += 1
        self.recorde = max(self.recorde, pontos)
        self.historico_pontos.append(pontos)

    def salvar(self, caminho=ARQUIVO_TABELA_Q):
        with open(caminho, "w") as f:
            json.dump({"tabela_q": dict(self.tabela_q), "episodios": self.episodios,
                       "recorde": self.recorde}, f)

    def carregar(self, caminho=ARQUIVO_TABELA_Q):
        if not os.path.exists(caminho):
            return False
        with open(caminho) as f:
            dados = json.load(f)
        self.tabela_q.update(dados["tabela_q"])
        self.episodios = dados.get("episodios", 0)
        self.recorde = dados.get("recorde", 0)
        return True


RECOMPENSA_VIVO = 1
RECOMPENSA_MORTE = -1000
LIMITE_PONTOS_TREINO = 1000  # evita partida infinita quando ele "zera" o jogo


def bateu_em_cima(jogo):
    cano = jogo.proximo_cano()
    return jogo.passaro.y + Passaro.TAMANHO[1] / 2 < cano.topo_vao + VAO_CANO / 2


def passo_ia(agente, jogo, treinando=True):
    """Um frame da IA. Retorna True se a partida acabou."""
    estado = agente.obter_estado(jogo)
    acao = agente.escolher_acao(estado, treinando)
    jogo.passo(acao == agente.PULAR)
    if treinando:
        agente.lembrar(estado, acao, agente.obter_estado(jogo))
    acabou = jogo.fim or jogo.pontos >= LIMITE_PONTOS_TREINO
    if acabou:
        if treinando:
            agente.aprender_partida(jogo.fim, jogo.fim and bateu_em_cima(jogo))
        agente.fim_episodio(jogo.pontos)
    return acabou


def jogar_episodio_ia(agente, jogo, treinando=True):
    """Roda uma partida completa sem desenhar. Retorna os pontos."""
    jogo.reiniciar()
    agente.memoria = []
    while not passo_ia(agente, jogo, treinando):
        pass
    return jogo.pontos


# ----------------------------------------------------------------------------
# Telas
# ----------------------------------------------------------------------------
def texto(tela, msg, tamanho, y, cor=(255, 255, 255), x=None):
    fonte = pygame.font.SysFont("arial", tamanho, bold=True)
    sombra = fonte.render(msg, True, (0, 0, 0))
    superficie = fonte.render(msg, True, cor)
    pos_x = (LARGURA - superficie.get_width()) // 2 if x is None else x
    tela.blit(sombra, (pos_x + 2, y + 2))
    tela.blit(superficie, (pos_x, y))


def ler_recorde():
    try:
        with open(ARQUIVO_RECORDE) as f:
            return int(f.read().strip() or 0)
    except (FileNotFoundError, ValueError):
        return 0


def salvar_recorde(valor):
    with open(ARQUIVO_RECORDE, "w") as f:
        f.write(str(valor))


def menu(tela, relogio):
    jogo_fundo = Jogo()
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return None
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    return "jogador"
                if evento.key == pygame.K_2:
                    return "ia"
                if evento.key == pygame.K_ESCAPE:
                    return None
        jogo_fundo.desenhar(tela)
        texto(tela, "FLAPPY BIRD", 60, 180)
        texto(tela, "1 - Jogar", 36, 330)
        texto(tela, "2 - Ver a IA aprender", 36, 390)
        texto(tela, "ESC - Sair", 28, 470)
        texto(tela, f"Recorde: {ler_recorde()}", 28, 560, (255, 230, 90))
        pygame.display.update()
        relogio.tick(FPS)


def tratar_eventos_jogador():
    """Retorna 'sair', 'pular' ou None. (F1: clique/toque/tecla)"""
    pular = False
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            return "sair"
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return "menu"
            if evento.key in (pygame.K_SPACE, pygame.K_UP):
                pular = True
        if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pular = True
    return "pular" if pular else None


def modo_jogador(tela, relogio):
    jogo = Jogo(acelerar=True)
    recorde = ler_recorde()
    comecou = False

    while True:
        comando = tratar_eventos_jogador()
        if comando == "sair":
            return False
        if comando == "menu":
            return True

        if not jogo.fim:
            if comando == "pular":
                comecou = True
            if comecou:
                jogo.passo(comando == "pular")
                if jogo.fim and jogo.pontos > recorde:
                    recorde = jogo.pontos
                    salvar_recorde(recorde)
        elif comando == "pular":
            jogo.reiniciar()
            comecou = False

        jogo.desenhar(tela)
        texto(tela, str(jogo.pontos), 64, 40)
        if not comecou and not jogo.fim:
            texto(tela, "Clique ou ESPAÇO para voar", 28, 520)
        if jogo.fim:
            texto(tela, "GAME OVER", 60, 250, (255, 90, 90))
            texto(tela, f"Pontos: {jogo.pontos}   Recorde: {recorde}", 30, 340)
            texto(tela, "Clique ou ESPAÇO para jogar de novo", 24, 420)
            texto(tela, "ESC para voltar ao menu", 24, 460)
        pygame.display.update()
        relogio.tick(FPS)


def modo_ia(tela, relogio):
    agente = AgenteQLearning()
    agente.carregar()
    jogo = Jogo(acelerar=True)
    turbo = False
    mostrar_info = True

    def sair():
        agente.salvar()
        return True

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                agente.salvar()
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return sair()
                if evento.key == pygame.K_t:
                    turbo = not turbo
                if evento.key == pygame.K_i:
                    mostrar_info = not mostrar_info
                if evento.key == pygame.K_g:
                    mostrar_graficos(agente)

        if turbo:
            # treina vários episódios sem desenhar cada frame
            for _ in range(20):
                jogar_episodio_ia(agente, jogo)
            if agente.episodios % 200 < 20:
                agente.salvar()
            jogo.desenhar(tela)
        else:
            if jogo.fim:
                jogo.reiniciar()
                agente.memoria = []
            if passo_ia(agente, jogo):
                jogo.reiniciar()
            jogo.desenhar(tela)
            texto(tela, str(jogo.pontos), 64, 40)

        if mostrar_info:
            ultimos = agente.historico_pontos[-100:]
            media = sum(ultimos) / len(ultimos) if ultimos else 0
            infos = [f"Episódio: {agente.episodios}", f"Recorde IA: {agente.recorde}",
                     f"Média (100): {media:.1f}",
                     f"Estados: {len(agente.tabela_q)}", f"Vel. canos: {jogo.velocidade}",
                     "T turbo | G gráfico | I info | ESC menu"]
            if turbo:
                infos.insert(0, "TURBO (treinando rápido)")
            for i, linha in enumerate(infos):
                texto(tela, linha, 20, 120 + i * 26, x=10)
        pygame.display.update()
        relogio.tick(FPS)


def mostrar_graficos(agente):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Instale o matplotlib para ver os gráficos: pip install matplotlib")
        return
    pontos = agente.historico_pontos
    if not pontos:
        return
    janela = 50
    media = [sum(pontos[max(0, i - janela + 1):i + 1]) / min(i + 1, janela)
             for i in range(len(pontos))]
    plt.figure(figsize=(10, 5))
    plt.plot(pontos, alpha=0.35, label="Pontos por episódio")
    plt.plot(media, label=f"Média móvel ({janela})")
    plt.xlabel("Episódio (desta sessão)")
    plt.ylabel("Pontos")
    plt.title("Evolução da IA")
    plt.legend()
    plt.tight_layout()
    plt.show()


# ----------------------------------------------------------------------------
# Treino sem janela
# ----------------------------------------------------------------------------
def treinar_sem_janela(n_episodios):
    agente = AgenteQLearning()
    if agente.carregar():
        print(f"Continuando treino: {agente.episodios} episódios já feitos.")
    jogo = Jogo(acelerar=True)
    for i in range(1, n_episodios + 1):
        jogar_episodio_ia(agente, jogo)
        if i % 250 == 0:
            ultimos = agente.historico_pontos[-250:]
            print(f"Episódio {agente.episodios:6d} | média {sum(ultimos)/len(ultimos):7.1f} | "
                  f"máx {max(ultimos):4d} | recorde {agente.recorde:4d} | "
                  f"estados {len(agente.tabela_q)}")
        if i % 1000 == 0:
            agente.salvar()  # salva no meio, se parar com Ctrl+C não perde tudo
    agente.salvar()
    print(f"Tabela Q salva em {ARQUIVO_TABELA_Q}")


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--treinar":
        treinar_sem_janela(int(sys.argv[2]))
        return

    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Flappy Bird")
    Imagens.carregar()
    relogio = pygame.time.Clock()

    while True:
        escolha = menu(tela, relogio)
        if escolha is None:
            break
        continuar = modo_jogador(tela, relogio) if escolha == "jogador" else modo_ia(tela, relogio)
        if not continuar:
            break
    pygame.quit()


if __name__ == "__main__":
    main()
