"""
Gera todas as imagens do jogo por código (pixel art) e salva em assets/imagens.

As imagens são desenhadas em tamanho pequeno e o jogo amplia 2x ao carregar,
por isso ficam com cara de pixel art.

Uso (a partir da pasta do projeto):
    python ferramentas/gerar_imagens.py

Para mudar o visual, altere as cores em PALETA ou as funções de desenho.
"""
import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # não precisa abrir janela
import pygame

PASTA_SAIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "assets", "imagens")

PALETA = {
    # pássaro
    "corpo": (70, 130, 220),
    "corpo_escuro": (40, 80, 160),
    "barriga": (200, 225, 255),
    "asa": (30, 60, 130),
    "bico": (255, 170, 40),
    "olho": (255, 255, 255),
    "pupila": (20, 20, 30),
    "contorno": (20, 25, 50),
    # coluna (obstáculo)
    "coluna": (120, 130, 150),
    "coluna_claro": (175, 185, 200),
    "coluna_escuro": (70, 78, 95),
    "faixa": (230, 120, 60),
    "parafuso": (50, 55, 70),
    # céu e cenário
    "ceu_topo": (40, 30, 90),
    "ceu_meio": (190, 80, 120),
    "ceu_baixo": (250, 170, 90),
    "sol": (255, 225, 140),
    "morro_longe": (120, 60, 110),
    "morro_perto": (70, 40, 85),
    "estrela": (255, 245, 220),
    # chão
    "grama": (60, 150, 80),
    "grama_escura": (35, 100, 55),
    "terra": (150, 100, 60),
    "terra_escura": (110, 70, 40),
    "pedra": (175, 155, 130),
}


def nova_superficie(largura, altura):
    return pygame.Surface((largura, altura), pygame.SRCALPHA)


# ----------------------------------------------------------------------------
# Pássaro 34x24 (3 quadros: asa em cima, no meio e embaixo)
# ----------------------------------------------------------------------------
def desenhar_passaro(posicao_asa):
    s = nova_superficie(34, 24)
    c = PALETA

    # topete (três penas)
    for i, (x, y) in enumerate([(9, 1), (12, 0), (15, 2)]):
        pygame.draw.polygon(s, c["corpo_escuro"], [(x, y + 5), (x + 2, y), (x + 4, y + 5)])

    # corpo e barriga
    pygame.draw.ellipse(s, c["contorno"], (2, 4, 28, 19))
    pygame.draw.ellipse(s, c["corpo"], (3, 5, 26, 17))
    pygame.draw.ellipse(s, c["barriga"], (8, 12, 17, 9))

    # rabo
    pygame.draw.polygon(s, c["corpo_escuro"], [(0, 9), (5, 11), (0, 15)])

    # olho
    pygame.draw.circle(s, c["contorno"], (22, 10), 4)
    pygame.draw.circle(s, c["olho"], (22, 10), 3)
    pygame.draw.rect(s, c["pupila"], (23, 9, 2, 3))

    # bico
    pygame.draw.polygon(s, c["contorno"], [(26, 12), (33, 14), (26, 17)])
    pygame.draw.polygon(s, c["bico"], [(27, 13), (32, 14), (27, 16)])

    # asa
    formatos = {
        "cima": [(6, 12), (12, 3), (16, 12)],
        "meio": [(5, 13), (16, 11), (14, 16)],
        "baixo": [(6, 13), (16, 13), (10, 21)],
    }
    pygame.draw.polygon(s, c["asa"], formatos[posicao_asa])
    return s


# ----------------------------------------------------------------------------
# Coluna 52x320 (o jogo vira de cabeça pra baixo para o obstáculo de cima)
# ----------------------------------------------------------------------------
def desenhar_coluna():
    s = nova_superficie(52, 320)
    c = PALETA

    def corpo(x, y, largura, altura):
        pygame.draw.rect(s, c["coluna"], (x, y, largura, altura))
        pygame.draw.rect(s, c["coluna_claro"], (x + 4, y, 6, altura))
        pygame.draw.rect(s, c["coluna_escuro"], (x + largura - 8, y, 5, altura))
        pygame.draw.rect(s, c["contorno"], (x, y, largura, altura), 2)

    # tronco
    corpo(4, 20, 44, 300)
    # faixas laranjas com parafusos a cada 60px
    for y in range(50, 320, 60):
        pygame.draw.rect(s, c["faixa"], (6, y, 40, 5))
        for x in (10, 26, 40):
            pygame.draw.circle(s, c["parafuso"], (x, y + 2), 1)
    # topo mais largo (a "boca" da coluna)
    corpo(0, 0, 52, 22)
    pygame.draw.rect(s, c["faixa"], (2, 16, 48, 3))
    for x in (7, 26, 45):
        pygame.draw.circle(s, c["parafuso"], (x, 8), 2)
    return s


# ----------------------------------------------------------------------------
# Fundo 288x512
# ----------------------------------------------------------------------------
def misturar(cor_a, cor_b, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(cor_a, cor_b))


def desenhar_fundo():
    s = nova_superficie(288, 512)
    c = PALETA
    horizonte = 360

    # céu em degradê (topo -> meio -> baixo)
    for y in range(512):
        if y < horizonte * 0.55:
            cor = misturar(c["ceu_topo"], c["ceu_meio"], y / (horizonte * 0.55))
        else:
            t = min(1.0, (y - horizonte * 0.55) / (horizonte * 0.45))
            cor = misturar(c["ceu_meio"], c["ceu_baixo"], t)
        pygame.draw.line(s, cor, (0, y), (287, y))

    # estrelas só na parte escura
    aleatorio = random.Random(7)  # semente fixa: sempre as mesmas estrelas
    for _ in range(40):
        x, y = aleatorio.randrange(288), aleatorio.randrange(150)
        s.set_at((x, y), c["estrela"])

    # sol com anéis
    for raio, alfa in ((46, 40), (38, 80), (30, 255)):
        halo = nova_superficie(100, 100)
        pygame.draw.circle(halo, (*c["sol"], alfa), (50, 50), raio)
        s.blit(halo, (150, horizonte - 95))

    # morros (duas camadas de ondas)
    def morros(cor, base, amplitude, frequencia, fase):
        pontos = [(0, 512)]
        for x in range(0, 289, 4):
            y = base - amplitude * (0.6 + 0.4 * math.sin(x * frequencia + fase)) \
                - amplitude * 0.3 * math.sin(x * frequencia * 2.7 + fase)
            pontos.append((x, y))
        pontos.append((288, 512))
        pygame.draw.polygon(s, cor, pontos)

    morros(c["morro_longe"], horizonte, 50, 0.025, 1.0)
    morros(c["morro_perto"], horizonte + 30, 35, 0.04, 3.0)
    return s


# ----------------------------------------------------------------------------
# Chão 336x112 (tem que emendar nas bordas porque o jogo repete ele)
# ----------------------------------------------------------------------------
def desenhar_chao():
    s = nova_superficie(336, 112)
    c = PALETA
    s.fill(c["terra"])

    # camadas de terra
    for y in range(30, 112, 18):
        pygame.draw.line(s, c["terra_escura"], (0, y), (335, y), 2)

    # pedrinhas repetindo a cada 24px (336 é múltiplo de 24, então emenda)
    for x in range(0, 336, 24):
        pygame.draw.ellipse(s, c["pedra"], (x + 5, 40, 8, 5))
        pygame.draw.ellipse(s, c["pedra"], (x + 15, 70, 6, 4))

    # grama com pontas, também repetindo a cada 12px
    pygame.draw.rect(s, c["grama"], (0, 0, 336, 14))
    for x in range(0, 336, 12):
        pygame.draw.polygon(s, c["grama_escura"], [(x, 14), (x + 6, 22), (x + 12, 14)])
        pygame.draw.line(s, c["grama_escura"], (x + 3, 2), (x + 5, 8), 2)
    pygame.draw.line(s, c["contorno"], (0, 0), (335, 0), 2)
    return s


def main():
    pygame.init()
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    imagens = {
        "passaro_1.png": desenhar_passaro("cima"),
        "passaro_2.png": desenhar_passaro("meio"),
        "passaro_3.png": desenhar_passaro("baixo"),
        "coluna.png": desenhar_coluna(),
        "fundo.png": desenhar_fundo(),
        "chao.png": desenhar_chao(),
    }
    for nome, superficie in imagens.items():
        caminho = os.path.join(PASTA_SAIDA, nome)
        pygame.image.save(superficie, caminho)
        print(f"gerada: {caminho} {superficie.get_size()}")
    pygame.quit()


if __name__ == "__main__":
    main()
