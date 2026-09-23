"""Telas do jogo: menu, modo jogador e modo IA."""
import os

import pygame

from jogo import config as c
from jogo.mundo import Jogo
from ia.agente import AgenteQLearning
from ia.treino import jogar_partida, passo_ia


def texto(tela, msg, tamanho, y, cor=c.BRANCO, x=None):
    fonte = pygame.font.SysFont("arial", tamanho, bold=True)
    sombra = fonte.render(msg, True, (0, 0, 0))
    superficie = fonte.render(msg, True, cor)
    pos_x = (c.LARGURA - superficie.get_width()) // 2 if x is None else x
    tela.blit(sombra, (pos_x + 2, y + 2))
    tela.blit(superficie, (pos_x, y))


def ler_recorde():
    try:
        with open(c.ARQUIVO_RECORDE) as f:
            return int(f.read().strip() or 0)
    except (FileNotFoundError, ValueError):
        return 0


def salvar_recorde(valor):
    os.makedirs(c.PASTA_DADOS, exist_ok=True)
    with open(c.ARQUIVO_RECORDE, "w") as f:
        f.write(str(valor))


# ----------------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------------
def menu(tela, relogio):
    """Retorna 'jogador', 'ia' ou None (sair)."""
    fundo = Jogo()
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
        fundo.desenhar(tela)
        texto(tela, "FLAPPY BIRD", 60, 180)
        texto(tela, "1 - Jogar", 36, 330)
        texto(tela, "2 - Ver a IA aprender", 36, 390)
        texto(tela, "ESC - Sair", 28, 470)
        texto(tela, f"Recorde: {ler_recorde()}", 28, 560, c.AMARELO)
        pygame.display.update()
        relogio.tick(c.FPS)


# ----------------------------------------------------------------------------
# Modo jogador
# ----------------------------------------------------------------------------
def ler_comando_jogador():
    """Retorna 'sair', 'menu', 'pular' ou None. (F1: clique, toque ou tecla)"""
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
    """Retorna False se o usuário fechou a janela, True para voltar ao menu."""
    jogo = Jogo(acelerar=True)
    recorde = ler_recorde()
    comecou = False

    while True:
        comando = ler_comando_jogador()
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
            texto(tela, "GAME OVER", 60, 250, c.VERMELHO)
            texto(tela, f"Pontos: {jogo.pontos}   Recorde: {recorde}", 30, 340)
            texto(tela, "Clique ou ESPAÇO para jogar de novo", 24, 420)
            texto(tela, "ESC para voltar ao menu", 24, 460)
        pygame.display.update()
        relogio.tick(c.FPS)


# ----------------------------------------------------------------------------
# Modo IA
# ----------------------------------------------------------------------------
def modo_ia(tela, relogio):
    """Retorna False se o usuário fechou a janela, True para voltar ao menu."""
    agente = AgenteQLearning()
    agente.carregar()
    jogo = Jogo(acelerar=True)
    turbo = False
    mostrar_info = True

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                agente.salvar()
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    agente.salvar()
                    return True
                if evento.key == pygame.K_t:
                    turbo = not turbo
                if evento.key == pygame.K_i:
                    mostrar_info = not mostrar_info
                if evento.key == pygame.K_g:
                    mostrar_graficos(agente)

        if turbo:
            for _ in range(20):  # várias partidas sem desenhar cada frame
                jogar_partida(agente, jogo)
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
            desenhar_info_ia(tela, agente, jogo, turbo)
        pygame.display.update()
        relogio.tick(c.FPS)


def desenhar_info_ia(tela, agente, jogo, turbo):
    linhas = [f"Partida: {agente.episodios}",
              f"Recorde IA: {agente.recorde}",
              f"Média (100): {agente.media_recente():.1f}",
              f"Sucesso (>= {c.META_SUCESSO} pts): {agente.taxa_sucesso():.0f}%",
              f"Exploração (ε): {agente.epsilon:.4f}",
              f"Estados: {len(agente.tabela_q)}",
              f"Velocidade: {jogo.velocidade}",
              "T turbo | G gráfico | I info | ESC menu"]
    if turbo:
        linhas.insert(0, "TURBO (treinando rápido)")
    for i, linha in enumerate(linhas):
        texto(tela, linha, 20, 120 + i * 26, x=10)


def mostrar_graficos(agente):
    from ia.graficos import criar_figura
    figura = criar_figura(agente)
    if figura is None:
        return
    import matplotlib.pyplot as plt
    plt.show()
