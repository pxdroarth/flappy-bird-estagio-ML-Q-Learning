"""Gráficos de desempenho da IA: pontos, taxa de sucesso e exploração."""
from jogo import config as c

JANELA = 100  # partidas usadas nas médias móveis


def media_movel(valores, janela=JANELA):
    resultado, soma = [], 0.0
    for i, v in enumerate(valores):
        soma += v
        if i >= janela:
            soma -= valores[i - janela]
        resultado.append(soma / min(i + 1, janela))
    return resultado


def criar_figura(agente):
    """Monta a figura com 3 gráficos. Retorna None se não houver dados ou matplotlib."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Instale o matplotlib para ver os gráficos: pip install matplotlib")
        return None
    pontos = agente.historico_pontos
    if not pontos:
        print("Ainda não há partidas para mostrar.")
        return None

    partidas = range(1, len(pontos) + 1)
    sucesso = media_movel([100.0 if p >= c.META_SUCESSO else 0.0 for p in pontos])

    figura, (g1, g2, g3) = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    g1.plot(partidas, pontos, alpha=0.25, label="Pontos por partida")
    g1.plot(partidas, media_movel(pontos), label=f"Média móvel ({JANELA})")
    g1.set_ylabel("Pontos")
    g1.set_title("Desempenho da IA")
    g1.legend()

    g2.plot(partidas, sucesso, color="tab:green")
    g2.set_ylabel("Sucesso (%)")
    g2.set_ylim(0, 100)
    g2.set_title(f"Taxa de sucesso: partidas com {c.META_SUCESSO} pontos ou mais")

    if agente.historico_epsilon:
        g3.plot(range(1, len(agente.historico_epsilon) + 1), agente.historico_epsilon,
                color="tab:red")
    g3.set_ylabel("ε")
    g3.set_xlabel("Partida")
    g3.set_title("Taxa de exploração (ε)")

    figura.tight_layout()
    return figura


def salvar_grafico(agente, caminho):
    """Salva o gráfico em PNG (usado no fim do treino sem janela)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
    except ImportError:
        return False
    figura = criar_figura(agente)
    if figura is None:
        return False
    figura.savefig(caminho, dpi=110)
    return True
