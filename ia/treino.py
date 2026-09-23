"""Rotinas que colocam o agente para jogar e aprender."""
import os

from jogo import config as c
from jogo.entidades import Passaro
from jogo.mundo import Jogo
from ia.agente import AgenteQLearning

LIMITE_PONTOS = 1000  # encerra a partida se ele "zerar" o jogo, senão nunca acaba


def bateu_em_cima(jogo):
    coluna = jogo.proxima_coluna()
    return jogo.passaro.y + Passaro.TAMANHO[1] / 2 < coluna.topo_vao + c.VAO_COLUNA / 2


def passo_ia(agente, jogo, treinando=True):
    """Um frame da IA. Retorna True se a partida acabou."""
    estado = agente.obter_estado(jogo)
    acao = agente.escolher_acao(estado, treinando)
    jogo.passo(acao == agente.PULAR)
    if treinando:
        agente.lembrar(estado, acao, agente.obter_estado(jogo))
    acabou = jogo.fim or jogo.pontos >= LIMITE_PONTOS
    if acabou:
        if treinando:
            agente.aprender_partida(jogo.fim, jogo.fim and bateu_em_cima(jogo))
        agente.fim_episodio(jogo.pontos)
    return acabou


def jogar_partida(agente, jogo, treinando=True):
    """Roda uma partida completa sem desenhar. Retorna os pontos."""
    jogo.reiniciar()
    agente.memoria = []
    while not passo_ia(agente, jogo, treinando):
        pass
    return jogo.pontos


def treinar_sem_janela(n_partidas):
    agente = AgenteQLearning()
    if agente.carregar():
        print(f"Continuando treino: {agente.episodios} partidas já feitas.")
    jogo = Jogo(acelerar=True)
    for i in range(1, n_partidas + 1):
        jogar_partida(agente, jogo)
        if i % 250 == 0:
            print(f"Partida {agente.episodios:6d} | média {agente.media_recente(250):7.1f} | "
                  f"sucesso {agente.taxa_sucesso(250):5.1f}% | recorde {agente.recorde:4d} | "
                  f"exploração {agente.epsilon:.4f} | estados {len(agente.tabela_q)}")
        if i % 1000 == 0:
            agente.salvar()  # se parar com Ctrl+C não perde tudo
    agente.salvar()
    print(f"Tabela Q salva em {c.ARQUIVO_TABELA_Q}")

    from ia.graficos import salvar_grafico
    caminho_grafico = os.path.join(c.PASTA_DADOS, "grafico_treino.png")
    if salvar_grafico(agente, caminho_grafico):
        print(f"Gráfico salvo em {caminho_grafico}")
